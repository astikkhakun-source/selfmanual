import json
import os
from typing import Dict, List, Any, Optional

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")

# CORE Base items C01..C24 mapping to master Question IDs and target signals
CORE_BASE_ITEMS = [
    {"core_id": "C01", "question_id": "Q018", "signal": "CS_RECOGNITION", "direction": "D"},
    {"core_id": "C02", "question_id": "Q019", "signal": "CS_RECOGNITION", "direction": "R"},
    {"core_id": "C03", "question_id": "Q028", "signal": "CS_AVOIDANCE", "direction": "D"},
    {"core_id": "C04", "question_id": "Q029", "signal": "CS_AVOIDANCE", "direction": "R"},
    {"core_id": "C05", "question_id": "Q043", "signal": "CS_ATTACH_ANXIETY", "direction": "D"},
    {"core_id": "C06", "question_id": "Q045", "signal": "CS_ATTACH_ANXIETY", "direction": "R"},
    {"core_id": "C07", "question_id": "Q047", "signal": "CS_ATTACH_AVOIDANCE", "direction": "D"},
    {"core_id": "C08", "question_id": "Q049", "signal": "CS_ATTACH_AVOIDANCE", "direction": "R"},
    {"core_id": "C09", "question_id": "Q076", "signal": "CS_AGENCY", "direction": "R"},
    {"core_id": "C10", "question_id": "Q077", "signal": "CS_AGENCY", "direction": "D"},
    {"core_id": "C11", "question_id": "Q085", "signal": "CS_UNCERTAINTY", "direction": "D"},
    {"core_id": "C12", "question_id": "Q087", "signal": "CS_UNCERTAINTY", "direction": "R"},
    {"core_id": "C13", "question_id": "Q104", "signal": "CS_ACTION", "direction": "D"},
    {"core_id": "C14", "question_id": "Q105", "signal": "CS_ACTION", "direction": "R"},
    {"core_id": "C15", "question_id": "Q112", "signal": "CS_FEAR_EVALUATION", "direction": "R"},
    {"core_id": "C16", "question_id": "Q113", "signal": "CS_FEAR_EVALUATION", "direction": "D"},
    {"core_id": "C17", "question_id": "Q114", "signal": "CS_AUTHENTICITY", "direction": "D"},
    {"core_id": "C18", "question_id": "Q116", "signal": "CS_AUTHENTICITY", "direction": "R"},
    {"core_id": "C19", "question_id": "Q128", "signal": "CS_PERFORMANCE_WORTH", "direction": "D"},
    {"core_id": "C20", "question_id": "Q129", "signal": "CS_PERFORMANCE_WORTH", "direction": "R"},
    {"core_id": "C21", "question_id": "Q131", "signal": "CS_STABLE_WORTH", "direction": "D"},
    {"core_id": "C22", "question_id": "Q133", "signal": "CS_STABLE_WORTH", "direction": "R"},
    {"core_id": "C23", "question_id": "Q138", "signal": "CS_NEED_AWARENESS", "direction": "D"},
    {"core_id": "C24", "question_id": "Q139", "signal": "CS_NEED_AWARENESS", "direction": "R"},
]

# Adaptive candidate items mapping per CORE signal
CORE_ADAPTIVE_POOL = {
    "CS_RECOGNITION": ["Q017", "Q020"],
    "CS_AVOIDANCE": ["Q027", "Q030"],
    "CS_ATTACH_ANXIETY": ["Q044", "Q046"],
    "CS_ATTACH_AVOIDANCE": ["Q048", "Q050"],
    "CS_AGENCY": ["Q075", "Q078"],
    "CS_UNCERTAINTY": ["Q086", "Q088"],
    "CS_ACTION": ["Q106"],
    "CS_FEAR_EVALUATION": ["Q110", "Q111"],
    "CS_AUTHENTICITY": ["Q115", "Q117"],
    "CS_PERFORMANCE_WORTH": ["Q127", "Q130"],
    "CS_STABLE_WORTH": ["Q132"],
    "CS_NEED_AWARENESS": ["Q137"],
}

# 46 primary scale -> item mapping with direction
PRIMARY_SCALES_MAP = {
    "cognitive_openness": [("Q001", "D"), ("Q002", "D"), ("Q003", "D")],
    "conscientiousness": [("Q004", "D"), ("Q005", "D"), ("Q006", "R")],
    "extraversion": [("Q007", "D"), ("Q008", "D"), ("Q009", "D")],
    "interpersonal_accommodation": [("Q010", "D"), ("Q011", "D"), ("Q012", "R")],
    "negative_emotionality": [("Q013", "D"), ("Q014", "D"), ("Q015", "R"), ("Q016", "D")],
    "recognition_based_self_regulation": [("Q017", "D"), ("Q018", "D"), ("Q019", "R"), ("Q020", "D")],
    "detachment_tendency": [("Q021", "D"), ("Q022", "D"), ("Q023", "R")],
    "rigid_control_tendency": [("Q024", "D"), ("Q025", "D"), ("Q026", "R")],
    "experiential_avoidance": [("Q027", "D"), ("Q028", "D"), ("Q029", "R"), ("Q030", "D")],
    "intellectualization": [("Q031", "D"), ("Q032", "D"), ("Q033", "R")],
    "emotional_suppression": [("Q034", "D"), ("Q035", "D"), ("Q036", "R")],
    "polarized_evaluation": [("Q037", "D"), ("Q038", "R"), ("Q039", "D")],
    "emotional_awareness": [("Q040", "D"), ("Q041", "D"), ("Q042", "R")],
    "attachment_anxiety": [("Q043", "D"), ("Q044", "D"), ("Q045", "R"), ("Q046", "D")],
    "attachment_avoidance": [("Q047", "D"), ("Q048", "D"), ("Q049", "R"), ("Q050", "D")],
    "interpersonal_trust": [("Q051", "D"), ("Q052", "D"), ("Q053", "R")],
    "boundary_assertiveness": [("Q054", "D"), ("Q055", "R"), ("Q056", "D")],
    "autonomy_value": [("Q057", "D"), ("Q058", "D"), ("Q059", "R")],
    "security_value": [("Q060", "D"), ("Q061", "D"), ("Q062", "R")],
    "achievement_value": [("Q063", "D"), ("Q064", "D"), ("Q065", "R")],
    "belonging_value": [("Q066", "D"), ("Q067", "D"), ("Q068", "R")],
    "meaning_value": [("Q069", "D"), ("Q070", "D"), ("Q071", "D")],
    "growth_value": [("Q072", "D"), ("Q073", "D"), ("Q074", "D")],
    "agency": [("Q075", "D"), ("Q076", "R"), ("Q077", "D"), ("Q078", "D")],
    "self_efficacy": [("Q079", "D"), ("Q080", "R"), ("Q081", "D")],
    "external_outcome_attribution": [("Q082", "D"), ("Q083", "D"), ("Q084", "R")],
    "uncertainty_tolerance": [("Q085", "D"), ("Q086", "D"), ("Q087", "R"), ("Q088", "D")],
    "control_need": [("Q089", "D"), ("Q090", "D"), ("Q091", "R")],
    "decisiveness": [("Q092", "D"), ("Q093", "R"), ("Q094", "D")],
    "decision_rumination": [("Q095", "D"), ("Q096", "D"), ("Q097", "R")],
    "reassurance_seeking": [("Q098", "D"), ("Q099", "D"), ("Q100", "R")],
    "error_intolerance": [("Q101", "D"), ("Q102", "D"), ("Q103", "R")],
    "action_initiation": [("Q104", "D"), ("Q105", "R"), ("Q106", "D")],
    "adaptive_flexibility": [("Q107", "D"), ("Q108", "R"), ("Q109", "D")],
    "fear_of_evaluation": [("Q110", "D"), ("Q111", "D"), ("Q112", "R"), ("Q113", "D")],
    "authentic_expression": [("Q114", "D"), ("Q115", "D"), ("Q116", "R"), ("Q117", "D")],
    "visibility_desire": [("Q118", "D"), ("Q119", "D"), ("Q120", "R")],
    "inner_critic": [("Q121", "D"), ("Q122", "D"), ("Q123", "R")],
    "vulnerability_avoidance": [("Q124", "D"), ("Q125", "D"), ("Q126", "R")],
    "performance_based_self_worth": [("Q127", "D"), ("Q128", "D"), ("Q129", "R"), ("Q130", "D")],
    "stable_self_worth": [("Q131", "D"), ("Q132", "D"), ("Q133", "R")],
    "achievement_drive": [("Q134", "D"), ("Q135", "D"), ("Q136", "R")],
    "need_awareness": [("Q137", "D"), ("Q138", "D"), ("Q139", "R")],
    "money_security": [("Q140", "D"), ("Q141", "D"), ("Q142", "R")],
    "money_autonomy": [("Q143", "D"), ("Q144", "D"), ("Q145", "R")],
    "money_status_achievement": [("Q146", "D"), ("Q147", "D"), ("Q148", "R")],
}

# 15 Forced-Choice Value pairs (VFC01..VFC15)
VFC_PAIRS = [
    {
        "vfc_id": "VFC01",
        "value_a": "autonomy",
        "text_a": "иметь больше свободы самостоятельно определять свою жизнь, даже ценой меньшей предсказуемости.",
        "value_b": "security",
        "text_b": "иметь больше устойчивости и предсказуемости, даже ценой части свободы выбора."
    },
    {
        "vfc_id": "VFC02",
        "value_a": "achievement",
        "text_a": "получить возможность добиться значительно большего результата.",
        "value_b": "autonomy",
        "text_b": "сохранить больше свободы распоряжаться собой и своим временем."
    },
    {
        "vfc_id": "VFC03",
        "value_a": "autonomy",
        "text_a": "иметь возможность жить преимущественно на собственных условиях.",
        "value_b": "belonging",
        "text_b": "сохранять тесную связь и чувство принадлежности к важным людям."
    },
    {
        "vfc_id": "VFC04",
        "value_a": "meaning",
        "text_a": "заниматься тем, что ощущается глубоко осмысленным.",
        "value_b": "autonomy",
        "text_b": "иметь максимальную свободу самостоятельно выбирать направление жизни."
    },
    {
        "vfc_id": "VFC05",
        "value_a": "autonomy",
        "text_a": "сохранить свободу выбирать собственный путь.",
        "value_b": "growth",
        "text_b": "выбрать путь, который сильнее развивает меня, даже если он ограничивает часть свободы."
    },
    {
        "vfc_id": "VFC06",
        "value_a": "security",
        "text_a": "сохранить надёжный и устойчивый уровень жизни.",
        "value_b": "achievement",
        "text_b": "рискнуть частью устойчивости ради возможности добиться значительно большего."
    },
    {
        "vfc_id": "VFC07",
        "value_a": "belonging",
        "text_a": "сохранить близость и принадлежность к важным людям.",
        "value_b": "security",
        "text_b": "выбрать более устойчивый и безопасный для себя вариант."
    },
    {
        "vfc_id": "VFC08",
        "value_a": "security",
        "text_a": "сохранить предсказуемость и устойчивость жизни.",
        "value_b": "meaning",
        "text_b": "выбрать менее предсказуемый путь, который ощущается значительно более осмысленным."
    },
    {
        "vfc_id": "VFC09",
        "value_a": "growth",
        "text_a": "выбрать путь, который сильнее меня развивает.",
        "value_b": "security",
        "text_b": "сохранить больше устойчивости и предсказуемости."
    },
    {
        "vfc_id": "VFC10",
        "value_a": "achievement",
        "text_a": "использовать возможность значительного достижения, даже если отношениям временно достанется меньше моего времени.",
        "value_b": "belonging",
        "text_b": "сохранить больше времени и включённости в важные отношения, даже ценой части возможностей."
    },
    {
        "vfc_id": "VFC11",
        "value_a": "meaning",
        "text_a": "заниматься более осмысленным для себя делом, даже если результат будет скромнее.",
        "value_b": "achievement",
        "text_b": "выбрать возможность значительно большего результата, даже если сама деятельность ощущается менее значимой."
    },
    {
        "vfc_id": "VFC12",
        "value_a": "achievement",
        "text_a": "получить более заметный внешний результат.",
        "value_b": "growth",
        "text_b": "получить опыт, который сильнее меня развивает, даже если внешний результат будет скромнее."
    },
    {
        "vfc_id": "VFC13",
        "value_a": "belonging",
        "text_a": "сохранить тесную связь с важными людьми.",
        "value_b": "meaning",
        "text_b": "следовать лично значимому направлению, даже если это создаст большую дистанцию."
    },
    {
        "vfc_id": "VFC14",
        "value_a": "growth",
        "text_a": "выбрать опыт, который существенно меня развивает.",
        "value_b": "belonging",
        "text_b": "сохранить привычную близость и включённость в отношения."
    },
    {
        "vfc_id": "VFC15",
        "value_a": "meaning",
        "text_a": "выбрать путь, который ощущается более осмысленным уже сейчас.",
        "value_b": "growth",
        "text_b": "выбрать путь, который сильнее меня изменит и разовьёт."
    }
]

# Canonical display order for DEEP phase trait questions
DEEP_TRAIT_ORDER = [
    "Q001", "Q007", "Q004", "Q057", "Q003", "Q009", "Q064", "Q005", "Q072", "Q011",
    "Q079", "Q066", "Q017", "Q043", "Q002", "Q082", "Q006", "Q110", "Q008", "Q024",
    "Q010", "Q127", "Q138", "Q051", "Q137", "Q085", "Q117", "Q134", "Q012", "Q040",
    "Q089", "Q114", "Q060", "Q021", "Q098", "Q140", "Q139", "Q013", "Q047", "Q075",
    "Q121", "Q069", "Q031", "Q092", "Q143", "Q054", "Q118", "Q027", "Q102", "Q131",
    "Q073", "Q034", "Q081", "Q018", "Q044", "Q083", "Q111", "Q025", "Q128", "Q052",
    "Q086", "Q135", "Q041", "Q090", "Q115", "Q061", "Q022", "Q099", "Q141", "Q014",
    "Q048", "Q076", "Q122", "Q070", "Q032", "Q093", "Q144", "Q055", "Q119", "Q028",
    "Q103", "Q132", "Q074", "Q035", "Q080", "Q019", "Q045", "Q084", "Q112", "Q026",
    "Q129", "Q053", "Q087", "Q136", "Q042", "Q091", "Q116", "Q062", "Q023", "Q100",
    "Q142", "Q015", "Q049", "Q077", "Q123", "Q071", "Q033", "Q094", "Q145", "Q056",
    "Q120", "Q029", "Q101", "Q133", "Q037", "Q036", "Q088", "Q020", "Q046", "Q107",
    "Q113", "Q038", "Q130", "Q058", "Q095", "Q146", "Q104", "Q030", "Q108", "Q063",
    "Q096", "Q109", "Q039", "Q016", "Q050", "Q078", "Q124", "Q059", "Q097", "Q147",
    "Q105", "Q065", "Q125", "Q068", "Q106", "Q148", "Q126", "Q067"
]

DEEP_STATE_CONTEXT_ORDER = [
    "Q149", "Q152", "Q150", "Q153", "Q151", "Q154",
    "Q155", "Q157", "Q156", "Q158", "Q159", "Q160"
]

VFC_ORDER = [
    "VFC08", "VFC02", "VFC13", "VFC06", "VFC15", "VFC03", "VFC12", "VFC07",
    "VFC04", "VFC10", "VFC01", "VFC14", "VFC11", "VFC05", "VFC09"
]
