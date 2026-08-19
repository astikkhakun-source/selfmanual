import statistics
from typing import Dict, List, Any, Optional
from src.services.config_loader import PRIMARY_SCALES_MAP


def score_item(raw_answer: int, direction: str) -> int:
    """
    Score a single 1..7 Likert item.
    Direct ('D'): scored_answer = raw_answer
    Reverse ('R'): scored_answer = 8 - raw_answer
    """
    if direction == "R":
        return 8 - raw_answer
    return raw_answer


def calculate_primary_scales(answers_by_qid: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate 46 primary trait scales from full raw answers dictionary.
    Returns scale scores dictionary containing raw_mean, normalized (0..100), rank, and relative delta.
    """
    scales_raw = {}
    
    for scale_id, items in PRIMARY_SCALES_MAP.items():
        scored_answers = []
        for q_id, direction in items:
            if q_id in answers_by_qid:
                scored_answers.append(score_item(answers_by_qid[q_id], direction))
        
        # Primary scale is computed ONLY if all items present
        if len(scored_answers) == len(items):
            raw_mean = statistics.mean(scored_answers)
            normalized = ((raw_mean - 1) / 6.0) * 100.0
            scales_raw[scale_id] = {
                "raw_mean": round(raw_mean, 4),
                "normalized": round(normalized, 2),
                "total_items": len(items)
            }

    if not scales_raw:
        return {}

    # Calculate profile median across computed normalized scores
    normalized_values = [v["normalized"] for v in scales_raw.values()]
    profile_median = statistics.median(normalized_values)

    # Sort scales by normalized score descending to derive profile ranks
    sorted_scales = sorted(scales_raw.items(), key=lambda x: x[1]["normalized"], reverse=True)
    
    result = {}
    for rank, (scale_id, data) in enumerate(sorted_scales, start=1):
        normalized = data["normalized"]
        delta = round(normalized - profile_median, 2)
        result[scale_id] = {
            "scale_id": scale_id,
            "raw_mean": data["raw_mean"],
            "normalized": normalized,
            "profile_rank": rank,
            "relative_delta": delta,
            "profile_median": round(profile_median, 2),
            "confidence": 1.0
        }

    return result
