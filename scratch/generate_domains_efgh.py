import json
import os

new_dimensions = [
    # DOMAIN E - ACHIEVEMENT / MOTIVATION
    {
        "id": "D26",
        "code": "D26_ACHIEVEMENT_ORIENTATION",
        "domain": "DOMAIN_E_ACHIEVEMENT",
        "name_en": "Achievement Orientation",
        "name_ru": "Ориентация на достижения",
        "definition": "Фокус на достижении высоких результатов, поставленных целей и постоянном профессиональном/личностном росте.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Гедонистическая ориентация, предпочтение комфорта, стабильности и процесса вместо результата.",
            "resource": "Умение наслаждаться моментом, низкий риск выгорания от амбиций, удовлетворенность имеющимся.",
            "cost": "Может приводить к стагнации, нереализованному потенциалу и упущенным возможностям."
        },
        "high_pole": {
            "description": "Высокие амбиции, постоянная планка выше текущего уровня, ориентация на победы.",
            "resource": "Высокий социальный и финансовый статус, преодоление трудностей, масштаб проектов.",
            "cost": "Обесценивание достигнутого, невозможность остановиться, синдром 'недостаточно хорошо'."
        },
        "scoring_anchors": {
            "0_20": "Абсолютное отсутствие амбиций, ориентация исключительно на покоить и сохранность.",
            "21_40": "Низкая мотивация к достижениям, редкая постановка амбициозных целей.",
            "41_60": "Баланс амбиций и комфорта. Работает на результат, но не в ущерб качеству жизни.",
            "61_80": "Высокая целеустремленность. Результаты являются важной частью самоотношения.",
            "81_100": "Крайняя степень достиженчества. Вся жизнь подчинена целям и метрикам."
        },
        "direct_evidence_tags": ["ambition_level", "goal_setting_style", "drive_for_results"],
        "indirect_evidence_tags": ["workaholism", "competitiveness"],
        "negative_evidence_tags": ["contentment", "process_enjoyment"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "ACHIEVEMENT", "MONEY"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": ["C4_ACHIEVEMENT_VS_SELF_PRESERVATION"],
        "related_dimensions": ["D02_SELF_WORTH_STABILITY", "D28_PERFECTIONISTIC_SELF_MONITORING"],
        "interpretation_rules": [
            "IF D26_HIGH AND D02_SELF_WORTH_STABILITY_LOW THEN achievement is compensatory for fragile self-esteem."
        ],
        "exclusion_rules": []
    },
    {
        "id": "D27",
        "code": "D27_FAILURE_TOLERANCE",
        "domain": "DOMAIN_E_ACHIEVEMENT",
        "name_en": "Failure Tolerance",
        "name_ru": "Толерантность к ошибкам",
        "definition": "Способность воспринимать ошибки и провалы как нормальную часть обучения и развития, а не как личностную катастрофу.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Страх ошибки блокирует действия. Ошибка воспринимается как окончательное доказательство несостоятельности.",
            "resource": "Сверхтщательность, высокий уровень контроля качества.",
            "cost": "Паралич действий, прокрастинация, неспособность к инновациям."
        },
        "high_pole": {
            "description": "Спокойное отношение к промахам. Ошибка — это просто данные для корректировки гипотезы.",
            "resource": "Высокая скорость итераций, отсутствие стыда за ошибки, быстрая обучаемость.",
            "cost": "Может переходить в халатность и повторение одних и тех же ошибок из-за отсутствия глубокой рефлексии."
        },
        "scoring_anchors": {
            "0_20": "Страх ошибки парализует любые начинания.",
            "21_40": "Ошибка вызывает сильный стыд и самокритику.",
            "41_60": "Ошибаться неприятно, но опыт анализируется и учитывается.",
            "61_80": "Хорошая устойчивость. Ошибка воспринимается как рабочая ситуация.",
            "81_100": "Абсолютная толерантность. Ошибки воспринимаются с азартом и благодарностью за опыт."
        },
        "direct_evidence_tags": ["error_reaction", "mistake_shame", "learning_attitude"],
        "indirect_evidence_tags": ["experimentation_readiness"],
        "negative_evidence_tags": ["fear_of_failure", "hiding_errors"],
        "exclusion_tags": [],
        "relevant_contexts": ["ACHIEVEMENT", "FAILURE", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": [],
        "related_dimensions": ["D04_SELF_COMPASSION", "D10_TOLERANCE_OF_IMPERFECT_ACTION"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D28",
        "code": "D28_PERFECTIONISTIC_SELF_MONITORING",
        "domain": "DOMAIN_E_ACHIEVEMENT",
        "name_en": "Perfectionistic Self-Monitoring",
        "name_ru": "Перфекционистский самомониторинг",
        "definition": "Постоянный жесткий фоновый контроль над своим поведением, проявлениями и результатами с целью соответствия недостижимому идеалу.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Естественность, спонтанность, принятие собственного несовершенства.",
            "resource": "Легкость в общении, экономия ментальной энергии, расслабленность.",
            "cost": "Может восприниматься как несобранность или невысокая требовательность к себе."
        },
        "high_pole": {
            "description": "Гиперконтроль каждого шага и слова, постоянное сравнение себя с идеальным образом.",
            "resource": "Высочайшая точность, аккуратность, создание безупречных формальных результатов.",
            "cost": "Хроническое истощение, невозможность расслабиться, постоянный страх 'разоблачения'."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная спонтанность. Полное отсутствие внутреннего цензора.",
            "21_40": "Легкий самомониторинг только в публичных ситуациях.",
            "41_60": "Умеренный контролер. Включается при важных задачах.",
            "61_80": "Высокий перфекционистский контроль. Постоянное напряжение.",
            "81_100": "Тотальный контроль каждого вздоха. Невозможность быть собой ни на секунду."
        },
        "direct_evidence_tags": ["perfectionism", "hyper_vigilance", "ideal_self_comparison"],
        "indirect_evidence_tags": ["imposter_syndrome", "exhaustion"],
        "negative_evidence_tags": ["spontaneity", "self_acceptance"],
        "exclusion_tags": [],
        "relevant_contexts": ["ACHIEVEMENT", "VISIBILITY", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": ["C3_VISIBILITY_VS_PROTECTION"],
        "related_dimensions": ["D05_SELF_CRITICISM", "D10_TOLERANCE_OF_IMPERFECT_ACTION"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D29",
        "code": "D29_EXTRINSIC_VS_INTRINSIC_DRIVE",
        "domain": "DOMAIN_E_ACHIEVEMENT",
        "name_en": "Intrinsic Motivation Share",
        "name_ru": "Доля внутренней мотивации",
        "definition": "Преобладание внутреннего интереса, азарта и смысла (Intrinsic) над внешними стимулами, наградами и одобрением (Extrinsic).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Преобладание внешней мотивации: деньги, статус, одобрение, страх наказания.",
            "resource": "Легкая управляемость через внешние стимулы, адаптивность к социальным рынкам.",
            "cost": "Выгорание при отсутствии внешних пряников, утеря смысла деятельности."
        },
        "high_pole": {
            "description": "Преобладание внутренней мотивации: подлинный curiosity, кайф от процесса, автономия.",
            "resource": "Неиссякаемый источник энергии, устойчивость в автономной работе, аутентичность.",
            "cost": "Трудно делать то, что 'надо', но не интересно; игнорирование рыночных требований."
        },
        "scoring_anchors": {
            "0_20": "Действует исключительно ради внешней награды или избегания проблем.",
            "21_40": "Внешние стимулы сильно преобладают над личным интересом.",
            "41_60": "Баланс. Работает за деньги, но выбирает то, что интересно.",
            "61_80": "Преимущественно внутренняя мотивация при понимании внешних контекстов.",
            "81_100": "Исключительно чистый внутренний двигатель и любопытство."
        },
        "direct_evidence_tags": ["motivation_type", "curiosity_driven", "reward_seeking"],
        "indirect_evidence_tags": ["burnout_vulnerability"],
        "negative_evidence_tags": ["money_driven_only", "status_seeking"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "ACHIEVEMENT"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D07_INTERNAL_LOCUS_OF_EVALUATION"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D30",
        "code": "D30_CHALLENGE_SEEKING",
        "domain": "DOMAIN_E_ACHIEVEMENT",
        "name_en": "Challenge Seeking",
        "name_ru": "Поиск вызовов",
        "definition": "Склонность выбираться из зоны комфорта, ставить перед собой заведомо сложные и нетривиальные задачи.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Предпочтение понятных, проверенных задач. Сохранение энергии.",
            "resource": "Предсказуемость результатов, высокая надежность в рутине, покой.",
            "cost": "Застревание на плато, скука, медленный рост профессионализма."
        },
        "high_pole": {
            "description": "Азарт перед лицом неизвестного и сложного. 'Чем сложнее, тем интереснее'.",
            "resource": "Быстрый кратный рост, лидерство, совершение прорывов.",
            "cost": "Переоценка своих сил, регулярное попадание в зоны выгорания и перегрузки."
        },
        "scoring_anchors": {
            "0_20": "Абсолютное избегание любых трудностей и новизны.",
            "21_40": "Предпочтение комфортной рутины. Вызовы берутся только по необходимости.",
            "41_60": "Умеренный аппетит к вызовам. Берет сложные задачи с понятным запасом сил.",
            "61_80": "Любит тестировать себя на прочность. Постоянный поиск роста.",
            "81_100": "Жажда экстремальных вызовов. Обычная жизнь кажется серой."
        },
        "direct_evidence_tags": ["growth_mindset", "comfort_zone_leaving", "ambition_for_diff"],
        "indirect_evidence_tags": ["boredom_in_stability"],
        "negative_evidence_tags": ["safety_seeking", "routine_enjoyment"],
        "exclusion_tags": [],
        "relevant_contexts": ["WORK", "ACHIEVEMENT", "UNCERTAINTY"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D18_RISK_TOLERANCE", "D26_ACHIEVEMENT_ORIENTATION"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },

    # DOMAIN F - INTERPERSONAL / VISIBILITY
    {
        "id": "D31",
        "code": "D31_BOUNDARY_FLEXIBILITY",
        "domain": "DOMAIN_F_INTERPERSONAL",
        "name_en": "Boundary Flexibility",
        "name_ru": "Гибкость личных границ",
        "definition": "Способность удерживать оптимальный баланс между отстаиванием своих интересов ('НЕТ') и умением идти на компромисс.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Либо размытые границы (слияние, неспособность сказать 'нет'), либо жесткая железобетонная стена.",
            "resource": "При слиянии — быстрая интеграция; при стене — абсолютная защищенность от посягательств.",
            "cost": "Эксплуатация окружением или полная эмоциональная изоляция."
        },
        "high_pole": {
            "description": "Здоровые адаптивные границы. Умение сказать 'нет' без вины и приоткрыть границы для близости.",
            "resource": "Безопасная близость, взаимное уважение, сохранение энергии.",
            "cost": "Требует постоянной осознанности и удержания контакта с собой."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная неспособность защитить себя или тотальная броня от всех.",
            "21_40": "Границы часто нарушаются, испытывает огромное чувство вины при отказе.",
            "41_60": "Один контекст проработан (например, работа), в другом — границы плывут (семья).",
            "61_80": "Уверенная защита своих границ без агрессии и вины.",
            "81_100": "Виртуозное владение границами: от полного контакта до мгновенной защиты."
        },
        "direct_evidence_tags": ["saying_no", "boundary_setting", "guilt_on_refusal"],
        "indirect_evidence_tags": ["resentment_level"],
        "negative_evidence_tags": ["people_pleasing", "isolation_wall"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "CONFLICT", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P4_SELF_SILENCING", "P1_APPROVAL_LOOP"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D33_NEED_TO_BELONG", "D36_HYPER_INDEPENDENCE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D32",
        "code": "D32_REJECTION_SENSITIVITY",
        "domain": "DOMAIN_F_INTERPERSONAL",
        "name_en": "Rejection Sensitivity",
        "name_ru": "Чувствительность к отвержению",
        "definition": "Склонность болезненно воспринимать реальные или гипотетические сигналы холодности, отказа или отвержения со стороны других.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Устойчивость к чужой неприязни. Отказ воспринимается как факт, а не как отвержение личности.",
            "resource": "Свобода в проявленности, легкие продажи, способность идти на риск в контактах.",
            "cost": "Может быть нечувствителен к тонким намекам на нежелательность своего присутствия."
        },
        "high_pole": {
            "description": "Гиперчувствительность к дистанции. Малейшая задержка ответа на сообщение интерпретируется как 'меня бросили'.",
            "resource": "Сверхточная настройка на эмоциональную температуру отношений.",
            "cost": "Постоянная тревога в отношениях, упреждающее бегство или подстраивание под других."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная броня. Чужое отвержение вообще не задевает.",
            "21_40": "Низкая чувствительность. Легко переносит отказы.",
            "41_60": "Отказ задевает, но не приводит к катастрофе или разрыву контакта.",
            "61_80": "Высокая ранимость. Любой намек на отказ вызывает сильную боль.",
            "81_100": "Парализующий страх отвержения. Жизнь в постоянном упреждающем страхе."
        },
        "direct_evidence_tags": ["rejection_fear", "hyper_vigilance_in_relationships", "abandonment_fear"],
        "indirect_evidence_tags": ["preemptive_withdrawal"],
        "negative_evidence_tags": ["thick_skin", "easy_approach"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "VISIBILITY", "CONFLICT"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P1_APPROVAL_LOOP", "P4_SELF_SILENCING"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D01_INTERNAL_SUPPORT", "D33_NEED_TO_BELONG"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D33",
        "code": "D33_NEED_TO_BELONG",
        "domain": "DOMAIN_F_INTERPERSONAL",
        "name_en": "Need to Belong / Approval Seeking",
        "name_ru": "Потребность в принадлежности и одобрении",
        "definition": "Степень значимости быть принятым группой/значимыми другими и соответствовать их ожиданиям.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Низок фокус на групповом одобрении. Готовность быть одиночкой или изгоем ради своих принципов.",
            "resource": "Независимость, способность к бунту и лидерству, стойкость против давления среды.",
            "cost": "Риск социализации, сложности с командной работой, чувство одиночества."
        },
        "high_pole": {
            "description": "Высокая потребность в 'мы'. Готовность жертвовать собственным мнением ради сохранения гармонии в группе.",
            "resource": "Прекрасный командный игрок, эмпат, создатель теплой атмосферы вокруг.",
            "cost": "Потеря собственного голоса, конформизм, зависимость от внешнего лайка."
        },
        "scoring_anchors": {
            "0_20": "Полный волк-одиночка. Одобрение группы не имеет никакого значения.",
            "21_40": "Принадлежность важна, но ценности и личные интересы всегда на первом месте.",
            "41_60": "Баланс. Ищет свою стаю, но не готов предавать себя ради принятия.",
            "61_80": "Сильная ориентация на мнение референтной группы.",
            "81_100": "Тотальное подстраивание (People Pleasing) ради гарантированного принятия."
        },
        "direct_evidence_tags": ["approval_seeking", "belonging_need", "conformity"],
        "indirect_evidence_tags": ["fear_of_exclusion"],
        "negative_evidence_tags": ["lone_wolf", "indifferent_to_opinion"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "VISIBILITY", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P1_APPROVAL_LOOP", "P4_SELF_SILENCING"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D07_INTERNAL_LOCUS_OF_EVALUATION", "D32_REJECTION_SENSITIVITY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D34",
        "code": "D34_CONFLICT_TOLERANCE",
        "domain": "DOMAIN_F_INTERPERSONAL",
        "name_en": "Conflict Tolerance",
        "name_ru": "Толерантность к конфликтам",
        "definition": "Способность выдерживать прямое столкновение интересов, чужую злость и напряжение в коммуникации без сбегания или уступчивости.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Избегание конфликтов любой ценой. 'Мир любой ценой', сглаживание углов в ущерб себе.",
            "resource": "Дипломатичность, предотвращение острых скандалов, удержание контакта.",
            "cost": "Накопление скрытого раздражения, потеря позиций, предательство собственных интересов."
        },
        "high_pole": {
            "description": "Комфорт в прямом противостоянии. Способность спокойно отстаивать позицию в горячем споре.",
            "resource": "Эффективные переговоры, защита ресурсов, прояснение скрытых нарывов.",
            "cost": "При крайних значениях — конфликтность, провоцирование ссор на пустом месте."
        },
        "scoring_anchors": {
            "0_20": "Панический страх любых ссор. Мгновенная капитуляция при нажиме.",
            "21_40": "Избегает острых тем. Старается перевести конфликт в скрытую форму.",
            "41_60": "Способен вступать в конфликт, если задеты принципиальные вещи.",
            "61_80": "Спокойно переносит чужую агрессию и выдерживает открытый разговор.",
            "81_100": "Абсолютный комфорт в открытых противостояниях. Использование конфликта как инструмента."
        },
        "direct_evidence_tags": ["conflict_avoidance", "confrontation_readiness", "fear_of_anger"],
        "indirect_evidence_tags": ["passive_aggression"],
        "negative_evidence_tags": ["direct_confrontation", "healthy_argumentation"],
        "exclusion_tags": [],
        "relevant_contexts": ["CONFLICT", "RELATIONSHIPS", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P4_SELF_SILENCING"],
        "related_conflicts": ["C1_AUTHENTICITY_VS_ACCEPTANCE"],
        "related_dimensions": ["D31_BOUNDARY_FLEXIBILITY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D35",
        "code": "D35_VISIBILITY_TOLERANCE",
        "domain": "DOMAIN_F_INTERPERSONAL",
        "name_en": "Visibility Tolerance",
        "name_ru": "Толерантность к видимости (Страх быть увиденным)",
        "definition": "Готовность предъявлять себя, свои результаты и свое мнение публике, быть объектом чужого внимания и оценки.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Страх сцены, проявляемости и чужих глаз. Желание 'быть невидимым' и безопасным.",
            "resource": "Защита от чужой зависти и токсичности, скромность, глубокая работа за кулисами.",
            "cost": "Невидимость для клиентов/работодателей, упущенные чеки, работа на чужие бренды."
        },
        "high_pole": {
            "description": "Комфорт под софитами. Органичное принятие публичности, выступления, ведение соцсетей.",
            "resource": "Высокий личный бренд, привлечение ресурсов, яркий авторитет.",
            "cost": "Риск нарциссической зависимости от внимания и потери интимной жизни."
        },
        "scoring_anchors": {
            "0_20": "Панический страх публичности. Страх выложить пост или показать лицо.",
            "21_40": "Проявляемость требует огромных усилий и преодоления сильного стыда.",
            "41_60": "Проявляется по необходимости (в профессии), но не ищет лишней славы.",
            "61_80": "Легко и с удовольствием проявляется на публике.",
            "81_100": "Яркий публичный профиль. Внимание является источником драйва."
        },
        "direct_evidence_tags": ["fear_of_being_seen", "public_speaking_fear", "social_media_hiding"],
        "indirect_evidence_tags": ["underpricing_services"],
        "negative_evidence_tags": ["stage_comfort", "self_promotion"],
        "exclusion_tags": [],
        "relevant_contexts": ["VISIBILITY", "WORK", "ACHIEVEMENT"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P4_SELF_SILENCING"],
        "related_conflicts": ["C3_VISIBILITY_VS_PROTECTION"],
        "related_dimensions": ["D32_REJECTION_SENSITIVITY", "D05_SELF_CRITICISM"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D36",
        "code": "D36_HYPER_INDEPENDENCE",
        "domain": "DOMAIN_F_INTERPERSONAL",
        "name_en": "Hyper-Independence",
        "name_ru": "Гиперавтономия (Запрет на уязвимость)",
        "definition": "Установка 'Я должен справиться сам', отказ от помощи, поддержки и прошения об одолжении, восходящий к контрзависимости.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Здоровая взаимозависимость. Легкость в обращении за помощью, умение опираться на других.",
            "resource": "Быстрое решение проблем через синергию, возможность быть слабым и согретым.",
            "cost": "При крайней степени — зависимое поведение и перекладывание задач на чужие плечи."
        },
        "high_pole": {
            "description": "Запрет на прошение о помощи. Восприятие любой опираемости на других как смертельной опасности.",
            "resource": "Полная автономность, выживаемость в одиночку, ни от кого не зависит.",
            "cost": "Хроническое одиночество, неспособность делегировать, истощение от того, что 'все на мне'."
        },
        "scoring_anchors": {
            "0_20": "Легкая и здоровая опора на окружение.",
            "21_40": "Обращается за помощью без особых проблем, если задача сложная.",
            "41_60": "Предпочитает делать сам, но при сильной нагрузке может попросить.",
            "61_80": "Тяжело просить о помощи. Воспринимает это как слабость.",
            "81_100": "Тотальный контрзависимый блок. Скорее рухнет от истощения, чем попросит ручку."
        },
        "direct_evidence_tags": ["asking_for_help_inability", "counter_dependence", "self_reliance_obsession"],
        "indirect_evidence_tags": ["loneliness", "inability_to_delegate"],
        "negative_evidence_tags": ["interdependence", "easy_asking"],
        "exclusion_tags": [],
        "relevant_contexts": ["RELATIONSHIPS", "WORK", "STRESS"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": ["C6_AUTHENTICITY_VS_PROTECTION"],
        "related_dimensions": ["D08_ACTION_AGENCY", "D31_BOUNDARY_FLEXIBILITY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },

    # DOMAIN G - ENERGY / REGULATION
    {
        "id": "D37",
        "code": "D37_STRESS_BASELINE",
        "domain": "DOMAIN_G_ENERGY",
        "name_en": "Stress Baseline",
        "name_ru": "Фоновый уровень стресса",
        "definition": "Хронический уровень физиологического и психоэмоционального напряжения, в котором находится человек постоянно.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Расслабленное фоновое состояние. Низкая частота пульса, отсутствие зажимов в теле.",
            "resource": "Высокий запас прочности, ясный ум, отличное качество сна.",
            "cost": "Может отсутствовать мобилизация в ситуациях, где нужен короткий рывок."
        },
        "high_pole": {
            "description": "Жизнь на взводе. Фоновая тревога, телесные зажимы, взвинченность даже в покое.",
            "resource": "Мгновенная готовность к бою/бегству.",
            "cost": "Разрушение здоровья, риск выгорания, вспышки раздражительности."
        },
        "scoring_anchors": {
            "0_20": "Глубокий базовый покой. Отсутствие фонового напряжения.",
            "21_40": "Умеренный покой с легкими всплесками стресса по делу.",
            "41_60": "Средний фоновый уровень. Стресс ощущается регулярным фоном.",
            "61_80": "Высокое постоянное напряжение. Трудно полностью расслабиться.",
            "81_100": "Хронический экстремальный дистресс. Ощущение постоянной угрозы."
        },
        "direct_evidence_tags": ["chronic_anxiety", "body_tension", "sleep_disturbances"],
        "indirect_evidence_tags": ["irritability", "caffeine_reliance"],
        "negative_evidence_tags": ["relaxed_state", "deep_rest"],
        "exclusion_tags": [],
        "relevant_contexts": ["STRESS", "SELF_RELATION"],
        "context_modifiers": {},
        "state_sensitivity": "HIGH",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": ["C4_ACHIEVEMENT_VS_SELF_PRESERVATION"],
        "related_dimensions": ["D40_HYPERAROUSAL_TENDENCY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D38",
        "code": "D38_RECOVERY_SPEED",
        "domain": "DOMAIN_G_ENERGY",
        "name_en": "Physiological & Mental Recovery Speed",
        "name_ru": "Скорость восстановления ресурсов",
        "definition": "Способность нервной системы и психики восполнять потраченную энергию после нагрузок или кризисов.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Медленное восстановление. Даже небольшая нагрузка требует длительного лежания пластом.",
            "resource": "Глубокая вынужденная пауза, защищающая от перегрузок.",
            "cost": "Низкая пропускная способность по задачам, выпадение из процесса надолго."
        },
        "high_pole": {
            "description": "Быстрая подзарядка. Час хорошего сна или прогулки полностью возвращают в строй.",
            "resource": "Огромный суточный объем работы, высокая выносливость.",
            "cost": "Риск пропустить момент, когда ресурсы действительно закончатся на фундаментальном уровне."
        },
        "scoring_anchors": {
            "0_20": "Очень тяжелое и долгое восстановление после любой нагрузки.",
            "21_40": "Нужда в частых длинных паузах для поддержания рабочей формы.",
            "41_60": "Стандартная скорость. Выходные возвращают ресурс за неделю.",
            "61_80": "Быстрая перезагрузка. Хороший контакт с восстанавливающими практиками.",
            "81_100": "Невероятный уровень регенерации. Минимальное время на отдых."
        },
        "direct_evidence_tags": ["stamina", "recharge_efficiency", "burnout_recovery"],
        "indirect_evidence_tags": ["energy_fluctuations"],
        "negative_evidence_tags": ["chronic_fatigue", "sluggishness"],
        "exclusion_tags": ["medical_conditions"],
        "relevant_contexts": ["STRESS", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "HIGH",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D37_STRESS_BASELINE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D39",
        "code": "D39_SOMATIC_DISCONNECT",
        "domain": "DOMAIN_G_ENERGY",
        "name_en": "Somatic Disconnect",
        "name_ru": "Соматический дисконнект (Игнорирование тела)",
        "definition": "Склонность игнорировать физиологические сигналы тела (голод, усталость, боль, позывы) ради выполнения задач.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Высокая соматическая чуткость. Тело расценивается как главный партнер.",
            "resource": "Профилактика заболеваний, отсутствие переутомления, телесная мудрость.",
            "cost": "Может мешать в ситуациях, где нужно перетерпеть физический дискомфорт ради прорыва."
        },
        "high_pole": {
            "description": "Использование тела как функция/транспортное средство. Запрет на признание усталости.",
            "resource": "Способность работать на износ, делать результат через 'не могу'.",
            "cost": "Внезапные тяжелые болезни как единственный способ тела остановить человека."
        },
        "scoring_anchors": {
            "0_20": "Глубокая связь с каждым сигналом тела. Мгновенный отклик на усталость.",
            "21_40": "Слышит тело, но иногда может отложить отдых на пару часов.",
            "41_60": "Замечает усталость, когда она уже сильно выражена.",
            "61_80": "Игнорирует боли и усталость до последнего момента.",
            "81_100": "Полный отрыв от тела. Замечает проблемы только при госпитализации."
        },
        "direct_evidence_tags": ["body_awareness_lacking", "ignoring_pain", "working_through_sickness"],
        "indirect_evidence_tags": ["sudden_illness_breakdowns"],
        "negative_evidence_tags": ["body_mindfulness", "timely_rest"],
        "exclusion_tags": [],
        "relevant_contexts": ["STRESS", "WORK", "SELF_RELATION"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": ["C4_ACHIEVEMENT_VS_SELF_PRESERVATION"],
        "related_dimensions": ["D20_EMOTIONAL_AWARENESS", "D37_STRESS_BASELINE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D40",
        "code": "D40_HYPERAROUSAL_TENDENCY",
        "domain": "DOMAIN_G_ENERGY",
        "name_en": "Hyperarousal Tendency",
        "name_ru": "Склонность к гипервозбуждению",
        "definition": "Легкость перехода нервной системы в состояние аффекта, паники или ярости от незначительных триггеров.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Хладнокровие, флегматичность, высокая реактивная тормозная способность.",
            "resource": "Устойчивость в чрезвычайных ситуациях, отсутствие импульсивных действий.",
            "cost": "Может казаться заторможенным или эмоционально плоским."
        },
        "high_pole": {
            "description": "Взрывной характер, реактивность 'с пол-оборота', легкий занос в аффект.",
            "resource": "Яркая эмоциональная энергия, способность к мгновенной мобилизации.",
            "cost": "Нарушение коммуникаций, импульсивные разрушительные решения, истощение."
        },
        "scoring_anchors": {
            "0_20": "Абсолютное олимпийское спокойствие. Вывести из себя невозможно.",
            "21_40": "Высокий порог закипания. Редко взрывается.",
            "41_60": "Средняя реактивность. Реагирует эмоционально только на близкие триггеры.",
            "61_80": "Легко заводится. Быстрый переход от покой в яркую эмоцию.",
            "81_100": "Пороховая бочка. Мгновенные аффективные вспышки."
        },
        "direct_evidence_tags": ["reactivity", "short_fuse", "affect_tendency"],
        "indirect_evidence_tags": ["impulsive_outbursts"],
        "negative_evidence_tags": ["calm_under_fire", "emotional_stability"],
        "exclusion_tags": [],
        "relevant_contexts": ["CONFLICT", "STRESS"],
        "context_modifiers": {},
        "state_sensitivity": "HIGH",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D37_STRESS_BASELINE", "D22_EMOTIONAL_TOLERANCE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },

    # DOMAIN H - COGNITIVE FLEXIBILITY / MEANING
    {
        "id": "D41",
        "code": "D41_MEANING_MAKING",
        "domain": "DOMAIN_H_COGNITION",
        "name_en": "Meaning Making",
        "name_ru": "Осмысление опыта (Поиск смыслов)",
        "definition": "Способность находить ценностный смысл, уроки и точку роста даже в тяжелых кризисах и испытаниях.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Восприятие страданий и неучач как бессмысленной несправедливости или хаоса.",
            "resource": "Отсутствие иллюзий, реалистичность, отсутствие стремления оправдать насилие/боль 'уроками судьбы'.",
            "cost": "Экзистенциальное бессилие, ощущением бессмысленности происходящего."
        },
        "high_pole": {
            "description": "Органичное умение извлекать смыслы: 'Для чего мне эта ситуация?'.",
            "resource": "Посттравматический рост, колоссальная душевная стойкость, выработка глубокой мудрости.",
            "cost": "Может превращаться в 'токсичный позитив' и духовный избегание реального проживания боли."
        },
        "scoring_anchors": {
            "0_20": "Абсолютный экзистенциальный вакуум. Любая боль воспринимается как бессмысленный удар.",
            "21_40": "Трудно находит смысл в провалах, скатывается в вопрос 'За что мне это?'.",
            "41_60": "Со временем способен отрефлексировать кризис и понять его ценность.",
            "61_80": "Быстро находит точки роста в испытаниях.",
            "81_100": "Глубокая философская трансформация любого опыта в личную силу."
        },
        "direct_evidence_tags": ["post_traumatic_growth", "finding_purpose", "lesson_extraction"],
        "indirect_evidence_tags": ["existential_resilience"],
        "negative_evidence_tags": ["meaninglessness", "victim_thinking"],
        "exclusion_tags": [],
        "relevant_contexts": ["FAILURE", "STRESS", "SELF_RELATION"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D13_RECOVERY_AFTER_FAILURE", "D42_PSYCHOLOGICAL_FLEXIBILITY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D42",
        "code": "D42_PSYCHOLOGICAL_FLEXIBILITY",
        "domain": "DOMAIN_H_COGNITION",
        "name_en": "Psychological Flexibility",
        "name_ru": "Психологическая гибкость (ACT-конструкт)",
        "definition": "Способность осознанно быть в настоящем моменте со всеми мыслями/чувствами и продолжать действовать в соответствии со своими ценностями.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Психологическая ригидность: слияние с мыслями, сбегание от чувств, отказ от ценностей ради избегания боли.",
            "resource": "Жесткость установок защищает от сомнений.",
            "cost": "Психологические тупики, зависимость поведения от мозаики случайных мыслей."
        },
        "high_pole": {
            "description": "Осознанное разотождествление с внутренним радио (дефузия), опора на ценностный вектор.",
            "resource": "Свобода выбора реакции, прохождение через любые эмоциональные штормы.",
            "cost": "Требует постоянной высокого уровня осознанности."
        },
        "scoring_anchors": {
            "0_20": "Полное слияние со своими негативными мыслями. 'Я и есть моя тревога'.",
            "21_40": "Мысли и чувства легко блокируют ценностное поведение.",
            "41_60": "Иногда удается сделать шаг вопреки страху, но слияние еще частое.",
            "61_80": "Хорошая психологическая гибкость. Принимает чувства и идет к цели.",
            "81_100": "Мастерское владение расцеплением (defusion) и понятный ценностный компас."
        },
        "direct_evidence_tags": ["cognitive_defusion", "values_based_action", "acceptance_capacity"],
        "indirect_evidence_tags": ["psychological_rigidity"],
        "negative_evidence_tags": ["fusion_with_thoughts", "experiential_avoidance"],
        "exclusion_tags": [],
        "relevant_contexts": ["UNCERTAINTY", "STRESS", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D24_EXPERIENTIAL_AVOIDANCE", "D12_BEHAVIORAL_FLEXIBILITY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D43",
        "code": "D43_PERSPECTIVE_TAKING",
        "domain": "DOMAIN_H_COGNITION",
        "name_en": "Perspective Taking",
        "name_ru": "Децентрация (Взгляд со стороны)",
        "definition": "Способность посмотреть на ситуацию глазами другого человека или с позиции беспристрастного третьего наблюдателя (Self-as-Context).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Эгоцентризм восприятия. 'Существует только моя правда и мой вариант происходящего'.",
            "resource": "Уверенность в своей правоте, отсутствие сомнений при напоре.",
            "cost": "Неспособность договориться, разрушение близких отношений, слепота к аргументам."
        },
        "high_pole": {
            "description": "Способность легко встать в чужие тапки и увидеть полную картину поля.",
            "resource": "Мастерство переговоров, разрешение конфликтов, глубокая эмпатия.",
            "cost": "Может размывать собственную позицию: 'все по-своему правы, где же я?'."
        },
        "scoring_anchors": {
            "0_20": "Абсолютный эгоцентризм. Иные точки зрения искренне считаются бредом или враждой.",
            "21_40": "С трудом допускает чужую правоту в споре.",
            "41_60": "Способен понять оппонента, если остынет эмоционально.",
            "61_80": "Хорошая децентрация. Спокойно видит позицию другой стороны.",
            "81_100": "Виртуозный взгляд с высоты птичьего полета на любые конфликты."
        },
        "direct_evidence_tags": ["empathy_in_perspective", "decentralization", "seeing_other_side"],
        "indirect_evidence_tags": ["conflict_resolution_skill"],
        "negative_evidence_tags": ["egocentrism", "my_way_or_highway"],
        "exclusion_tags": [],
        "relevant_contexts": ["CONFLICT", "RELATIONSHIPS"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D17_AMBIGUITY_TOLERANCE"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D44",
        "code": "D44_TEMPORAL_FOCUS",
        "domain": "DOMAIN_H_COGNITION",
        "name_en": "Temporal Focus",
        "name_ru": "Временная ориентация",
        "definition": "Преобладающая ментальная локация внимания: в прошлом (ностальгия/сожаления), настоящем (здесь и сейчас) или будущем (планы/тревога).",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Застревание в прошлом (сожаления, травмы) или гиперопека будущего (тревожное ожидание).",
            "resource": "Уважение к опыту или прогностическая функция.",
            "cost": "Утечка жизни мимо настоящего момента."
        },
        "high_pole": {
            "description": "Преобладание контакта с настоящим моментом при здоровом использовании прошлого и будущего как инструментов.",
            "resource": "Высокое качество жизни, заземленность, ясность мышления.",
            "cost": "При экстремальном уходе в настоящее — риск игнорирования долгосрочных перспектив."
        },
        "scoring_anchors": {
            "0_20": "Тотальное застревание в прошлом или в тревоге о будущем.",
            "21_40": "Настоящий момент проносится мимо. Внимание всегда 'не здесь'.",
            "41_60": "Умеет возвращаться в 'здесь и сейчас', но фоново улетает в мысли.",
            "61_80": "Хороший контакт с настоящим моментом.",
            "81_100": "Глубокая заземленность и полное присутствие в текущей секунде."
        },
        "direct_evidence_tags": ["present_moment_focus", "stuck_in_past", "future_anxiety"],
        "indirect_evidence_tags": ["mindfulness"],
        "negative_evidence_tags": ["absent_mindedness", "nostalgia_overdrive"],
        "exclusion_tags": [],
        "relevant_contexts": ["SELF_RELATION", "STRESS"],
        "context_modifiers": {},
        "state_sensitivity": "MEDIUM",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D19_COGNITIVE_OVERPROCESSING"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D45",
        "code": "D45_DOGMA_ATTACHMENT",
        "domain": "DOMAIN_H_COGNITION",
        "name_en": "Dogma Attachment",
        "name_ru": "Привязанность к догмам (Долженствования)",
        "definition": "Степень жесткости внутренних 'Я должен', 'Они должны', 'Мир обязан'. Тирания долга по Карен Хорни.",
        "construct_type": "BIPOLAR",
        "score_direction": "LOW_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Замена жесткого 'должен' на гибкое 'я выбираю' или 'мне бы хотелось'.",
            "resource": "Свобода от чувства вины и обиды на мир, психологическая легкость.",
            "cost": "Может показаться необязательностью при недостаточности дисциплины."
        },
        "high_pole": {
            "description": "Свод бескомпромиссных правил о том, как ДОЛЖНО быть. Негодование при их нарушении.",
            "resource": "Высокая нормативность, следование моральным кодексам.",
            "cost": "Хронический праведный гнев, обида на несовершенство мира, чувство вины перед собой."
        },
        "scoring_anchors": {
            "0_20": "Абсолютно гибкое восприятие норм. Нет концепции жесткого 'должен'.",
            "21_40": "Минимальное количество обязательных правил. Преобладают личные предпочтения.",
            "41_60": "Есть список правил, но способен делать исключения без боли.",
            "61_80": "Высокая догматичность. Разочарование при нарушении ожиданий.",
            "81_100": "Тотальная тирания долга. Непрерывный гнев или вина из-за несоответствия идеалу."
        },
        "direct_evidence_tags": ["should_statements", "rigidity_of_rules", "moralizing"],
        "indirect_evidence_tags": ["righteous_anger", "guilt"],
        "negative_evidence_tags": ["flexibility_of_beliefs", "acceptance_of_flaws"],
        "exclusion_tags": [],
        "relevant_contexts": ["SELF_RELATION", "RELATIONSHIPS", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": ["P5_PERFORMANCE_SELF_WORTH"],
        "related_conflicts": [],
        "related_dimensions": ["D05_SELF_CRITICISM", "D42_PSYCHOLOGICAL_FLEXIBILITY"],
        "interpretation_rules": [],
        "exclusion_rules": []
    },
    {
        "id": "D46",
        "code": "D46_COGNITIVE_REFRAMING",
        "domain": "DOMAIN_H_COGNITION",
        "name_en": "Cognitive Reframing",
        "name_ru": "Когнитивный рефрейминг",
        "definition": "Способность произвольно менять угол зрения на проблему, находя в ней новые смыслы, выгоды и альтернативные трактовки.",
        "construct_type": "BIPOLAR",
        "score_direction": "HIGH_MEANS_MORE_CONSTRUCT",
        "low_pole": {
            "description": "Фиксация на первой (обычно негативной) интерпретации события. Застревание в тупиковой рамке.",
            "resource": "Реалистичность оценки ущерба, отсутствие преждевременного успокоения.",
            "cost": "Безысходность, ощущение запертости в проблеме."
        },
        "high_pole": {
            "description": "Легкость смены рамки. 'Это не проблема, это задача', 'Это не потеря, это освобождение места'.",
            "resource": "Высочайшая ментальная гибкость, оптимизм, нахождение выходов из тупиков.",
            "cost": "Может использоваться как рационализация и побег от истинной боли."
        },
        "scoring_anchors": {
            "0_20": "Абсолютная когнитивная застреваемость. Если все плохо — значит, все плохо.",
            "21_40": "С трудом видит альтернативные интерпретации событий.",
            "41_60": "Способен на рефрейминг с помощью со стороны (психолог, друг).",
            "61_80": "Самостоятельно и легко переформулирует проблемы в задачи.",
            "81_100": "Виртуозный когнитивный рефрейминг любой ситуации в считанные секунды."
        },
        "direct_evidence_tags": ["reframing_ability", "perspective_shift", "seeing_silver_lining"],
        "indirect_evidence_tags": ["problem_solving_speed"],
        "negative_evidence_tags": ["tunnel_vision", "catastrophizing"],
        "exclusion_tags": [],
        "relevant_contexts": ["STRESS", "FAILURE", "WORK"],
        "context_modifiers": {},
        "state_sensitivity": "LOW",
        "minimum_evidence": {"medium_confidence": 3, "high_confidence": 5},
        "related_patterns": [],
        "related_conflicts": [],
        "related_dimensions": ["D41_MEANING_MAKING", "D42_PSYCHOLOGICAL_FLEXIBILITY"],
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
