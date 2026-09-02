import json
import os

dimensions = [
    # DOMAIN A - SELF / ВНУТРЕННЯЯ ОПОРА
    {
        "id": "D01",
        "code": "D01_INTERNAL_SUPPORT",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Internal Support",
        "name_ru": "Внутренняя опора",
        "definition": "Способность сохранять ощущение собственной состоятельности без постоянного внешнего подтверждения.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Сильная зависимость самоощущения от внешних факторов, мнений и успехов. Хрупкость Я.",
            "resource": "Высокая чувствительность к социальным сигналам, быстрая адаптация к ожиданиям группы, эмпатичность.",
            "cost": "Постоянная тревога об оценке, невозможность принимать непопулярные решения, потеря связи с собственными желаниями."
        },
        "high_pole": {
            "description": "Высокая автономность самоощущения, устойчивость к внешней критике и неудачам.",
            "resource": "Позволяет выдерживать одиночество, отказы и длительное отсутствие результата без разрушения.",
            "cost": "При экстремально высоких значениях может приводить к самоизоляции, упрямству и нечувствительности к полезной обратной связи."
        },
        "scoring_anchors": {
            "0_20": "Самоотношение преимущественно определяется внешней реакцией; отдельная критика или неудача может значительно менять отношение к себе.",
            "21_40": "Внешнее подтверждение заметно влияет на устойчивость самоотношения.",
            "41_60": "Смешанный профиль; внутренняя и внешняя опора используются в зависимости от ситуации.",
            "61_80": "Преимущественно устойчивое внутреннее самоотношение при сохранении чувствительности к значимой обратной связи.",
            "81_100": "Очень высокая автономность самоотношения; внешняя оценка редко существенно меняет отношение к себе."
        },
        "direct_evidence_tags": ["self_worth_source", "reaction_to_failure", "reaction_to_criticism"],
        "indirect_evidence_tags": ["approval_seeking", "decision_making_autonomy"],
        "negative_evidence_tags": ["chronic_reassurance_seeking", "mood_swings_after_feedback", "fear_of_rejection"],
        "exclusion_tags": ["clinical_depression_markers"],
        "relevant_contexts": ["WORK", "RELATIONSHIPS", "VISIBILITY", "CONFLICT"],
        "context_modifiers": {
            "RELATIONSHIPS": "May manifest as boundary dissolution when low."
        },
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P1_APPROVAL_LOOP", "P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D02_SELF_WORTH_STABILITY", "D07_INTERNAL_LOCUS_OF_EVALUATION"],
        "interpretation_rules": [
            "IF context==RELATIONSHIPS AND score >= 80 THEN note potential risk of emotional distance.",
            "IF score <= 30 THEN frame as heightened interpersonal sensitivity rather than purely a deficit."
        ],
        "exclusion_rules": [
            "Do not infer low internal support solely from asking for advice in high-stakes professional contexts."
        ]
    },
    {
        "id": "D02",
        "code": "D02_SELF_WORTH_STABILITY",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Self-Worth Stability",
        "name_ru": "Стабильность самооценки",
        "definition": "Амплитуда колебаний отношения к себе в ответ на триггеры (успех/неудача, принятие/отвержение).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Резкие качели отношения к себе в зависимости от текущего результата или обратной связи.",
            "resource": "Огромный мобилизационный потенциал — страх упасть в 'ничтожество' заставляет достигать выдающихся результатов.",
            "cost": "Хроническое истощение, невозможность расслабиться, ощущение, что 'ты хорош настолько, насколько хорош твой последний результат'."
        },
        "high_pole": {
            "description": "Отношение к себе остается ровным, несмотря на локальные ошибки или достижения.",
            "resource": "Сохранение энергии в кризисах. Отсутствие необходимости постоянно 'доказывать' свою ценность.",
            "cost": "Может приводить к снижению амбиций и мотивации к сверхдостижениям."
        },
        "scoring_anchors": {
            "0_20": "Ярко выраженные эмоциональные качели. Ошибка воспринимается как крах личности.",
            "21_40": "Заметные колебания. Успех дает эйфорию, неудача отбрасывает назад.",
            "41_60": "Относительная стабильность в норме, но сильные триггеры все еще выбивают из колеи.",
            "61_80": "Хорошая стабильность. Ошибки расстраивают, но не рушат фундаментальное самоотношение.",
            "81_100": "Несгибаемое базовое отношение к себе. Результаты воспринимаются как внешние факты, а не как мера личности."
        },
        "direct_evidence_tags": ["mood_swings_after_feedback", "imposter_syndrome", "reaction_to_mistake"],
        "indirect_evidence_tags": ["perfectionism", "burnout_cycles"],
        "negative_evidence_tags": ["even_mood_under_pressure", "casual_attitude_to_failure"],
        "exclusion_tags": ["grief", "acute_trauma"],
        "relevant_contexts": ["ACHIEVEMENT", "RELATIONSHIPS", "FAILURE"],
        "context_modifiers": {},
        "state_sensitivity": "HIGH",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH", "P1_APPROVAL_LOOP"],
        "related_conflicts": ["C4_ACHIEVEMENT_VS_SELF_PRESERVATION"],
        "related_dimensions": ["D01_INTERNAL_SUPPORT", "D04_SELF_COMPASSION"],
        "interpretation_rules": [
            "IF score <= 30 AND context==ACHIEVEMENT THEN highlight the compensatory nature of their ambition."
        ],
        "exclusion_rules": [
            "Do not score low stability if mood swings are purely physiological or clearly situational (e.g. loss of a close person)."
        ]
    },
    {
        "id": "D03",
        "code": "D03_SELF_TRUST",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Self-Trust",
        "name_ru": "Доверие себе",
        "definition": "Уверенность в собственной способности справиться с будущими вызовами и правильности своих решений.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Хроническое сомнение в своих решениях, потребность советоваться.",
            "resource": "Тщательная проверка гипотез, минимизация грубых ошибок через сбор мнений.",
            "cost": "Паралич принятия решений, упущенные возможности, жизнь по чужим сценариям."
        },
        "high_pole": {
            "description": "Способность действовать на основе внутреннего отклика и неполной информации.",
            "resource": "Высокая скорость решений, способность быть первопроходцем, самодостаточность.",
            "cost": "Риск импульсивности, игнорирования объективных внешних рисков и полезного опыта других."
        },
        "scoring_anchors": {
            "0_20": "Крайняя степень неуверенности. Невозможность принять решение без одобрения авторитета.",
            "21_40": "Склонность делегировать ответственность за важные выборы.",
            "41_60": "Доверие себе зависит от сферы. В знакомых областях уверен, в новых - опирается на других.",
            "61_80": "Хорошее внутреннее чутье. Обращается за советом для обогащения картины, а не для снятия ответственности.",
            "81_100": "Абсолютная вера в свои решения, даже если весь мир против."
        },
        "direct_evidence_tags": ["decision_speed", "information_gathering_need", "autonomous_decision"],
        "indirect_evidence_tags": ["regret_frequency", "intuition_reliance"],
        "negative_evidence_tags": ["chronic_reassurance_seeking", "decision_paralysis", "excessive_information_gathering"],
        "exclusion_tags": [],
        "relevant_contexts": ["UNCERTAINTY", "WORK", "MONEY"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P3_CERTAINTY_BEFORE_ACTION", "P2_CONTROL_ANALYSIS_LOOP"],
        "related_conflicts": [],
        "related_dimensions": ["D08_ACTION_AGENCY", "D01_INTERNAL_SUPPORT"],
        "interpretation_rules": [
            "IF score <= 40 THEN frame as a cautious strategy rather than 'lack of confidence'."
        ],
        "exclusion_rules": [
            "Do not infer low self-trust from extensive information gathering when decision stakes are objectively high (e.g. buying a house).",
            "Do not infer low self-trust from consultation when user ultimately makes an autonomous decision."
        ]
    },
    {
        "id": "D04",
        "code": "D04_SELF_COMPASSION",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Self-Compassion",
        "name_ru": "Самосострадание",
        "definition": "Способность относиться к себе с поддержкой и пониманием в моменты ошибок, стресса и боли.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Жестокое отношение к себе при малейших промахах. Запрет на сочувствие к себе.",
            "resource": "Служит механизмом внутреннего контроля. Исключает 'расхлябанность' и попустительство.",
            "cost": "Разрушительное вторичное страдание при любой ошибке. Страх ошибки становится парализующим."
        },
        "high_pole": {
            "description": "Теплое и поддерживающее отношение к себе, способность быть себе другом в кризисе.",
            "resource": "Быстрое и конструктивное восстановление после неудач, профилактика выгорания.",
            "cost": "При крайне некритичной интерпретации своих действий поддержка может сочетаться с недостаточной ответственностью (требует подтверждения)."
        },
        "scoring_anchors": {
            "0_20": "Агрессивное нападение на себя при любой трудности. Восприятие сочувствия к себе как слабости.",
            "21_40": "Фоновая строгость. Поддержка себя включается редко и только после полного истощения.",
            "41_60": "Умение поддержать себя в сильном кризисе, но строгость в повседневных задачах.",
            "61_80": "Бережное отношение к своим ресурсам. Умение отделить свою ценность от совершенной ошибки.",
            "81_100": "Глубокое, безусловное самосострадание. Готовность прощать себе человеческие слабости и учиться на них без боли."
        },
        "direct_evidence_tags": ["reaction_to_mistake", "internal_dialogue", "self_forgiveness"],
        "indirect_evidence_tags": ["recovery_speed", "burnout_prevention"],
        "negative_evidence_tags": ["harsh_inner_critic", "self_punishment"],
        "exclusion_tags": [],
        "relevant_contexts": ["FAILURE", "STRESS", "SELF_RELATION"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH", "P4_SELF_SILENCING"],
        "related_conflicts": [],
        "related_dimensions": ["D05_SELF_CRITICISM", "D02_SELF_WORTH_STABILITY"],
        "interpretation_rules": [
            "IF D04_HIGH AND D08_ACTION_AGENCY_HIGH THEN interpret as highly resilient functioning."
        ],
        "exclusion_rules": [
            "Do not confuse high self-compassion with low accountability unless there is direct evidence of avoiding responsibility."
        ]
    },
    {
        "id": "D05",
        "code": "D05_SELF_CRITICISM",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Self-Criticism",
        "name_ru": "Самокритика",
        "definition": "Использование жесткой внутренней критики как основного механизма мотивации и контроля.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Отсутствие карающего голоса, конструктивный анализ ошибок без нападения на личность.",
            "resource": "Снижение фонового стресса. Энергия тратится на решение проблемы, а не на самобичевание.",
            "cost": "Может не хватать 'волшебного пинка' для старта в условиях отсутствия внешней мотивации."
        },
        "high_pole": {
            "description": "Постоянный фоновый мониторинг недостатков, наказание себя за несоответствие идеалу.",
            "resource": "Обеспечивает высокие стандарты качества и социальную безопасность ('я сам себя накажу первым').",
            "cost": "Хронический фоновый стресс, избегание рисков из-за страха внутреннего наказания, истощение."
        },
        "scoring_anchors": {
            "0_20": "Тотальный внутренний террор. Внутренний критик никогда не замолкает.",
            "21_40": "Выраженная критика. Является главным топливом для достижений.",
            "41_60": "Ситуативная критика. Включается только при значимых провалах.",
            "61_80": "Преимущественно конструктивный анализ. Критика отделена от идентичности.",
            "81_100": "Полное отсутствие карающего голоса. Абсолютно функциональный подход к ошибкам."
        },
        "direct_evidence_tags": ["internal_dialogue", "motivation_source", "harsh_inner_critic"],
        "indirect_evidence_tags": ["procrastination", "imposter_syndrome"],
        "negative_evidence_tags": ["self_compassion", "objective_error_analysis"],
        "exclusion_tags": [],
        "relevant_contexts": ["ACHIEVEMENT", "VISIBILITY", "FAILURE"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH", "P3_CERTAINTY_BEFORE_ACTION"],
        "related_conflicts": ["C3_VISIBILITY_VS_PROTECTION"],
        "related_dimensions": ["D04_SELF_COMPASSION", "D02_SELF_WORTH_STABILITY"],
        "interpretation_rules": [
            "IF D05_HIGH AND D08_ACTION_AGENCY_LOW THEN interpret self-criticism as a paralyzing agent."
        ],
        "exclusion_rules": []
    },
    {
        "id": "D06",
        "code": "D06_IDENTITY_STABILITY",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Identity Stability",
        "name_ru": "Стабильность идентичности",
        "definition": "Наличие ясного, последовательного и устойчивого понимания 'Кто я такой', 'Что для меня важно' и 'Чего я хочу'.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Размытость Я. Подстраивание своих желаний и взглядов под текущее окружение (хамелеонство).",
            "resource": "Экстремальная социальная гибкость, способность встроиться в любой контекст, легкость на подъем.",
            "cost": "Потеря ориентиров, жизнь чужой жизнью, хроническое ощущение 'я не знаю, чего хочу'."
        },
        "high_pole": {
            "description": "Устойчивое Я. Ясное понимание своих ценностей, которое не меняется в угоду ситуации.",
            "resource": "Основа для долгосрочных обязательств, способность выстраивать глубокие отношения и реализовывать длинные стратегии.",
            "cost": "В комбинации с низкой гибкостью — риск ригидности, упрямства и неспособности адаптироваться."
        },
        "scoring_anchors": {
            "0_20": "Крайняя фрагментация Я. Желания меняются каждый день в зависимости от окружения.",
            "21_40": "Заметная подстройка. Ценности часто берутся 'напрокат' у авторитетов.",
            "41_60": "Базовый стержень есть, но в сложных контекстах (например, в слиянии с партнером) границы Я плывут.",
            "61_80": "Хорошо очерченная идентичность, допускающая развитие.",
            "81_100": "Монолитное, кристально ясное понимание себя и своих ценностей."
        },
        "direct_evidence_tags": ["sense_of_self", "value_clarity", "chameleon_behavior"],
        "indirect_evidence_tags": ["boundary_flexibility", "goal_consistency"],
        "negative_evidence_tags": ["identity_diffusion", "frequent_radical_life_changes", "adopting_others_values"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "CONFLICT", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P1_APPROVAL_LOOP"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D01_INTERNAL_SUPPORT", "D07_INTERNAL_LOCUS_OF_EVALUATION"],
        "interpretation_rules": [
            "IF D06_LOW THEN explore mechanisms of adapting to others' expectations."
        ],
        "exclusion_rules": [
            "Do not score low identity stability during a normative life crisis (e.g. mid-life transition) where values are actively being re-evaluated."
        ]
    },
    {
        "id": "D07",
        "code": "D07_INTERNAL_LOCUS_OF_EVALUATION",
        "domain": "DOMAIN_A_SELF",
        "name_en": "Internal Locus of Evaluation",
        "name_ru": "Внутренний локус оценки",
        "definition": "Степень, в которой критерии успеха и правильности исходят изнутри, а не навязываются извне.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Ориентация на социально одобряемые метрики (статус, чужое признание, 'как принято').",
            "resource": "Социальная адекватность, понятность для окружающих, легкая интеграция в иерархии.",
            "cost": "Вечная погоня за 'правильными' целями, которые не приносят внутреннего удовлетворения."
        },
        "high_pole": {
            "description": "Ориентация на собственные критерии качества и смысла, даже если они расходятся с ожиданиями социума.",
            "resource": "Глубокая аутентичность, устойчивость к модным трендам, способность идти своим путем.",
            "cost": "Риск маргинализации, конфликта с социальными институтами или упущенной выгоды от несоблюдения 'правил игры'."
        },
        "scoring_anchors": {
            "0_20": "Полная зависимость от внешних критериев. Успех измеряется только глазами других.",
            "21_40": "Внешние метрики преобладают, внутренние голоса часто игнорируются ради одобрения.",
            "41_60": "Попытка балансировать. В работе - внешние критерии, в хобби - внутренние.",
            "61_80": "Внутренние критерии первичны, но внешняя оценка учитывается как полезная обратная связь.",
            "81_100": "Абсолютная опора на свой компас. Внешние метрики успеха игнорируются, если они противоречат внутренним."
        },
        "direct_evidence_tags": ["success_criteria", "reaction_to_praise", "goal_setting_source"],
        "indirect_evidence_tags": ["career_choices", "lifestyle_choices"],
        "negative_evidence_tags": ["status_seeking", "keeping_up_with_the_joneses"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "ACHIEVEMENT", "MONEY"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D01_INTERNAL_SUPPORT", "D06_IDENTITY_STABILITY"],
        "interpretation_rules": [],
        "exclusion_rules": [
            "Do not penalize score for considering market realities in business contexts; strategic alignment with external metrics is not necessarily low internal locus."
        ]
    },

    # DOMAIN B - ACTION / СУБЪЕКТНОСТЬ
    {
        "id": "D08",
        "code": "D08_ACTION_AGENCY",
        "domain": "DOMAIN_B_ACTION",
        "name_en": "Action Agency",
        "name_ru": "Субъектность действия",
        "definition": "Способность переводить намерение в действие, брать ответственность за изменения и инициировать процессы.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Склонность занимать пассивную или выжидательную позицию. Ожидание, что ситуация разрешится сама или кто-то другой сделает первый шаг.",
            "resource": "Сохранение энергии, минимизация риска неверного шага, способность органично встраиваться в чужие инициативы.",
            "cost": "Потеря контроля над своей жизнью, ощущение себя жертвой обстоятельств, упущенное время."
        },
        "high_pole": {
            "description": "Проактивная позиция. Способность инициировать изменения, не дожидаясь идеальных условий или внешнего разрешения.",
            "resource": "Высокая результативность, управление своей жизнью, способность менять реальность под себя.",
            "cost": "Может приводить к излишнему контролю ('я должен все сделать сам'), неумению отпустить ситуацию или чрезмерному давлению на окружающих."
        },
        "scoring_anchors": {
            "0_20": "Крайняя пассивность. Жизнь 'случается' с человеком. Реактивная позиция.",
            "21_40": "Действует только при сильном внешнем стимуле или давлении обстоятельств.",
            "41_60": "Ситуативная субъектность. В одной сфере активен, в другой — ждет инициативы извне.",
            "61_80": "Хороший уровень проактивности. Регулярно инициирует изменения, но может 'буксовать' в сложных узлах.",
            "81_100": "Ярко выраженная авторская позиция. Не ждет, а создает условия сам."
        },
        "direct_evidence_tags": ["proactive_initiation", "responsibility_taking", "waiting_strategy"],
        "indirect_evidence_tags": ["career_progression_style", "conflict_initiation"],
        "negative_evidence_tags": ["victim_mentality", "passive_waiting", "blaming_circumstances"],
        "exclusion_tags": ["burnout", "clinical_depression"],
        "relevant_contexts": ["WORK", "UNCERTAINTY", "RELATIONSHIPS"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P2_CONTROL_ANALYSIS_LOOP"],
        "related_conflicts": ["C2_FREEDOM_VS_SECURITY"],
        "related_dimensions": ["D09_DECISIVENESS", "D11_PERSISTENCE"],
        "interpretation_rules": [
            "IF D08_HIGH AND D12_BEHAVIORAL_FLEXIBILITY_LOW THEN note risk of forcing outcomes."
        ],
        "exclusion_rules": [
            "Do not score low agency if waiting is a deliberate, calculated strategic pause."
        ]
    },
    {
        "id": "D09",
        "code": "D09_DECISIVENESS",
        "domain": "DOMAIN_B_ACTION",
        "name_en": "Decisiveness",
        "name_ru": "Решительность",
        "definition": "Скорость и легкость принятия решений, особенно в условиях недостатка информации или гарантий.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Долгие сомнения, бесконечный сбор данных, попытка просчитать все варианты перед выбором.",
            "resource": "Снижение риска грубых ошибок, глубокая аналитика, защита от необдуманных шагов.",
            "cost": "Паралич анализа. Решение откладывается до тех пор, пока окно возможностей не закроется."
        },
        "high_pole": {
            "description": "Способность быстро 'рубить узлы'. Решения принимаются даже при 70% информации.",
            "resource": "Высокая скорость движения, захват возможностей, отсутствие изнуряющих внутренних торгов.",
            "cost": "Риск импульсивности, поспешные выводы, необходимость исправлять последствия 'на ходу'."
        },
        "scoring_anchors": {
            "0_20": "Хронический паралич решений. Любой выбор вызывает мучения.",
            "21_40": "Заметное затягивание решений, сильная потребность в дополнительных данных.",
            "41_60": "Средняя скорость. Простые решения принимаются легко, сложные требуют длительного 'вызревания'.",
            "61_80": "Хорошая решительность. Способность поставить точку в анализе и сделать выбор.",
            "81_100": "Мгновенное принятие решений. Высокая толерантность к риску ошибиться."
        },
        "direct_evidence_tags": ["decision_speed", "analysis_paralysis", "information_gathering"],
        "indirect_evidence_tags": ["regret_over_missed_opportunities"],
        "negative_evidence_tags": ["endless_deliberation", "fear_of_wrong_choice"],
        "exclusion_tags": [],
        "relevant_contexts": ["UNCERTAINTY", "WORK", "MONEY"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P3_CERTAINTY_BEFORE_ACTION", "P2_CONTROL_ANALYSIS_LOOP"],
        "related_conflicts": [],
        "related_dimensions": ["D03_SELF_TRUST", "D10_TOLERANCE_OF_IMPERFECT_ACTION"],
        "interpretation_rules": [
            "IF D09_LOW THEN explore the specific fear driving the delay (e.g. fear of judgment vs fear of failure)."
        ],
        "exclusion_rules": [
            "Do not score low decisiveness for complex strategic decisions that objectively require time."
        ]
    },
    {
        "id": "D10",
        "code": "D10_TOLERANCE_OF_IMPERFECT_ACTION",
        "domain": "DOMAIN_B_ACTION",
        "name_en": "Tolerance of Imperfect Action",
        "name_ru": "Толерантность к неидеальному действию",
        "definition": "Способность действовать и выпускать результаты в мир, когда они еще 'сырые' или не соответствуют идеальным стандартам.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Жесткий перфекционизм. 'Или идеально, или никак'. Действие блокируется страхом выдать средний результат.",
            "resource": "Гарантия высокого качества. Защита от критики (так как продукт вылизан до идеала).",
            "cost": "Хроническое откладывание запусков. Много работы 'в стол'. Неспособность к быстрым итерациям."
        },
        "high_pole": {
            "description": "Легкость в запуске 'черновиков'. Установка 'done is better than perfect'.",
            "resource": "Быстрое тестирование гипотез, получение реальной обратной связи от мира, высокая скорость обучения.",
            "cost": "Риск репутационных потерь из-за откровенной халтуры. Поверхностность."
        },
        "scoring_anchors": {
            "0_20": "Крайний перфекционизм. Полная неспособность показать миру что-либо неидеальное.",
            "21_40": "Высокие стандарты сильно тормозят процесс. Много переделок перед финальным шагом.",
            "41_60": "Может выпустить 'достаточно хорошее' в рутине, но перфекционист в значимых проектах.",
            "61_80": "Способен запускать MVP (минимальный продукт). Понимает ценность быстрой ошибки.",
            "81_100": "Абсолютная легкость в действии. Полное отсутствие стыда за 'сырой' результат."
        },
        "direct_evidence_tags": ["perfectionism", "shipping_speed", "draft_tolerance"],
        "indirect_evidence_tags": ["procrastination_before_launch"],
        "negative_evidence_tags": ["endless_polishing", "hiding_work"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "VISIBILITY", "ACHIEVEMENT"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH", "P4_SELF_SILENCING"],
        "related_conflicts": ["C3_VISIBILITY_VS_PROTECTION"],
        "related_dimensions": ["D05_SELF_CRITICISM", "D09_DECISIVENESS"],
        "interpretation_rules": [
            "IF D10_LOW AND D05_SELF_CRITICISM_HIGH THEN note that perfect action is a defense mechanism against the inner critic."
        ],
        "exclusion_rules": [
            "Do not score low tolerance if the context objectively demands zero-defect performance (e.g. surgeon, aviation)."
        ]
    },
    {
        "id": "D11",
        "code": "D11_PERSISTENCE",
        "domain": "DOMAIN_B_ACTION",
        "name_en": "Persistence",
        "name_ru": "Настойчивость (Упорство)",
        "definition": "Способность продолжать целенаправленные действия на длинной дистанции, несмотря на скуку, препятствия и отсутствие быстрого результата.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Склонность быстро загораться и бросать при первых трудностях или падении интереса.",
            "resource": "Способность быстро тестировать много ниш, не застревать в мертвых проектах, следовать за энергией.",
            "cost": "Неспособность получить результаты, требующие длительного накопления усилий. Поверхностность."
        },
        "high_pole": {
            "description": "Способность методично 'бить в одну точку' годами. Доведение дел до конца.",
            "resource": "Достижение масштабных, сложных целей. Надежность, кумулятивный эффект усилий.",
            "cost": "Риск упрямства: продолжение движения в тупик просто потому, что 'не привык бросать'. 'Ловушка невозвратных затрат'."
        },
        "scoring_anchors": {
            "0_20": "Крайняя неустойчивость внимания. Бросает дела при первых признаках рутины.",
            "21_40": "Часто меняет направления. Требуется сильная внешняя стимуляция для продолжения.",
            "41_60": "Среднее упорство. Завершает важные проекты, но может бросать личные инициативы.",
            "61_80": "Высокая настойчивость. Способен долго работать без подкрепления.",
            "81_100": "Экстремальное упорство. Движется к цели несмотря ни на что (даже когда объективно пора остановиться)."
        },
        "direct_evidence_tags": ["project_completion_rate", "reaction_to_boredom", "long_term_goals"],
        "indirect_evidence_tags": ["habit_maintenance", "delayed_gratification"],
        "negative_evidence_tags": ["frequent_quitting", "shiny_object_syndrome"],
        "exclusion_tags": ["ADHD_markers"],
        "relevant_contexts": ["WORK", "ACHIEVEMENT"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D08_ACTION_AGENCY", "D12_BEHAVIORAL_FLEXIBILITY"],
        "interpretation_rules": [
            "IF D11_HIGH AND D12_BEHAVIORAL_FLEXIBILITY_LOW THEN highlight the risk of 'sunk cost fallacy'."
        ],
        "exclusion_rules": [
            "Do not score low persistence if the quitting was a highly strategic, rational pivot."
        ]
    },
    {
        "id": "D12",
        "code": "D12_BEHAVIORAL_FLEXIBILITY",
        "domain": "DOMAIN_B_ACTION",
        "name_en": "Behavioral Flexibility",
        "name_ru": "Поведенческая гибкость",
        "definition": "Способность менять свои стратегии и планы, когда обратная связь от реальности показывает их неэффективность.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Ригидность. Повторение одних и тех же действий с надеждой на другой результат. Упрямое следование первоначальному плану.",
            "resource": "Предсказуемость, стабильность, способность выдерживать хаос за счет жесткой структуры.",
            "cost": "Разбивание лба о стену. Неспособность адаптироваться к быстро меняющимся условиям."
        },
        "high_pole": {
            "description": "Пластичность. Готовность мгновенно перестроить подход, отказаться от неработающей гипотезы.",
            "resource": "Выживаемость в кризисах, быстрая обучаемость, нахождение нестандартных путей.",
            "cost": "Может приводить к отсутствию твердой линии, хаотичности и невозможности довести дело до конца."
        },
        "scoring_anchors": {
            "0_20": "Крайняя ригидность. 'Будет так, как я сказал, даже если это приведет к катастрофе'.",
            "21_40": "Тяжело перестраивается. Долго сопротивляется новой информации.",
            "41_60": "Баланс. Держит структуру, но готов изменить план при наличии веских доказательств.",
            "61_80": "Высокая гибкость. Легко пивотируется (меняет направление) без сожалений.",
            "81_100": "Крайняя текучесть. Стратегия меняется так часто, что система не успевает стабилизироваться."
        },
        "direct_evidence_tags": ["strategy_change", "reaction_to_negative_feedback", "plan_revision"],
        "indirect_evidence_tags": ["adaptability"],
        "negative_evidence_tags": ["stubbornness", "repeating_mistakes"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "UNCERTAINTY", "FAILURE"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D11_PERSISTENCE", "D06_IDENTITY_STABILITY"],
        "interpretation_rules": [
            "IF D06_IDENTITY_STABILITY_HIGH AND D12_LOW THEN interpret: Stable identity may become rigid under changing conditions."
        ],
        "exclusion_rules": [
            "Do not score low flexibility if the user is maintaining a boundary based on core values."
        ]
    },
    {
        "id": "D13",
        "code": "D13_RECOVERY_AFTER_FAILURE",
        "domain": "DOMAIN_B_ACTION",
        "name_en": "Recovery After Failure",
        "name_ru": "Восстановление после неудачи (Resilience)",
        "definition": "Скорость и качество возвращения в функциональное состояние после значимых провалов или отказов.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Длительное 'залипание' в неудаче. Падение мотивации, самобичевание, страх новых попыток.",
            "resource": "Глубокая переработка опыта, страховка от повторения тех же ошибок (через избегание).",
            "cost": "Упущенное время, формирование выученной беспомощности, снижение толерантности к риску."
        },
        "high_pole": {
            "description": "Быстрый 'отскок'. Неудача воспринимается как обратная связь, а не как приговор.",
            "resource": "Возможность делать много попыток. Антихрупкость.",
            "cost": "При экстремально высоких значениях: недостаточная рефлексия, обесценивание потерь, прыжок в новое дело без выводов."
        },
        "scoring_anchors": {
            "0_20": "Одна крупная неудача может выбить из колеи на месяцы или годы.",
            "21_40": "Восстановление долгое и тяжелое, требует много внешней поддержки.",
            "41_60": "Средний 'отскок'. Проживает боль, но в разумные сроки возвращается к делу.",
            "61_80": "Быстрое восстановление. Фокус смещается с 'почему я упал' на 'как подняться'.",
            "81_100": "Неудача мгновенно конвертируется в опыт. Поразительная устойчивость."
        },
        "direct_evidence_tags": ["bounce_back_speed", "post_failure_behavior", "learning_from_mistakes"],
        "indirect_evidence_tags": ["optimism", "risk_appetite"],
        "negative_evidence_tags": ["dwelling_on_past", "fear_of_trying_again"],
        "exclusion_tags": ["clinical_trauma"],
        "relevant_contexts": ["FAILURE", "ACHIEVEMENT"],
        "context_modifiers": {},
        "state_sensitivity": "HIGH",
        "minimum_evidence": {
            "medium_confidence": 3,
            "high_confidence": 5
        },
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": [],
        "related_dimensions": ["D04_SELF_COMPASSION", "D02_SELF_WORTH_STABILITY"],
        "interpretation_rules": [
            "IF D13_HIGH AND D05_SELF_CRITICISM_LOW THEN note that constructive self-relation fuels resilience."
        ],
        "exclusion_rules": [
            "Do not score low recovery if the failure was catastrophic (e.g. bankruptcy, death of business) and insufficient time has passed."
        ]
    }
]

output_dir = r"c:\Sher_AI_Studio\projects\selfmanual\src\domain\scoring\dictionaries"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "dimensions.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dimensions, f, indent=2, ensure_ascii=False)

print(f"Generated {len(dimensions)} dimensions to {output_path}")
