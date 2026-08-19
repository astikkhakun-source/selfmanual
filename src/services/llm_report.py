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
Ты — профессиональный психологический архитектор и ведущий эксперт продукта «Инструкция к себе» V1.3.
Твоя задача — трансформировать строго рассчитанные детерминированные выводы бэкенда (46 шкал, 37 паттернов, 12 конфликтов, 3-5 системных циклов) в глубокий, умный, уважительный и психологически грамотный персональный отчет на русском языке.

СТРОГИЕ ПРАВИЛА:
1. Запрещено придумывать незафиксированные бэкендом данные, диагнозы или детские травмы.
2. Никакого медицинского или психиатрического языка.
3. Соблюдать осторожность формулировок (cautious language), учитывать контрсвидетельства (counter-evidence).
4. Писать прямо, по-взрослому, без инфантилизации и без морализаторства.
5. Вернуть ответ СТРОГО в формате JSON с 12 главами отчета, 10 персональными правилами и описанием опоры/ловушки/рычага.
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
    """Fallback deterministic mock report generator when LLM API unavailable."""
    return {
        "meta": {
            "version": "1.3",
            "generation_mode": "FULL_FALLBACK",
            "language": "ru"
        },
        "chapters": {
            "ch01_overview": "Ваша архитектура личности строится на высоком стремлении к результатам и автономности...",
            "ch02_drivers": "Ключевые ценности и ориентиры вашей системы...",
            "ch03_self_worth": "Регуляция самоценности и внутренний критик...",
            "ch04_emotions": "Контакт с эмоциями и стратегии справления с дискомфортом...",
            "ch05_relationships": "Динамика близости, доверия и границ...",
            "ch06_decisions": "Процесс принятия решений и отношение к неопределенности...",
            "ch07_action": "Цепочка запуска действий и точка возможного сбоя...",
            "ch08_visibility": "Проявление в мире и публичность...",
            "ch09_money": "Отношение к финансовой безопасности и независимости...",
            "ch10_stress": "Поведение системы под нагрузкой...",
            "ch11_cycles": "Ключевые системные циклы вашей жизни...",
            "ch12_instruction": "Персональная инструкция по обращению с собой..."
        },
        "personal_rules": [
            "1. Замечать паузу между импульсом дискомфорта и желанием сменить действие.",
            "2. Оценивать решения по критерию продвижения к ценностям, а не отсутствия тревоги.",
            "3. Разделять собственное отношение к себе и оценку окружающих.",
            "4. Вводить правило первого 15-минутного действия без ожидания гарантий.",
            "5. Прямо обозначать личные границы до нарастания внутреннего раздражения.",
            "6. Фиксировать фактический результат задачи до включения внутреннего критика.",
            "7. Давать себе право на постепенный выбор без попытки удержать все альтернативы.",
            "8. Использовать регулярные паузы восстановления при высокой нагрузке.",
            "9. Отслеживать защитную функцию контроля при росте неопределенности.",
            "10. Опираться на внутренние ценности при выборе новых проектов."
        ],
        "final_synthesis": {
            "top_resource": "Адаптивная субъектность и способность действовать.",
            "top_trap": "Требование определенности до первого шага.",
            "top_leverage": "Переход к малым действиям в условиях неполной информации."
        }
    }
