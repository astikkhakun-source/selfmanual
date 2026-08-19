import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from src.domain.scoring.scales import score_item
from src.services.config_loader import CORE_BASE_ITEMS, CORE_ADAPTIVE_POOL

# Map signal to question IDs for base 24 CORE questions
SIGNAL_ITEMS = {
    "CS_RECOGNITION": [("Q018", "D"), ("Q019", "R")],
    "CS_AVOIDANCE": [("Q028", "D"), ("Q029", "R")],
    "CS_ATTACH_ANXIETY": [("Q043", "D"), ("Q045", "R")],
    "CS_ATTACH_AVOIDANCE": [("Q047", "D"), ("Q049", "R")],
    "CS_AGENCY": [("Q076", "R"), ("Q077", "D")],
    "CS_UNCERTAINTY": [("Q085", "D"), ("Q087", "R")],
    "CS_ACTION": [("Q104", "D"), ("Q105", "R")],
    "CS_FEAR_EVALUATION": [("Q112", "R"), ("Q113", "D")],
    "CS_AUTHENTICITY": [("Q114", "D"), ("Q116", "R")],
    "CS_PERFORMANCE_WORTH": [("Q128", "D"), ("Q129", "R")],
    "CS_STABLE_WORTH": [("Q131", "D"), ("Q133", "R")],
    "CS_NEED_AWARENESS": [("Q138", "D"), ("Q139", "R")],
}


def calculate_signal_confidence(scored_answers: List[int]) -> float:
    """Calculate confidence based on item gap between answers."""
    if len(scored_answers) < 2:
        return 0.50
    
    gap = abs(scored_answers[0] - scored_answers[1])
    if len(scored_answers) == 2:
        if gap <= 1:
            return 0.80  # CONSISTENT
        elif gap == 2:
            return 0.70  # ACCEPTABLE
        elif gap == 3:
            return 0.55  # UNCERTAIN
        else:
            return 0.35  # CONTRADICTORY

    # 3 or more items (after adaptive questions)
    std_dev = statistics.stdev(scored_answers)
    if std_dev <= 1.0:
        return 0.90  # Elevated confidence
    else:
        return min(0.60, 0.35 + (3.0 - std_dev) * 0.15)


def calculate_core_signals(answers_by_qid: Dict[str, int]) -> Dict[str, Any]:
    """Calculate 12 CORE signals (0..100) and confidence values."""
    signals = {}
    
    for signal_name, items in SIGNAL_ITEMS.items():
        scored = []
        for q_id, direction in items:
            if q_id in answers_by_qid:
                scored.append(score_item(answers_by_qid[q_id], direction))

        # Check for adaptive items answered for this signal
        adaptive_qids = CORE_ADAPTIVE_POOL.get(signal_name, [])
        for q_id in adaptive_qids:
            if q_id in answers_by_qid:
                # Need to determine item direction (look up default 'D' unless known 'R')
                direction = "R" if q_id in ("Q019", "Q029", "Q045", "Q049", "Q076", "Q087", "Q105", "Q112", "Q116", "Q129", "Q133", "Q139") else "D"
                scored.append(score_item(answers_by_qid[q_id], direction))

        if scored:
            raw_mean = statistics.mean(scored)
            signal_val = round(((raw_mean - 1.0) / 6.0) * 100.0, 2)
            confidence = calculate_signal_confidence(scored)
            signals[signal_name] = {
                "signal": signal_name,
                "score": signal_val,
                "confidence": confidence,
                "scored_items_count": len(scored)
            }
            
    return signals


def select_next_adaptive_question(
    answers_by_qid: Dict[str, int],
    adaptive_history: List[str]
) -> Optional[str]:
    """
    Select the next adaptive question (max 6) based on uncertainty_need and priority.
    Stop Rule: if max questions (30 total = 24 base + 6 adaptive) reached or no contradictory signal needing resolution.
    """
    if len(adaptive_history) >= 6:
        return None

    signals = calculate_core_signals(answers_by_qid)
    
    # Priority score map for signals needing resolution
    candidates = []
    
    for signal_name, sig_data in signals.items():
        conf = sig_data["confidence"]
        if conf >= 0.75:
            continue  # Signal already confident enough

        # Check unused pool items
        pool_qids = CORE_ADAPTIVE_POOL.get(signal_name, [])
        unused = [q for q in pool_qids if q not in answers_by_qid and q not in adaptive_history]
        
        if not unused:
            continue

        # Priority calculation
        uncertainty_need = 100 if conf <= 0.35 else (70 if conf <= 0.55 else 25)
        priority = 0.35 * uncertainty_need + 0.65 * (100.0 - conf * 100.0)
        
        candidates.append((priority, unused[0]))

    if not candidates:
        return None

    # Sort descending by priority
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def evaluate_core_conflicts(signals: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str], str]:
    """
    Evaluate CORE conflicts CF01..CF08 per Section 17.
    Returns (conflicts_dict, top_conflict_id, report_mode).
    """
    def sig(name: str) -> float:
        return signals.get(name, {}).get("score", 0.0)

    def conf(name: str) -> float:
        return signals.get(name, {}).get("confidence", 0.50)

    def inv(x: float) -> float:
        return 100.0 - x

    conflicts = {}

    # CF01: freedom_without_guarantees
    agency = sig("CS_AGENCY")
    uncert = sig("CS_UNCERTAINTY")
    score_cf01 = (agency * inv(uncert) / 100.0) if agency >= 55 else 0.0
    conf_cf01 = math.sqrt(conf("CS_AGENCY") * conf("CS_UNCERTAINTY"))
    conflicts["CF01"] = {
        "id": "CF01",
        "name": "freedom_without_guarantees",
        "headline": "ТЫ ХОЧЕШЬ СВОБОДЫ, НО ХОЧЕШЬ ГАРАНТИЙ.",
        "score": round(score_cf01, 2),
        "confidence": round(conf_cf01, 2)
    }

    # CF02: know_but_do_not_act
    need_aw = sig("CS_NEED_AWARENESS")
    action = sig("CS_ACTION")
    avoid = sig("CS_AVOIDANCE")
    score_cf02 = need_aw * (0.55 * inv(action) + 0.45 * avoid) / 100.0
    conf_cf02 = (conf("CS_NEED_AWARENESS") * conf("CS_ACTION") * conf("CS_AVOIDANCE")) ** (1/3)
    conflicts["CF02"] = {
        "id": "CF02",
        "name": "know_but_do_not_act",
        "headline": "ТЫ ЗНАЕШЬ, ЧЕГО ХОЧЕШЬ. НО ЭТО ЕЩЁ НЕ ЗНАЧИТ, ЧТО ТЫ ЭТО ВЫБЕРЕШЬ.",
        "score": round(score_cf02, 2),
        "confidence": round(conf_cf02, 2)
    }

    # CF03: closeness_dependency
    anx = sig("CS_ATTACH_ANXIETY")
    att_avoid = sig("CS_ATTACH_AVOIDANCE")
    score_cf03 = anx * att_avoid / 100.0
    conf_cf03 = math.sqrt(conf("CS_ATTACH_ANXIETY") * conf("CS_ATTACH_AVOIDANCE"))
    conflicts["CF03"] = {
        "id": "CF03",
        "name": "closeness_dependency",
        "headline": "ТЫ ХОЧЕШЬ БЛИЗОСТИ, НО НЕ ХОЧЕШЬ ЗАВИСЕТЬ.",
        "score": round(score_cf03, 2),
        "confidence": round(conf_cf03, 2)
    }

    # CF04: authentic_but_costly
    fear_eval = sig("CS_FEAR_EVALUATION")
    auth = sig("CS_AUTHENTICITY")
    score_cf04 = fear_eval * auth / 100.0
    conf_cf04 = math.sqrt(conf("CS_FEAR_EVALUATION") * conf("CS_AUTHENTICITY"))
    conflicts["CF04"] = {
        "id": "CF04",
        "name": "authentic_but_costly",
        "headline": "ТЫ ОСТАЁШЬСЯ СОБОЙ. НО ИНОГДА ЭТО СЛИШКОМ ДОРОГО.",
        "score": round(score_cf04, 2),
        "confidence": round(conf_cf04, 2)
    }

    # CF05: self_editing
    score_cf05 = fear_eval * inv(auth) / 100.0
    conf_cf05 = math.sqrt(conf("CS_FEAR_EVALUATION") * conf("CS_AUTHENTICITY"))
    conflicts["CF05"] = {
        "id": "CF05",
        "name": "self_editing",
        "headline": "ТЫ РЕДАКТИРУЕШЬ СЕБЯ ЕЩЁ ДО ТОГО, КАК ЭТО СДЕЛАЮТ ДРУГИЕ.",
        "score": round(score_cf05, 2),
        "confidence": round(conf_cf05, 2)
    }

    # CF06: prove_worth
    perf_worth = sig("CS_PERFORMANCE_WORTH")
    stable_worth = sig("CS_STABLE_WORTH")
    score_cf06 = perf_worth * inv(stable_worth) / 100.0
    conf_cf06 = math.sqrt(conf("CS_PERFORMANCE_WORTH") * conf("CS_STABLE_WORTH"))
    conflicts["CF06"] = {
        "id": "CF06",
        "name": "prove_worth",
        "headline": "ТЕБЕ НЕДОСТАТОЧНО БЫТЬ. ТЕБЕ НУЖНО ДОКАЗЫВАТЬ, ЧТО ТЫ ЧЕГО-ТО СТОИШЬ.",
        "score": round(score_cf06, 2),
        "confidence": round(conf_cf06, 2)
    }

    # CF07: need_confirmation
    recog = sig("CS_RECOGNITION")
    score_cf07 = recog * inv(stable_worth) / 100.0
    conf_cf07 = math.sqrt(conf("CS_RECOGNITION") * conf("CS_STABLE_WORTH"))
    conflicts["CF07"] = {
        "id": "CF07",
        "name": "need_confirmation",
        "headline": "ТЕБЕ ЛЕГЧЕ ВЕРИТЬ В СЕБЯ, КОГДА В ТЕБЯ ВЕРЯТ ДРУГИЕ.",
        "score": round(score_cf07, 2),
        "confidence": round(conf_cf07, 2)
    }

    # CF08: know_need_avoid_price
    score_cf08 = need_aw * avoid / 100.0
    conf_cf08 = math.sqrt(conf("CS_NEED_AWARENESS") * conf("CS_AVOIDANCE"))
    conflicts["CF08"] = {
        "id": "CF08",
        "name": "know_need_avoid_price",
        "headline": "ТЫ ЗНАЕШЬ, ЧЕГО ХОЧЕШЬ. ТЫ ПРОСТО НЕ ВСЕГДА ГОТОВ ПЛАТИТЬ ЦЕНУ.",
        "score": round(score_cf08, 2),
        "confidence": round(conf_cf08, 2)
    }

    # Determine priority and top conflict
    sorted_conflicts = sorted(
        conflicts.items(),
        key=lambda x: (0.50 * x[1]["score"] + 0.30 * x[1]["confidence"] * 100.0),
        reverse=True
    )
    
    top_id, top_data = sorted_conflicts[0]
    
    if top_data["score"] < 50.0 or top_data["confidence"] < 0.60:
        return conflicts, None, "CONFIGURATION_ONLY"
    else:
        return conflicts, top_id, "CONFLICT"
