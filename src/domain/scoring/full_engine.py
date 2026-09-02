import json
import os
import math
from typing import Dict, List, Any, Optional
from collections import defaultdict

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
CONFLICTS_DICT = _load_json("conflicts.json")

def calculate_full_profile(answers_by_qid: Dict[str, int]) -> Dict[str, Any]:
    """
    Scoring Engine SelfCode-160 v1.0:
    Processes raw user answers (1-7 Likert scale)
    - Maps primary constructs
    - Maps secondary evidence (with weights and directions)
    - Cluster-aware confidence calculation (SCORE vs GENERALIZATION)
    """
    
    # Structure: dimension_code -> list of (norm_score, weight, cluster_id, context)
    dim_evidence: Dict[str, List[tuple]] = defaultdict(list)
    
    for q_id, ans in answers_by_qid.items():
        if q_id not in QUESTIONS_DICT:
            continue
            
        q_info = QUESTIONS_DICT[q_id]
        primary_scale = q_info.get("legacy_scale_id", "")
        primary_dir = q_info.get("direction", "D")
        cluster_id = q_info.get("auto_evidence_cluster_id", "UNKNOWN")
        
        if not (isinstance(ans, int) and 1 <= ans <= 7):
            ans = 4 # Neutral default if invalid
            
        # 1. Primary Mapping (Weight 1.0)
        if primary_dir == "D":
            primary_norm = ((ans - 1) / 6.0) * 100.0
        else:
            primary_norm = ((7 - ans) / 6.0) * 100.0
            
        if primary_scale:
            # We map it to the exact dimension code if it matches, otherwise we store it by its scale_id.
            # In dimensions.json, code is usually the same as scale_id or name.
            dim_evidence[primary_scale.lower()].append((primary_norm, 1.0, cluster_id, "GENERAL"))
            
        # 2. Secondary Mappings (Variable weight)
        for sec in q_info.get("secondary_mappings", []):
            dim = sec.get("dimension", "").lower()
            w = sec.get("weight", 0.0)
            d = sec.get("direction", 1)
            ctx = sec.get("context", "GENERAL")
            
            if d == 1 or d == "D":
                sec_norm = ((ans - 1) / 6.0) * 100.0
            else:
                sec_norm = ((7 - ans) / 6.0) * 100.0
                
            dim_evidence[dim].append((sec_norm, w, cluster_id, ctx))
            
    # Process all 46 dimensions
    dimensions_result = {}
    for code, dim_def in DIMENSIONS_DICT.items():
        dim_id = dim_def["id"]
        
        scores = dim_evidence.get(code.lower(), [])
        if not scores:
            scores = dim_evidence.get(dim_def["name_en"].lower().replace(" ", "_"), [])
            
        if scores:
            total_w = sum(s[1] for s in scores)
            weighted_sum = sum(s[0] * s[1] for s in scores)
            mean_score = weighted_sum / total_w if total_w > 0 else 50.0
            
            clusters = set(s[2] for s in scores if s[2] and s[2] != "UNKNOWN")
            c_count = len(clusters)
            q_count = len(scores)
            
            # Score Confidence (Reliability based on volume)
            if q_count >= 5: score_conf = "HIGH"
            elif q_count >= 3: score_conf = "MEDIUM"
            else: score_conf = "LOW"
            
            # Generalization Confidence (Based on independent clusters)
            if c_count >= 3: gen_conf = "HIGH"
            elif c_count == 2: gen_conf = "MEDIUM"
            else: gen_conf = "LOW"
            
            # Backwards compatibility numeric confidence
            numeric_conf = min(1.0, q_count / float(dim_def.get("minimum_evidence", {}).get("high_confidence", 4)))
            
        else:
            mean_score = 50.0
            score_conf = "NONE"
            gen_conf = "NONE"
            numeric_conf = 0.0
            c_count = 0
            q_count = 0
            
        low_pole_active = mean_score <= 40.0
        high_pole_active = mean_score >= 60.0

        dimensions_result[code] = {
            "id": dim_id,
            "code": code,
            "name_ru": dim_def.get("name_ru", ""),
            "score": round(mean_score, 1),
            "confidence": round(numeric_conf, 2),
            "score_confidence": score_conf,
            "generalization_confidence": gen_conf,
            "evidence_stats": {
                "raw_questions": q_count,
                "independent_clusters": c_count
            },
            "low_pole_active": low_pole_active,
            "high_pole_active": high_pole_active,
            "anchors": dim_def.get("scoring_anchors", {}),
            "interpretation_rules": dim_def.get("interpretation_rules", [])
        }

    def is_dim_active(dim_code: str) -> bool:
        dim_res = dimensions_result.get(dim_code, {})
        return dim_res.get("low_pole_active", False) or dim_res.get("high_pole_active", False)

    # Evaluate 37 Patterns
    active_patterns = []
    for item in PATTERNS_DICT:
        req_dims = item.get("required_dimensions", [])
        if req_dims and all(is_dim_active(d) for d in req_dims):
            active_patterns.append({
                "id": item["id"],
                "name_ru": item.get("name_ru", item.get("name", "")),
                "name_en": item.get("name_en", ""),
                "definition": item.get("definition", item.get("description", "")),
                "short_term_function": item.get("short_term_function", ""),
                "long_term_cost": item.get("long_term_cost", "")
            })

    # Evaluate 12 Conflicts
    active_conflicts = []
    for item in CONFLICTS_DICT:
        req_dims = item.get("required_dimensions", [])
        if req_dims and all(is_dim_active(d) for d in req_dims):
            active_conflicts.append({
                "id": item["id"],
                "code": item.get("code", item["id"]),
                "name_ru": item.get("name_ru", item.get("name", "")),
                "name_en": item.get("name_en", ""),
                "definition": item.get("definition", item.get("description", "")),
                "short_term_function": item.get("short_term_function", ""),
                "long_term_cost": item.get("long_term_cost", "")
            })

    return {
        "dimensions": dimensions_result,
        "active_patterns": active_patterns,
        "active_conflicts": active_conflicts,
        "total_answered": len(answers_by_qid)
    }
