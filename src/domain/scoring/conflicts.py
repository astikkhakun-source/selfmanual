from typing import Dict, List, Any, Optional


def evaluate_full_conflicts(
    scales: Dict[str, Any],
    context: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluate 12 full psychological conflicts from 46 primary scale scores (0..100).
    """
    ctx = context or {}

    def s(name: str) -> float:
        return scales.get(name, {}).get("normalized", 50.0)

    def inv(x: float) -> float:
        return 100.0 - x

    conflicts = []

    # C01 visibility_vs_evaluation
    score_c01 = s("visibility_desire") * s("fear_of_evaluation") / 100.0
    conflicts.append({"id": "C01", "name": "visibility_vs_evaluation", "score": round(score_c01, 2)})

    # C02 authenticity_vs_acceptance
    side_a = .60 * s("autonomy_value") + .40 * s("authentic_expression")
    side_b = .55 * s("recognition_based_self_regulation") + .45 * s("fear_of_evaluation")
    score_c02 = side_a * side_b / 100.0
    conflicts.append({"id": "C02", "name": "authenticity_vs_acceptance", "score": round(score_c02, 2)})

    # C03 closeness_vs_dependency
    side_a = .55 * s("belonging_value") + .45 * s("attachment_anxiety")
    side_b = .60 * s("attachment_avoidance") + .40 * s("vulnerability_avoidance")
    score_c03 = side_a * side_b / 100.0
    conflicts.append({"id": "C03", "name": "closeness_vs_dependency", "score": round(score_c03, 2)})

    # C04 belonging_vs_boundaries
    side_a = .60 * s("belonging_value") + .40 * s("interpersonal_accommodation")
    score_c04 = side_a * inv(s("boundary_assertiveness")) / 100.0
    conflicts.append({"id": "C04", "name": "belonging_vs_boundaries", "score": round(score_c04, 2)})

    # C05 achievement_vs_failure
    side_a = .50 * s("achievement_value") + .50 * s("achievement_drive")
    side_b = .55 * s("error_intolerance") + .45 * s("performance_based_self_worth")
    score_c05 = side_a * side_b / 100.0
    conflicts.append({"id": "C05", "name": "achievement_vs_failure", "score": round(score_c05, 2)})

    # C06 action_vs_certainty
    side_a = .45 * s("agency") + .30 * s("action_initiation") + .25 * s("achievement_drive")
    side_b = .50 * inv(s("uncertainty_tolerance")) + .30 * s("control_need") + .20 * s("error_intolerance")
    score_c06 = side_a * side_b / 100.0
    conflicts.append({"id": "C06", "name": "action_vs_certainty", "score": round(score_c06, 2)})

    # C07 choice_vs_error
    side_a = .50 * s("decisiveness") + .30 * s("agency") + .20 * s("autonomy_value")
    score_c07 = side_a * s("error_intolerance") / 100.0
    conflicts.append({"id": "C07", "name": "choice_vs_error", "score": round(score_c07, 2)})

    # C08 need_vs_expression
    side_b = .55 * inv(s("boundary_assertiveness")) + .45 * inv(s("authentic_expression"))
    score_c08 = s("need_awareness") * side_b / 100.0
    conflicts.append({"id": "C08", "name": "need_vs_expression", "score": round(score_c08, 2)})

    # C09 growth_vs_security
    score_c09 = s("growth_value") * s("security_value") / 100.0
    conflicts.append({"id": "C09", "name": "growth_vs_security", "score": round(score_c09, 2)})

    # C10 autonomy_vs_belonging
    score_c10 = s("autonomy_value") * s("belonging_value") / 100.0
    conflicts.append({"id": "C10", "name": "autonomy_vs_belonging", "score": round(score_c10, 2)})

    # C11 money_freedom_vs_money_safety
    score_c11 = s("money_autonomy") * s("money_security") / 100.0
    conflicts.append({"id": "C11", "name": "money_freedom_vs_money_safety", "score": round(score_c11, 2)})

    # C12 meaning_vs_current_life
    curr_meaning = ctx.get("current_meaning", 50.0)
    score_c12 = s("meaning_value") * inv(curr_meaning) / 100.0
    conflicts.append({"id": "C12", "name": "meaning_vs_current_life", "score": round(score_c12, 2)})

    return conflicts
