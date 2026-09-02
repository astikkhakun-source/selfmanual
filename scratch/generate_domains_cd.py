import json
import os

new_dimensions = [
    # DOMAIN C - UNCERTAINTY / CONTROL
    {
        "id": "D14",
        "code": "D14_UNCERTAINTY_TOLERANCE",
        "domain": "DOMAIN_C_UNCERTAINTY",
        "name_en": "Uncertainty Tolerance",
        "name_ru": "Толерантность к неопределенности",
        "definition": "Способность выдерживать отсутствие ясности, контроля и гарантий результата без чрезмерного разрушительного стресса.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Острое неприятие неизвестности. Неопределенность воспринимается как угроза, требующая немедленного устранения.",
            "resource": "Стремление структурировать хаос. Создание надежных процессов, систем безопасности и резервных планов.",
            "cost": "Хроническая тревога, отказ от выгодных, но непредсказуемых возможностей (например, новая профессия или смена страны)."
        },
        "high_pole": {
            "description": "Неизвестность воспринимается как естественная часть жизни или даже как пространство возможностей.",
            "resource": "Способность действовать в хаосе, комфорт в инновациях и стартапах, снижение тревожности.",
            "cost": "Может приводить к беспечности, отсутствию базовой страховки и игнорированию реальных рисков ('авось пронесет')."
        },
        "scoring_anchors": {
            "0_20": "Крайняя непереносимость. Любая неизвестность парализует или вызывает панику.",
            "21_40": "Сильный дискомфорт. Требуется много энергии, чтобы не сбежать из непонятной ситуации.",
            "41_60": "Средняя переносимость. Может выдержать локальную неопределенность, если базовая безопасность сохранена.",
            "61_80": "Хорошая толерантность. Неизвестность не пугает, а скорее мобилизует.",
            "81_100": "Абсолютный комфорт в хаосе. Структура и предсказуемость даже могут вызывать скуку."
        },
        "direct_evidence_tags": ["reaction_to_unknown", "ambiguity_stress", "need_for_guarantees"],
        "indirect_evidence_tags": ["control_freak", "job_security_preference"],
        "negative_evidence_tags": ["thriving_in_chaos", "boredom_in_routine"],
        "exclusion_tags": ["actual_life_threat"],
        "relevant_contexts": ["UNCERTAINTY", "WORK", "MONEY"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P3_CERTAINTY_BEFORE_ACTION", "P2_CONTROL_ANALYSIS_LOOP"],
        "related_conflicts": ["C2_FREEDOM_VS_SECURITY"],
        "related_dimensions": ["D15_CONTROL_RELIANCE", "D18_RISK_TOLERANCE"],
        "interpretation_rules": [
            "IF D14_LOW AND D15_CONTROL_RELIANCE_HIGH THEN note that control is the primary coping mechanism for uncertainty."
        ],
        "exclusion_rules": [
            "Do not score low tolerance if the uncertainty is related to basic survival (e.g., losing a home)."
        ]
    },
    {
        "id": "D15",
        "code": "D15_CONTROL_RELIANCE",
        "domain": "DOMAIN_C_UNCERTAINTY",
        "name_en": "Control Reliance",
        "name_ru": "Опора на контроль",
        "definition": "Склонность использовать микроменеджмент, гиперпланирование и сбор информации как главный способ снижения тревоги.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Минимальная потребность контролировать процесс. Готовность плыть по течению или делегировать.",
            "resource": "Экономия энергии, гибкость, доверие к другим.",
            "cost": "Может переходить в безответственность, попустительство и потерю управления в критических ситуациях."
        },
        "high_pole": {
            "description": "Попытка удержать все нити управления в своих руках. 'Если не я, то все рухнет'.",
            "resource": "Высокое качество операционной работы, минимизация сюрпризов, надежность.",
            "cost": "Тотальное истощение, невозможность делегировать, удушение инициативы других."
        },
        "scoring_anchors": {
            "0_20": "Абсолютное попустительство. Отказ от планирования.",
            "21_40": "Контролирует только критические узлы, остальное отпускает.",
            "41_60": "Баланс. Контроль в зоне своей ответственности, доверие в зоне чужой.",
            "61_80": "Повышенный контроль. Трудно расслабиться, если процесс идет без прямого участия.",
            "81_100": "Тотальный гиперконтроль. Физическая невозможность передать задачу без микроменеджмента."
        },
        "direct_evidence_tags": ["micromanagement", "delegation_difficulty", "planning_obsession"],
        "indirect_evidence_tags": ["exhaustion_from_management"],
        "negative_evidence_tags": ["easy_delegation", "letting_go"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "RELATIONSHIPS"],
        "context_modifiers": {
            "RELATIONSHIPS": "May manifest as attempting to control a partner's feelings or behavior to prevent abandonment."
        },
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P2_CONTROL_ANALYSIS_LOOP"],
        "related_conflicts": ["C5_CONTROL_VS_SPONTANEITY"],
        "related_dimensions": ["D14_UNCERTAINTY_TOLERANCE"],
        "interpretation_rules": [
            "IF D15_HIGH AND context==RELATIONSHIPS THEN explore if control is a defense against rejection."
        ],
        "exclusion_rules": [
            "Do not score high control reliance if the user is objectively a project manager responsible for extreme details, unless it spills over into personal life."
        ]
    },
    {
        "id": "D16",
        "code": "D16_PREDICTABILITY_NEED",
        "domain": "DOMAIN_C_UNCERTAINTY",
        "name_en": "Predictability Need",
        "name_ru": "Потребность в предсказуемости",
        "definition": "Степень важности наличия ясного, пошагового плана и понимания 'что будет дальше' для начала и продолжения действия.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Скука от рутины. Предпочтение спонтанности и импровизации.",
            "resource": "Генерация новых идей, способность перестраиваться на лету, креативность.",
            "cost": "Трудности с системной работой, саботаж долгосрочных структур."
        },
        "high_pole": {
            "description": "Необходимость четких правил, регламентов и понимания финала. Действие блокируется, если план не ясен.",
            "resource": "Последовательность, умение выстраивать прочные процессы.",
            "cost": "Отказ от начинаний, где пошаговый план невозможен в принципе."
        },
        "scoring_anchors": {
            "0_20": "Хронический бунт против любых планов и структур.",
            "21_40": "Предпочтение открытого финала. Структура используется только как черновик.",
            "41_60": "Нуждается в 'скелете' плана, но легко отступает от него.",
            "61_80": "Сильный дискомфорт без понятных правил игры. Нужен прогноз.",
            "81_100": "Жесткое требование гарантий будущего. Шаг не делается без ясного понимания последствий."
        },
        "direct_evidence_tags": ["need_for_plan", "routine_preference", "spontaneity_resistance"],
        "indirect_evidence_tags": ["anxiety_without_schedule"],
        "negative_evidence_tags": ["improvisation", "boredom_in_routine"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "MONEY"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P3_CERTAINTY_BEFORE_ACTION"],
        "related_conflicts": ["C5_CONTROL_VS_SPONTANEITY"],
        "related_dimensions": ["D14_UNCERTAINTY_TOLERANCE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D17",
        "code": "D17_AMBIGUITY_TOLERANCE",
        "domain": "DOMAIN_C_UNCERTAINTY",
        "name_en": "Ambiguity Tolerance",
        "name_ru": "Толерантность к двусмысленности",
        "definition": "Способность выдерживать противоречивую информацию, амбивалентные чувства и ситуации без черно-белых ответов.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Черно-белое мышление. Потребность быстро разложить все по полочкам: 'кто прав, а кто виноват'.",
            "resource": "Быстрое принятие однозначных решений, сильная поляризация (полезно в конкуренции).",
            "cost": "Неспособность видеть нюансы, разрушение отношений из-за жестких ярлыков."
        },
        "high_pole": {
            "description": "Способность удерживать в голове взаимоисключающие вещи (например, 'он хороший человек, но поступил ужасно').",
            "resource": "Глубокая эмпатия, мудрость, системное мышление, разрешение сложных конфликтов.",
            "cost": "Риск застревания в амбивалентности: 'с одной стороны... но с другой...', приводящее к бездействию."
        },
        "scoring_anchors": {
            "0_20": "Категоричность. Либо идеализация, либо полное обесценивание.",
            "21_40": "Склонность к быстрым упрощениям сложной картины мира.",
            "41_60": "Видит нюансы, но в состоянии стресса скатывается в черно-белое мышление.",
            "61_80": "Способен долго удерживать противоречия, не делая поспешных выводов.",
            "81_100": "Мастерство парадоксального мышления. Полное отсутствие категоричности."
        },
        "direct_evidence_tags": ["black_and_white_thinking", "nuance_tolerance", "cognitive_complexity"],
        "indirect_evidence_tags": ["idealization_devaluation_cycles"],
        "negative_evidence_tags": ["rigid_judgments", "quick_labeling"],
        "exclusion_tags": [],
        "relevant_contexts": ["CONFLICT", "RELATIONSHIPS"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D21_EMOTIONAL_DIFFERENTIATION"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D18",
        "code": "D18_RISK_TOLERANCE",
        "domain": "DOMAIN_C_UNCERTAINTY",
        "name_en": "Risk Tolerance",
        "name_ru": "Толерантность к риску",
        "definition": "Степень готовности принимать решения, которые могут привести к значимым потерям (финансовым, статусным, отношенческим).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Стратегия минимизации потерь. Выбор синицы в руках.",
            "resource": "Сбережение ресурсов, защита от катастроф, накопление.",
            "cost": "Упущенные кратные потенциалы роста, стагнация."
        },
        "high_pole": {
            "description": "Стратегия максимизации выигрыша. Готовность ставить на кон значимые ресурсы ради журавля в небе.",
            "resource": "Шанс на нелинейный прорыв, захват новых территорий.",
            "cost": "Риск разрушения системы, банкротство, потеря репутации."
        },
        "scoring_anchors": {
            "0_20": "Абсолютное избегание любых рисков. Полный консерватизм.",
            "21_40": "Выбирает риск только если есть 100% подушка безопасности.",
            "41_60": "Взвешенный риск. Готов рискнуть тем, что не жалко потерять.",
            "61_80": "Высокий аппетит к риску. Любит крупные ставки.",
            "81_100": "Склонность к авантюризму. Игнорирование стоп-лоссов."
        },
        "direct_evidence_tags": ["risk_appetite", "loss_aversion", "bold_decisions"],
        "indirect_evidence_tags": ["financial_behavior"],
        "negative_evidence_tags": ["playing_it_safe", "over_insuring"],
        "exclusion_tags": [],
        "relevant_contexts": ["MONEY", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": [],
        "related_conflicts": ["C2_FREEDOM_VS_SECURITY"],
        "related_dimensions": ["D14_UNCERTAINTY_TOLERANCE"],
        "interpretation_rules": [
            "IF D18_HIGH AND D15_CONTROL_RELIANCE_HIGH THEN interpret as 'calculated bold moves', not blind gambling."
        ],
        "exclusion_rules": []
    },
    {
        "id": "D19",
        "code": "D19_COGNITIVE_OVERPROCESSING",
        "domain": "DOMAIN_C_UNCERTAINTY",
        "name_en": "Cognitive Overprocessing",
        "name_ru": "Избыточная когнитивная обработка (Румминация)",
        "definition": "Склонность застревать в мысленных жвачках, бесконечно прокручивать сценарии прошлого или будущего вместо действия.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Мгновенное переключение. Мысли направлены только на текущую задачу.",
            "resource": "Огромная экономия ментальной энергии, присутствие 'здесь и сейчас'.",
            "cost": "Может не хватать глубины анализа и рефлексии сложных ситуаций."
        },
        "high_pole": {
            "description": "Постоянный фоновый процесс анализа: 'А что если...', 'А почему он так сказал...'.",
            "resource": "Сверхдетальная проработка контекста, замечание мельчайших нюансов.",
            "cost": "Утечка энергии. Истощение до начала реального действия. Тревога генерируется самими мыслями."
        },
        "scoring_anchors": {
            "0_20": "Голова свободна от фоновых мыслей. Полное присутствие в реальности.",
            "21_40": "Редкие эпизоды анализа, которые быстро завершаются.",
            "41_60": "В стрессе может 'погонять мысли', но в целом умеет останавливать этот процесс.",
            "61_80": "Заметная румминация. Требуются специальные усилия, чтобы отключить голову.",
            "81_100": "Хроническая мысленная жвачка. Невозможность уснуть из-за прокручивания сценариев."
        },
        "direct_evidence_tags": ["rumination", "overthinking", "inability_to_turn_off_mind"],
        "indirect_evidence_tags": ["anxiety_generation", "insomnia"],
        "negative_evidence_tags": ["empty_mind", "easy_switching"],
        "exclusion_tags": ["OCD_markers"],
        "relevant_contexts": ["STRESS", "RELATIONSHIPS"],
        "context_modifiers": {},
        "state_sensitivity": "HIGH",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P2_CONTROL_ANALYSIS_LOOP"],
        "related_conflicts": [],
        "related_dimensions": ["D09_DECISIVENESS", "D15_CONTROL_RELIANCE"],
        "interpretation_rules": [
            "IF D19_HIGH THEN note that thinking has become a substitute for feeling or doing."
        ],
        "exclusion_rules": []
    },

    # DOMAIN D - EMOTIONAL FUNCTIONING
    {
        "id": "D20",
        "code": "D20_EMOTIONAL_AWARENESS",
        "domain": "DOMAIN_D_EMOTIONS",
        "name_en": "Emotional Awareness",
        "name_ru": "Эмоциональная осознанность",
        "definition": "Способность замечать возникновение эмоции в реальном времени и называть ее.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Алекситимия. Эмоции замечаются только на уровне сильных физиологических реакций (заболела голова, сорвался на крик).",
            "resource": "Позволяет функционировать в крайне травматичных или высокострессовых условиях (как машина).",
            "cost": "Психосоматика. Решения принимаются под влиянием скрытых аффектов. Отсутствие 'компаса'."
        },
        "high_pole": {
            "description": "Ясное понимание: 'сейчас я злюсь', 'сейчас мне страшно', до того, как это перешло в действие.",
            "resource": "Возможность выбора реакции. Глубокий контакт с собой.",
            "cost": "Может приводить к избыточному фокусу на своем состоянии ('я не в ресурсе'), парализующему действие."
        },
        "scoring_anchors": {
            "0_20": "Полная слепота к своим чувствам. 'Я не злюсь, просто вы все идиоты'.",
            "21_40": "Замечает только крайне сильные эмоции (ярость, паника). Фоновый фон не распознается.",
            "41_60": "Осознает эмоции постфактум ('вчера я был зол').",
            "61_80": "Хороший контакт. Распознает состояние в процессе.",
            "81_100": "Филигранная чувствительность к малейшим изменениям внутреннего состояния."
        },
        "direct_evidence_tags": ["alexithymia", "feeling_recognition", "somatic_markers"],
        "indirect_evidence_tags": ["emotional_vocabulary"],
        "negative_evidence_tags": ["body_disconnect", "logical_overdrive"],
        "exclusion_tags": [],
        "relevant_contexts": ["STRESS", "CONFLICT", "SELF_RELATION"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P6_EMOTION_INTELLECTUALIZATION"],
        "related_conflicts": [],
        "related_dimensions": ["D21_EMOTIONAL_DIFFERENTIATION", "D24_EXPERIENTIAL_AVOIDANCE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D21",
        "code": "D21_EMOTIONAL_DIFFERENTIATION",
        "domain": "DOMAIN_D_EMOTIONS",
        "name_en": "Emotional Differentiation",
        "name_ru": "Эмоциональная дифференциация",
        "definition": "Способность отличать тонкие оттенки чувств друг от друга (например, разочарование от обиды, тревогу от страха).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Схлопывание чувств в базовые корзины: 'мне плохо', 'меня кроет'.",
            "resource": "Снижение когнитивной нагрузки на анализ состояний.",
            "cost": "Невозможность подобрать правильный инструмент регуляции (лечить обиду как усталость)."
        },
        "high_pole": {
            "description": "Высокое разрешение эмоционального зрения. Распознавание сложных 'коктейлей' (светлая грусть с примесью вины).",
            "resource": "Высокий эмоциональный интеллект, точная коммуникация в отношениях.",
            "cost": "Склонность к избыточному 'копанию' в себе."
        },
        "scoring_anchors": {
            "0_20": "Все негативные эмоции воспринимаются как один 'ком'.",
            "21_40": "Различает базовые 4-5 эмоций (злость, страх, радость, грусть).",
            "41_60": "Средняя гранулярность. Может отличить усталость от грусти.",
            "61_80": "Высокая детализация. Замечает разницу между тревогой и страхом.",
            "81_100": "Исключительное богатство оттенков. Видит противоречивые слои в одном моменте."
        },
        "direct_evidence_tags": ["emotional_granularity", "mixed_feelings"],
        "indirect_evidence_tags": ["nuance_tolerance"],
        "negative_evidence_tags": ["all_or_nothing_emotions"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "SELF_RELATION"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D20_EMOTIONAL_AWARENESS", "D17_AMBIGUITY_TOLERANCE"],
        "interpretation_rules": [],
        "exclusion_rules": [
            "Requires D20_EMOTIONAL_AWARENESS to be at least medium to evaluate accurately."
        ]
    },
    {
        "id": "D22",
        "code": "D22_EMOTIONAL_TOLERANCE",
        "domain": "DOMAIN_D_EMOTIONS",
        "name_en": "Emotional Tolerance",
        "name_ru": "Эмоциональная толерантность (Выдерживание)",
        "definition": "Способность оставаться в контакте со сложными, болезненными эмоциями, не прибегая к немедленному бегству или подавлению.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Непереносимость дискомфорта. При малейшем стрессе — срочное заедание, запивание, скроллинг или побег.",
            "resource": "Быстрая анестезия, позволяющая не разрушиться в моменте.",
            "cost": "Формирование зависимостей. Непрожитые эмоции копятся и управляют поведением."
        },
        "high_pole": {
            "description": "Способность 'дышать через боль'. Разрешение эмоции быть, пока она не спадет сама.",
            "resource": "Глубокая психологическая переработка опыта, отсутствие нужды в дешевых дофаминовых заплатках.",
            "cost": "Риск превращения в мазохизм: терпение разрушительных ситуаций без попыток изменить их."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная непереносимость. Любой дискомфорт немедленно глушится.",
            "21_40": "Короткие вспышки может выдержать, но длительный стресс требует срочного отвлечения.",
            "41_60": "Среднее выдерживание. Справляется с грустью, но сбегает от стыда или бессилия.",
            "61_80": "Хороший контейнер. Может проживать боль, оставаясь функциональным.",
            "81_100": "Невероятная емкость контейнера. Выдерживает самые тяжелые состояния, не пытаясь от них избавиться."
        },
        "direct_evidence_tags": ["distress_tolerance", "sitting_with_feelings", "urge_surfing"],
        "indirect_evidence_tags": ["addictive_behaviors", "distraction_tactics"],
        "negative_evidence_tags": ["instant_gratification", "escaping_pain"],
        "exclusion_tags": [],
        "relevant_contexts": ["STRESS", "FAILURE", "CONFLICT"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P6_EMOTION_INTELLECTUALIZATION"],
        "related_conflicts": [],
        "related_dimensions": ["D24_EXPERIENTIAL_AVOIDANCE"],
        "interpretation_rules": [
            "IF D22_LOW AND D24_EXPERIENTIAL_AVOIDANCE_HIGH THEN confirm a strong protective barrier against internal experience."
        ],
        "exclusion_rules": []
    },
    {
        "id": "D23",
        "code": "D23_EMOTIONAL_EXPRESSION",
        "domain": "DOMAIN_D_EMOTIONS",
        "name_en": "Emotional Expression",
        "name_ru": "Эмоциональная проявленность",
        "definition": "Степень, в которой внутренние переживания свободно транслируются вовне (в мимике, словах, действиях).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Полная заморозка или покерфейс. Внутри буря, снаружи штиль.",
            "resource": "Сохранение лица в корпоративной среде, защита уязвимости от враждебного окружения.",
            "cost": "Окружающие не понимают, что происходит. Впечатление 'холодности' разрушает близость."
        },
        "high_pole": {
            "description": "Все, что чувствуется, немедленно оказывается на лице и в словах. Распахнутость.",
            "resource": "Искренность, понятность для партнеров, отсутствие заблокированной энергии в теле.",
            "cost": "Может быть воспринято как истеричность или 'too much'. Сложности в дипломатии."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная стена. Никто никогда не знает, что человек чувствует.",
            "21_40": "Высокий контроль проявлений. Показывает только 'социально одобряемые' чувства.",
            "41_60": "Регулируемая экспрессия. С близкими распахнут, на работе — закрыт.",
            "61_80": "Яркая экспрессия. Эмоции легко читаются по лицу и телу.",
            "81_100": "Невозможность скрыть ничего. Эмоции выплескиваются быстрее, чем осознаются."
        },
        "direct_evidence_tags": ["vulnerability_display", "poker_face", "sharing_feelings"],
        "indirect_evidence_tags": ["perceived_coldness_by_others"],
        "negative_evidence_tags": ["suppression_of_tears", "forced_smile"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "CONFLICT"],
        "context_modifiers": {
            "RELATIONSHIPS": "Low score here often triggers anxiety in highly anxious partners."
        },
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P4_SELF_SILENCING"],
        "related_conflicts": ["C6_AUTHENTICITY_VS_PROTECTION"],
        "related_dimensions": ["D20_EMOTIONAL_AWARENESS"],
        "interpretation_rules": [
            "IF D23_LOW AND D20_EMOTIONAL_AWARENESS_HIGH THEN note that the person knows exactly what they feel, but deliberately hides it."
        ],
        "exclusion_rules": []
    },
    {
        "id": "D24",
        "code": "D24_EXPERIENTIAL_AVOIDANCE",
        "domain": "DOMAIN_D_EMOTIONS",
        "name_en": "Experiential Avoidance",
        "name_ru": "Избегание опыта",
        "definition": "Тенденция избегать мыслей, чувств, воспоминаний или физических ощущений, даже если это вредит долгосрочным целям.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Радикальное принятие внутреннего опыта. Готовность чувствовать страх, но идти вперед.",
            "resource": "Способность реализовывать ценности несмотря на сложный эмоциональный фон.",
            "cost": "Может привести к перегрузке, если нет навыков разгрузки."
        },
        "high_pole": {
            "description": "Сжатие жизни ради того, чтобы не сталкиваться с тревогой или стыдом.",
            "resource": "Краткосрочное избавление от боли. Поддержание субъективного спокойствия.",
            "cost": "Жизнь становится все более узкой. Отказ от отношений, карьеры, реализации ради того, чтобы 'не чувствовать'."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная открытость любому опыту, как приятному, так и болезненному.",
            "21_40": "Редкое избегание, преимущественно идет в страх.",
            "41_60": "Избегает только крайне травматичного опыта, с бытовыми стрессами справляется.",
            "61_80": "Заметное сужение жизни. Отказывается от многих возможностей, чтобы не волноваться.",
            "81_100": "Тотальное бегство от жизни. Фобия собственных чувств."
        },
        "direct_evidence_tags": ["avoidance_behavior", "withdrawing_from_opportunities", "numbing"],
        "indirect_evidence_tags": ["procrastination", "isolation"],
        "negative_evidence_tags": ["facing_fears", "acceptance"],
        "exclusion_tags": ["clinical_phobias"],
        "relevant_contexts": ["UNCERTAINTY", "VISIBILITY", "RELATIONSHIPS"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P6_EMOTION_INTELLECTUALIZATION"],
        "related_conflicts": ["C3_VISIBILITY_VS_PROTECTION"],
        "related_dimensions": ["D22_EMOTIONAL_TOLERANCE"],
        "interpretation_rules": [
            "IF D24_HIGH THEN the primary leverage point is increasing tolerance to discomfort."
        ],
        "exclusion_rules": [
            "Do not score high avoidance if the user is strategically resting and choosing battles."
        ]
    },
    {
        "id": "D25",
        "code": "D25_REGULATION_FLEXIBILITY",
        "domain": "DOMAIN_D_EMOTIONS",
        "name_en": "Regulation Flexibility",
        "name_ru": "Гибкость регуляции",
        "definition": "Наличие богатого арсенала различных стратегий совладания (coping) со стрессом и умение применять их адекватно ситуации.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Использование одного и того же 'молотка' для всех гвоздей (только работает, или только плачет, или только злится).",
            "resource": "Предсказуемость реакций, автоматизм, не требующий когнитивных усилий.",
            "cost": "Стратегия часто не подходит к ситуации (например, интеллектуализация горя)."
        },
        "high_pole": {
            "description": "Широкий репертуар: может отвлечься, может погрузиться в боль, может переоценить ситуацию когнитивно.",
            "resource": "Высочайшая адаптивность к разным типам кризисов.",
            "cost": "Требует развитого эмоционального интеллекта и больших затрат энергии на начальных этапах."
        },
        "scoring_anchors": {
            "0_20": "Моно-стратегия (например, всегда только подавляет).",
            "21_40": "Использует 2-3 жесткие стратегии.",
            "41_60": "Может варьировать стратегии, но в сильном стрессе скатывается к одной базовой.",
            "61_80": "Хороший арсенал. Умеет подбирать ключи к разным состояниям.",
            "81_100": "Виртуозная саморегуляция. Способность применить парадоксальные стратегии."
        },
        "direct_evidence_tags": ["coping_variety", "adaptive_coping"],
        "indirect_evidence_tags": ["resilience"],
        "negative_evidence_tags": ["rigid_coping", "maladaptive_habits"],
        "exclusion_tags": [],
        "relevant_contexts": ["STRESS", "FAILURE"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D22_EMOTIONAL_TOLERANCE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    }
]

file_path = r"c:\Sher_AI_Studio\projects\selfmanual\src\domain\scoring\dictionaries\dimensions.json"

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

data.extend(new_dimensions)

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Appended {len(new_dimensions)} new dimensions. Total is now {len(data)}.")
