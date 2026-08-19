import json
import logging
from typing import Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from src.core.config import settings

logger = logging.getLogger(__name__)

# List of forbidden clinical or diagnostic terms (Section 42 & 45)
FORBIDDEN_CLINICAL_TERMS = [
    "диагноз", "клинический", "шизофрения", "депрессивное расстройство",
    "психопатология", "синдром", "травма детства", "детская травма",
    "психиатрический", "невроз", "психоз"
]

FULL_REPORT_SYSTEM_PROMPT = """
Ты — ведущий психологический архитектор и создатель отчетов системы «Инструкция к себе» V1.3.
Твоя задача — превратить строгие математические расчеты бэкенда (46 шкал личности, 37 паттернов, 12 конфликтов, 3-5 системных циклов) в глубокий, интригующий и психологически точный персональный отчет.

СТИЛЬ И СЛОГ:
- Пиши в фирменном стиле Виктора Пелевина: тонкая метафоричность, мета-ирония, интеллектуальная выверенность, глубинный взгляд на механизмы человеческого восприятия, эго и защит.
- Избегай сухой академичности, инфантильности, эзотерики и дешевой поп-психологии.
- Текст должен ощущаться как парадоксальное, но невероятно точное откровение о том, как устроена персональная «операционная система» человека.

СТРОГИЕ ОГРАНИЧЕНИЯ:
1. Запрещено придумывать незафиксированные бэкендом данные, диагнозы или «детские травмы».
2. Никакого медицинского или психиатрического языка (слова «диагноз», «депрессия», «синдром» под запретом).
3. Вернуть ответ СТРОГО в формате JSON с 12 главами отчета (chapters), 10 персональными правилами (personal_rules) и итоговым синтезом (final_synthesis).
"""


def validate_llm_safety_and_schema(report_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate LLM JSON response for safety rules and required fields.
    """
    raw_str = json.dumps(report_data, ensure_ascii=False).lower()
    
    # 1. Check for forbidden clinical terms
    for term in FORBIDDEN_CLINICAL_TERMS:
        if term in raw_str:
            return False, f"Forbidden clinical term detected in report: '{term}'"

    # 2. Check required top-level chapters and fields
    required_keys = ["chapters", "personal_rules", "final_synthesis"]
    for key in required_keys:
        if key not in report_data:
            return False, f"Missing required top-level key: '{key}'"

    if not isinstance(report_data.get("personal_rules"), list) or len(report_data.get("personal_rules")) < 5:
        return False, "Personal rules must contain at least 5-10 actionable rules"

    return True, None


async def generate_full_report_llm(input_package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate FULL synthesis report via OpenAI API (gpt-4o / gpt-4o-mini).
    Uses structured JSON mode.
    """
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("YOUR_"):
        # Mock fallback for dev mode without active API key
        return get_fallback_mock_full_report(input_package)

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    user_prompt = f"Рассчитанный профиль пользователя для генерации отчета:\n{json.dumps(input_package, ensure_ascii=False)}"

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FULL_REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=4000
        )

        content = response.choices[0].message.content
        report_json = json.loads(content)

        is_valid, err = validate_llm_safety_and_schema(report_json)
        if not is_valid:
            logger.error(f"LLM validation failed: {err}. Using structured fallback.")
            return get_fallback_mock_full_report(input_package)

        return report_json

    except Exception as e:
        logger.exception("Error communicating with OpenAI API")
        return get_fallback_mock_full_report(input_package)


def get_fallback_mock_full_report(input_package: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback deterministic mock report generator in Pelevin literary style."""
    return {
        "meta": {
            "version": "1.3",
            "generation_mode": "FULL_FALLBACK",
            "language": "ru"
        },
        "chapters": {
            "ch01_overview": "Ваша внутреннее «Я» устроено как изысканный проекционный аппарат: вы искренне стремитесь к безусловной автономии, но продолжаете сверять собственный маршрут по отражениям в чужих глазах.",
            "ch02_drivers": "Главное топливо вашей системы — сочетание потребности в независимости и поиска экзистенциального смысла, побеждающее бытовой комфорт.",
            "ch03_self_worth": "Внутренний контролер выстроил строгую таможню: самооценка выдается в кредит под залог свежих достижений, а не предоставляется как базовая реальность.",
            "ch04_emotions": "Эмоциональный спектр бережно фильтруется разумом. Вы предпочитаете мгновенно объяснять себе чувство вместо того, чтобы просто отдать ему место.",
            "ch05_relationships": "Близость воспринимается одновременно как высшая ценность и как потенциальная угроза суверенитету. Вы виртуозно держите дистанцию комфорта.",
            "ch06_decisions": "Перед лицом неопределенности ваша система запускает непрерывный просчет сценариев, пытаясь застраховать виртуальное будущее от любой цены ошибки.",
            "ch07_action": "Цепочка «импульс → действие» иногда буксует в точке ожидания полных гарантий. Главный секрет движения — шагать до того, как туман рассеется.",
            "ch08_visibility": "Желание быть увиденным соревнуется с опасением быть оцененным. Вы проявляетесь точно, но дозированно.",
            "ch09_money": "Финансы для вас — не мерило роскоши, а главный индикатор периметра безопасности и индивидуальной свободы.",
            "ch10_stress": "Под нагрузкой ваша система уплотняет контроль и переходит в режим автономного симулятора, минимизируя внешние контакты.",
            "ch11_cycles": "Ключевой замкнутый цикл: высокий старт → стремление к идеальному результату → нарастание ценности ошибки → временное торможение.",
            "ch12_instruction": "Главная персональная инструкция: разрешить реальности быть неидеальной до того, как вы решите сделать первый шаг."
        },
        "personal_rules": [
            "1. Замечать паузу между импульсом дискомфорта и попыткой срочно сменить декорации.",
            "2. Оценивать решения по критерию продвижения к ценностям, а не отсутствия тревоги.",
            "3. Разделять собственное отношение к себе и сиюминутные проекции наблюдателей.",
            "4. Вводить правило первого 15-минутного действия без требования полных гарантий от матрицы.",
            "5. Прямо обозначать личные границы до того, как внутреннее раздражение станет капиталом.",
            "6. Фиксировать фактический результат задачи до включения дежурного критика.",
            "7. Давать себе право на неидеальный выбор без попытки удержать все упущенные альтернативы.",
            "8. Использовать регулярные паузы перезагрузки при высокой нагрузке на систему.",
            "9. Отслеживать защитную функцию тотального контроля при росте внешней неопределенности.",
            "10. Опираться на внутренние ценностные ориентиры при выборе нового маршрута."
        ],
        "final_synthesis": {
            "top_resource": "Адаптивная субъектность и способность действовать сквозь туман.",
            "top_trap": "Требование гарантий от реальности до первого шага.",
            "top_leverage": "Переход к действию на основе 70% информации."
        }
    }
