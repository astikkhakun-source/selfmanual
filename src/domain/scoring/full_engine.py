import json
import os
import math
from typing import Dict, List, Any, Optional

DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")

def _load_json(filename: str) -> Any:
    filepath = os.path.join(DICT_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

DIMENSIONS_DICT = {d["code"]: d for d in _load_json("dimensions.json")}
QUESTIONS_DICT = {q["question_id"]: q for q in _load_json("questions.json")}
PATTERNS_DICT = _load_json("patterns.json")

def calculate_full_profile(answers_by_qid: Dict[str, int]) -> Dict[str, Any]:
    """
    Scoring Engine FULL-175:
    Processes raw user answers (1-7 Likert scale or VFC forced choice)
    and returns a structured analytical profile object with:
    - 46 dimension scores (0-100) and confidence levels
    - Active systemic patterns and conflicts
    """
    scale_raw_scores: Dict[str, List[float]] = {}
    
    # Map questions to dimensions
    for q_id, ans in answers_by_qid.items():
        if q_id not in QUESTIONS_DICT:
            continue
        
        q_info = QUESTIONS_DICT[q_id]
        scale_code = q_info.get("legacy_scale_id", "")
        direction = q_info.get("direction", "D")
        
        # Likert 1-7 normalization to 0-100
        # If ans is 1-7
        if isinstance(ans, int) and 1 <= ans <= 7:
            if direction == "D":
                norm_score = ((ans - 1) / 6.0) * 100.0
            else:
                norm_score = ((7 - ans) / 6.0) * 100.0
        else:
            norm_score = 50.0
            
        if scale_code not in scale_raw_scores:
            scale_raw_scores[scale_code] = []
        scale_raw_scores[scale_code].append(norm_score)

    # Process all 46 dimensions
    dimensions_result = {}
    for code, dim_def in DIMENSIONS_DICT.items():
        dim_id = dim_def["id"]
        # Find matching scores in raw_scores (by lower code or id)
        scores = scale_raw_scores.get(code.lower(), [])
        if not scores:
            scores = scale_raw_scores.get(dim_def["name_en"].lower().replace(" ", "_"), [])
            
        if scores:
            mean_score = sum(scores) / len(scores)
            items_count = len(scores)
            confidence = min(1.0, items_count / float(dim_def.get("minimum_evidence", {}).get("high_confidence", 4)))
        else:
            mean_score = 50.0
            confidence = 0.0

        low_pole_active = mean_score <= 40.0
        high_pole_active = mean_score >= 60.0

        dimensions_result[code] = {
            "id": dim_id,
            "code": code,
            "name_ru": dim_def.get("name_ru", ""),
            "score": round(mean_score, 1),
            "confidence": round(confidence, 2),
            "low_pole_active": low_pole_active,
            "high_pole_active": high_pole_active,
            "anchors": dim_def.get("scoring_anchors", {}),
            "interpretation_rules": dim_def.get("interpretation_rules", [])
        }

    # Evaluate Patterns & Conflicts
    active_patterns = []
    active_conflicts = []

    for item in PATTERNS_DICT:
        conditions = item.get("trigger_conditions", [])
        triggered = True
        
        for cond in conditions:
            target_dim = cond.get("dimension")
            op = cond.get("operator")
            target_val = cond.get("value", 50)
            
            dim_res = dimensions_result.get(target_dim, {})
            current_score = dim_res.get("score", 50.0)
            
            if op == "<=" and not (current_score <= target_val):
                triggered = False
                break
            elif op == ">=" and not (current_score >= target_val):
                triggered = False
                break
            elif op == "==" and not (current_score == target_val):
                triggered = False
                break

        if triggered:
            res_obj = {
                "id": item["id"],
                "code": item["code"],
                "name": item["name"],
                "description": item["description"],
                "interpretation": item["interpretation"]
            }
            if item.get("type") == "PATTERN":
                active_patterns.append(res_obj)
            else:
                active_conflicts.append(res_obj)

    return {
        "dimensions": dimensions_result,
        "active_patterns": active_patterns,
        "active_conflicts": active_conflicts,
        "total_answered": len(answers_by_qid)
    }
