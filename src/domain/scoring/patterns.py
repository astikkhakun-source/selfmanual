from typing import Dict, List, Any, Optional


def evaluate_full_patterns(
    scales: Dict[str, Any],
    context: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluate 37 full patterns from calculated 46 primary scale scores (0..100).
    Applies strict suppression rules and counter-evidence tagging.
    """
    ctx = context or {}

    def s(name: str) -> float:
        return scales.get(name, {}).get("normalized", 50.0)

    def inv(x: float) -> float:
        return 100.0 - x

    raw_patterns = []

    # P01 achievement_contingent_self_worth
    score_p01 = .45 * s("performance_based_self_worth") + .25 * s("achievement_drive") + .20 * s("inner_critic") + .10 * inv(s("stable_self_worth"))
    raw_patterns.append({
        "id": "P01", "name": "achievement_contingent_self_worth", "cluster": "SELF_WORTH",
        "score": round(score_p01, 2), "type": "PATTERN", "weight_type": "CORE_MECHANISM"
    })

    # P02 externalized_self_validation
    score_p02 = .50 * s("recognition_based_self_regulation") + .25 * s("reassurance_seeking") + .25 * inv(s("stable_self_worth"))
    raw_patterns.append({
        "id": "P02", "name": "externalized_self_validation", "cluster": "SELF_WORTH",
        "score": round(score_p02, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P03 harsh_internal_regulation
    if s("inner_critic") >= 55:
        score_p03 = .50 * s("inner_critic") + .25 * s("error_intolerance") + .25 * s("conscientiousness")
    else:
        score_p03 = 0.0
    raw_patterns.append({
        "id": "P03", "name": "harsh_internal_regulation", "cluster": "SELF_WORTH",
        "score": round(score_p03, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P04 stable_self_regard RESOURCE
    score_p04 = .55 * s("stable_self_worth") + .25 * inv(s("performance_based_self_worth")) + .20 * inv(s("recognition_based_self_regulation"))
    raw_patterns.append({
        "id": "P04", "name": "stable_self_regard", "cluster": "SELF_WORTH",
        "score": round(score_p04, 2), "type": "RESOURCE", "weight_type": "RESOURCE"
    })

    # P05 experiential_avoidance_loop
    score_p05 = .55 * s("experiential_avoidance") + .20 * s("negative_emotionality") + .15 * inv(s("emotional_awareness")) + .10 * inv(s("adaptive_flexibility"))
    raw_patterns.append({
        "id": "P05", "name": "experiential_avoidance_loop", "cluster": "EMOTIONAL_REGULATION",
        "score": round(score_p05, 2), "type": "PATTERN", "weight_type": "CORE_MECHANISM"
    })

    # P06 intellectualized_emotion (Suppression: awareness >= 70 AND avoidance <= 35)
    if s("emotional_awareness") >= 70 and s("experiential_avoidance") <= 35:
        score_p06 = 0.0
        status_p06 = "SUPPRESSED"
    else:
        score_p06 = s("intellectualization") * (.40 * s("experiential_avoidance") + .30 * s("emotional_suppression") + .30 * inv(s("emotional_awareness"))) / 100.0
        status_p06 = "ACTIVE"
    raw_patterns.append({
        "id": "P06", "name": "intellectualized_emotion", "cluster": "EMOTIONAL_REGULATION",
        "score": round(score_p06, 2), "type": "PATTERN", "status": status_p06, "weight_type": "IMPORTANT"
    })

    # P07 emotional_concealment
    score_p07 = .45 * s("emotional_suppression") + .35 * s("vulnerability_avoidance") + .20 * s("fear_of_evaluation")
    raw_patterns.append({
        "id": "P07", "name": "emotional_concealment", "cluster": "EMOTIONAL_REGULATION",
        "score": round(score_p07, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P08 emotionally_informed_regulation RESOURCE
    score_p08 = .45 * s("emotional_awareness") + .30 * inv(s("experiential_avoidance")) + .25 * s("adaptive_flexibility")
    raw_patterns.append({
        "id": "P08", "name": "emotionally_informed_regulation", "cluster": "EMOTIONAL_REGULATION",
        "score": round(score_p08, 2), "type": "RESOURCE", "weight_type": "RESOURCE"
    })

    # P09 attachment_hyperactivation
    rel_uncert_ctx = ctx.get("relational_uncertainty", 50.0)
    score_p09 = .50 * s("attachment_anxiety") + .25 * s("reassurance_seeking") + .15 * rel_uncert_ctx + .10 * s("negative_emotionality")
    raw_patterns.append({
        "id": "P09", "name": "attachment_hyperactivation", "cluster": "RELATIONSHIPS",
        "score": round(score_p09, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P10 defensive_independence
    score_p10 = s("autonomy_value") * (.45 * s("attachment_avoidance") + .30 * s("vulnerability_avoidance") + .25 * s("detachment_tendency")) / 100.0
    raw_patterns.append({
        "id": "P10", "name": "defensive_independence", "cluster": "RELATIONSHIPS",
        "score": round(score_p10, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P11 approach_avoidance_closeness
    score_p11 = s("attachment_anxiety") * s("attachment_avoidance") / 100.0
    raw_patterns.append({
        "id": "P11", "name": "approach_avoidance_closeness", "cluster": "RELATIONSHIPS",
        "score": round(score_p11, 2), "type": "PATTERN", "weight_type": "CORE_MECHANISM"
    })

    # P12 self_loss_through_accommodation (Suppression: boundary_assertiveness >= 70)
    if s("boundary_assertiveness") >= 70:
        score_p12 = 0.0
        status_p12 = "SUPPRESSED"
    else:
        side_a = .40 * s("belonging_value") + .30 * s("attachment_anxiety") + .30 * s("interpersonal_accommodation")
        side_b = .55 * inv(s("boundary_assertiveness")) + .45 * inv(s("authentic_expression"))
        score_p12 = side_a * side_b / 100.0
        status_p12 = "ACTIVE"
    raw_patterns.append({
        "id": "P12", "name": "self_loss_through_accommodation", "cluster": "RELATIONSHIPS",
        "score": round(score_p12, 2), "type": "PATTERN", "status": status_p12, "weight_type": "IMPORTANT"
    })

    # P13 secure_relational_capacity RESOURCE
    score_p13 = .30 * s("interpersonal_trust") + .25 * s("boundary_assertiveness") + .20 * inv(s("attachment_anxiety")) + .15 * inv(s("attachment_avoidance")) + .10 * inv(s("vulnerability_avoidance"))
    raw_patterns.append({
        "id": "P13", "name": "secure_relational_capacity", "cluster": "RELATIONSHIPS",
        "score": round(score_p13, 2), "type": "RESOURCE", "weight_type": "RESOURCE"
    })

    # P14 need_disconnection
    score_p14 = .50 * inv(s("need_awareness")) + .25 * s("interpersonal_accommodation") + .25 * inv(s("boundary_assertiveness"))
    raw_patterns.append({
        "id": "P14", "name": "need_disconnection", "cluster": "NEEDS_BOUNDARIES",
        "score": round(score_p14, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P15 needs_to_action_gap
    score_p15 = s("need_awareness") * (.35 * inv(s("action_initiation")) + .25 * s("fear_of_evaluation") + .20 * s("experiential_avoidance") + .20 * inv(s("boundary_assertiveness"))) / 100.0
    raw_patterns.append({
        "id": "P15", "name": "needs_to_action_gap", "cluster": "NEEDS_BOUNDARIES",
        "score": round(score_p15, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P16 learned_powerlessness_configuration (Suppression: agency >= 70)
    if s("agency") >= 70:
        score_p16 = 0.0
        status_p16 = "SUPPRESSED"
    else:
        score_p16 = .35 * inv(s("agency")) + .30 * inv(s("self_efficacy")) + .20 * s("external_outcome_attribution") + .15 * inv(s("action_initiation"))
        status_p16 = "ACTIVE"
    raw_patterns.append({
        "id": "P16", "name": "learned_powerlessness_configuration", "cluster": "AGENCY_ACTION",
        "score": round(score_p16, 2), "type": "PATTERN", "status": status_p16, "weight_type": "CORE_MECHANISM"
    })

    # P17 agency_without_confidence
    score_p17 = s("agency") * inv(s("self_efficacy")) / 100.0
    raw_patterns.append({
        "id": "P17", "name": "agency_without_confidence", "cluster": "AGENCY_ACTION",
        "score": round(score_p17, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P18 confidence_without_action
    score_p18 = s("self_efficacy") * inv(s("action_initiation")) / 100.0
    raw_patterns.append({
        "id": "P18", "name": "confidence_without_action", "cluster": "AGENCY_ACTION",
        "score": round(score_p18, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P19 certainty_before_action
    score_p19 = .40 * inv(s("uncertainty_tolerance")) + .30 * s("control_need") + .30 * s("error_intolerance")
    raw_patterns.append({
        "id": "P19", "name": "certainty_before_action", "cluster": "AGENCY_ACTION",
        "score": round(score_p19, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P20 action_without_adaptation
    score_p20 = s("action_initiation") * inv(s("adaptive_flexibility")) / 100.0
    raw_patterns.append({
        "id": "P20", "name": "action_without_adaptation", "cluster": "AGENCY_ACTION",
        "score": round(score_p20, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P21 adaptive_agency RESOURCE
    score_p21 = .35 * s("agency") + .25 * s("action_initiation") + .25 * s("adaptive_flexibility") + .15 * s("self_efficacy")
    raw_patterns.append({
        "id": "P21", "name": "adaptive_agency", "cluster": "AGENCY_ACTION",
        "score": round(score_p21, 2), "type": "RESOURCE", "weight_type": "RESOURCE"
    })

    # P22 analysis_paralysis
    score_p22 = .40 * inv(s("decisiveness")) + .30 * s("decision_rumination") + .20 * s("error_intolerance") + .10 * inv(s("uncertainty_tolerance"))
    raw_patterns.append({
        "id": "P22", "name": "analysis_paralysis", "cluster": "DECISIONS",
        "score": round(score_p22, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P23 outsourced_certainty
    score_p23 = .45 * s("reassurance_seeking") + .25 * inv(s("stable_self_worth")) + .20 * s("fear_of_evaluation") + .10 * inv(s("self_efficacy"))
    raw_patterns.append({
        "id": "P23", "name": "outsourced_certainty", "cluster": "DECISIONS",
        "score": round(score_p23, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P24 post_decision_instability
    score_p24 = .55 * s("decision_rumination") + .25 * s("error_intolerance") + .20 * s("reassurance_seeking")
    raw_patterns.append({
        "id": "P24", "name": "post_decision_instability", "cluster": "DECISIONS",
        "score": round(score_p24, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P25 visibility_conflict (Suppression: visibility_desire < 40)
    if s("visibility_desire") < 40:
        score_p25 = 0.0
        status_p25 = "SUPPRESSED"
    else:
        score_p25 = s("visibility_desire") * (.50 * s("fear_of_evaluation") + .30 * inv(s("authentic_expression")) + .20 * s("vulnerability_avoidance")) / 100.0
        status_p25 = "ACTIVE"
    raw_patterns.append({
        "id": "P25", "name": "visibility_conflict", "cluster": "VISIBILITY_EVALUATION",
        "score": round(score_p25, 2), "type": "PATTERN", "status": status_p25, "weight_type": "CORE_MECHANISM"
    })

    # P26 self_editing_for_acceptance
    score_p26 = .45 * inv(s("authentic_expression")) + .30 * s("fear_of_evaluation") + .25 * s("recognition_based_self_regulation")
    raw_patterns.append({
        "id": "P26", "name": "self_editing_for_acceptance", "cluster": "VISIBILITY_EVALUATION",
        "score": round(score_p26, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P27 visible_but_vulnerable
    score_p27 = s("visibility_desire") * s("fear_of_evaluation") * s("authentic_expression") / 10000.0
    raw_patterns.append({
        "id": "P27", "name": "visible_but_vulnerable", "cluster": "VISIBILITY_EVALUATION",
        "score": round(score_p27, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P28 low_visibility_by_preference NORMALIZING
    score_p28 = inv(s("visibility_desire")) * inv(s("fear_of_evaluation")) / 100.0
    raw_patterns.append({
        "id": "P28", "name": "low_visibility_by_preference", "cluster": "VISIBILITY_EVALUATION",
        "score": round(score_p28, 2), "type": "NORMALIZING", "weight_type": "NORMALIZING"
    })

    # P29 healthy_achievement_orientation RESOURCE (downgrade if perf worth high & stable worth low)
    score_p29 = .40 * s("achievement_drive") + .25 * s("achievement_value") + .20 * s("stable_self_worth") + .15 * s("adaptive_flexibility")
    if s("performance_based_self_worth") >= 65 and s("stable_self_worth") <= 35:
        score_p29 *= 0.50
    raw_patterns.append({
        "id": "P29", "name": "healthy_achievement_orientation", "cluster": "ACHIEVEMENT",
        "score": round(score_p29, 2), "type": "RESOURCE", "weight_type": "RESOURCE"
    })

    # P30 achievement_pressure (downgrade if stable_self_worth >= 75 AND inner_critic <= 40)
    score_p30 = .35 * s("achievement_drive") + .30 * s("performance_based_self_worth") + .20 * s("inner_critic") + .15 * s("error_intolerance")
    if s("stable_self_worth") >= 75 and s("inner_critic") <= 40:
        score_p30 *= 0.50
    raw_patterns.append({
        "id": "P30", "name": "achievement_pressure", "cluster": "ACHIEVEMENT",
        "score": round(score_p30, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P31 perfectionistic_evaluation
    score_p31 = .30 * s("error_intolerance") + .25 * s("polarized_evaluation") + .20 * s("inner_critic") + .15 * s("rigid_control_tendency") + .10 * s("fear_of_evaluation")
    raw_patterns.append({
        "id": "P31", "name": "perfectionistic_evaluation", "cluster": "ACHIEVEMENT",
        "score": round(score_p31, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P32 money_as_safety_regulator
    score_p32 = .60 * s("money_security") + .20 * s("security_value") + .20 * s("control_need")
    raw_patterns.append({
        "id": "P32", "name": "money_as_safety_regulator", "cluster": "MONEY",
        "score": round(score_p32, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P33 money_as_autonomy_regulator
    score_p33 = .55 * s("money_autonomy") + .25 * s("autonomy_value") + .20 * s("agency")
    raw_patterns.append({
        "id": "P33", "name": "money_as_autonomy_regulator", "cluster": "MONEY",
        "score": round(score_p33, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P34 financial_success_identity (Suppression: money_status_achievement < 40)
    if s("money_status_achievement") < 40:
        score_p34 = 0.0
        status_p34 = "SUPPRESSED"
    else:
        score_p34 = .50 * s("money_status_achievement") + .25 * s("achievement_value") + .15 * s("recognition_based_self_regulation") + .10 * s("performance_based_self_worth")
        status_p34 = "ACTIVE"
    raw_patterns.append({
        "id": "P34", "name": "financial_success_identity", "cluster": "MONEY",
        "score": round(score_p34, 2), "type": "PATTERN", "status": status_p34, "weight_type": "IMPORTANT"
    })

    # P35 meaning_gap
    curr_meaning = ctx.get("current_meaning", 50.0)
    score_p35 = s("meaning_value") * inv(curr_meaning) / 100.0
    raw_patterns.append({
        "id": "P35", "name": "meaning_gap", "cluster": "VALUES_MEANING",
        "score": round(score_p35, 2), "type": "PATTERN", "weight_type": "IMPORTANT"
    })

    # P36 growth_stability_tension
    score_p36 = s("growth_value") * s("security_value") / 100.0
    raw_patterns.append({
        "id": "P36", "name": "growth_stability_tension", "cluster": "VALUES_MEANING",
        "score": round(score_p36, 2), "type": "PATTERN", "weight_type": "CONTEXTUAL"
    })

    # P37 autonomy_belonging_tension
    score_p37 = s("autonomy_value") * s("belonging_value") / 100.0
    raw_patterns.append({
        "id": "P37", "name": "autonomy_belonging_tension", "cluster": "VALUES_MEANING",
        "score": round(score_p37, 2), "type": "PATTERN", "weight_type": "CONTEXTUAL"
    })

    return raw_patterns
