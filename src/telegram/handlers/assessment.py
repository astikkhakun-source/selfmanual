import json
import os
import uuid
import logging
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from src.db.base import AsyncSessionLocal
from src.services.config_loader import (
    CORE_BASE_ITEMS, VFC_PAIRS, CONFIG_DIR
)
from src.services.assessment import (
    get_or_create_user, get_active_session, start_new_session,
    save_answer, get_next_question_for_session, get_session_answers_map
)
from src.domain.scoring.core_engine import calculate_core_signals, evaluate_core_conflicts
from src.domain.scoring.scales import calculate_primary_scales
from src.domain.scoring.patterns import evaluate_full_patterns
from src.domain.scoring.conflicts import evaluate_full_conflicts
from src.services.payment import create_prodamus_payment_link
from src.services.llm_report import generate_full_report_llm
from src.services.pdf_export import generate_pdf_report
from src.telegram.keyboards import (
    get_likert_keyboard, get_vfc_keyboard, get_paywall_keyboard, get_consent_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handler for /start command."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            language=message.from_user.language_code or "ru"
        )
        
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)

        # Show Onboarding / Consent first
        if session.phase == "CONSENT_PENDING":
            welcome_text = (
                "<b>Приветствуем в системе «Инструкция к себе» V1.3</b>\n\n"
                "Это двухступенчатая система психологической самодиагностики.\n"
                "Первый этап (CORE) — короткая бесплатная диагностика из 24 обязательных и нескольких адаптивных вопросов.\n\n"
                "<i>Нажимая кнопку ниже, вы соглашаетесь на обработку ответов в целях психологической самодиагностики.</i>"
            )
            await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_consent_keyboard())
            return

        await send_next_question(message, db, session)


@router.callback_query(F.data == "accept_consent")
async def cb_accept_consent(callback: CallbackQuery):
    """Handle consent agreement."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id
        )
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)

        session.phase = "CORE_IN_PROGRESS"
        await db.commit()

        await callback.answer("Согласие принято!")
        await send_next_question(callback.message, db, session)


@router.callback_query(F.data.startswith("ans:"))
async def cb_answer_likert(callback: CallbackQuery):
    """Handle Likert 1-7 answer selection."""
    parts = callback.data.split(":")
    if len(parts) < 4:
        await callback.answer()
        return

    q_id = parts[1]
    raw_answer = int(parts[2])
    client_event_id = parts[3]

    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id
        )
        session = await get_active_session(db, user.id)
        if not session:
            await callback.answer("Сессия не найдена. Нажмите /start.")
            return

        phase = session.phase
        await save_answer(
            db,
            session_id=session.id,
            question_id=q_id,
            raw_answer=raw_answer,
            phase=phase,
            client_event_id=client_event_id
        )

        await callback.answer(f"Ответ {raw_answer} сохранен.")
        await send_next_question(callback.message, db, session, edit_existing=True)


@router.callback_query(F.data.startswith("vfc:"))
async def cb_answer_vfc(callback: CallbackQuery):
    """Handle VFC 2-choice value selection."""
    parts = callback.data.split(":")
    if len(parts) < 4:
        await callback.answer()
        return

    vfc_id = parts[1]
    selected_val = parts[2]
    client_event_id = parts[3]

    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id
        )
        session = await get_active_session(db, user.id)
        if not session:
            await callback.answer("Сессия не найдена.")
            return

        await save_answer(
            db,
            session_id=session.id,
            question_id=vfc_id,
            raw_answer=1 if selected_val == "autonomy" else 2,
            phase="VFC",
            client_event_id=client_event_id,
            selected_value=selected_val
        )

        await callback.answer("Выбор сохранен.")
        await send_next_question(callback.message, db, session, edit_existing=True)


async def send_next_question(message: Message, db, session, edit_existing: bool = False):
    """Determine next question and render to Telegram chat."""
    next_q = await get_next_question_for_session(db, session)

    if not next_q:
        if session.phase == "CORE_READY":
            await render_free_core_report(message, db, session)
        elif session.phase == "FULL_ASSESSMENT_COMPLETED":
            await render_full_report_and_pdf(message, db, session)
        return

    q_id = next_q["question_id"]
    client_event_id = str(uuid.uuid4())[:12]
    progress = next_q.get("total_progress", 0)
    target = next_q.get("target_total", 24)

    # Load question text from json config
    q_file = os.path.join(CONFIG_DIR, "questions_v1_2.json")
    with open(q_file, "r", encoding="utf-8") as f:
        questions_map = json.load(f)

    q_info = questions_map.get(q_id, {})
    q_text = q_info.get("text_ru", f"Вопрос {q_id}")

    if next_q["phase"] == "VFC":
        vfc_data = next_q.get("vfc_data") or {"value_a": "A", "text_a": "Вариант А", "value_b": "B", "text_b": "Вариант Б"}
        text = (
            f"<b>Вопрос {progress + 1} из {target} (Выбор приоритета):</b>\n\n"
            f"Что для вас представляет большую ценность?"
        )
        markup = get_vfc_keyboard(q_id, vfc_data, client_event_id)
    else:
        text = (
            f"<b>Вопрос {progress + 1} из {target}:</b>\n\n"
            f"«{q_text}»\n\n"
            f"<i>1 — Полностью не согласен ... 7 — Полностью согласен</i>"
        )
        markup = get_likert_keyboard(q_id, client_event_id)

    if edit_existing:
        try:
            await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
            return
        except Exception:
            pass

    await message.answer(text, parse_mode="HTML", reply_markup=markup)


async def render_free_core_report(message: Message, db, session):
    """Render 6-screen FREE report and personalized Paywall."""
    answers_map = await get_session_answers_map(db, session.id)
    signals = calculate_core_signals(answers_map)
    conflicts, top_conflict_id, report_mode = evaluate_core_conflicts(signals)

    top_cf_text = conflicts.get(top_conflict_id, {}).get("headline", "Ты ищешь собственный баланс.") if top_conflict_id else "Ты ищешь баланс между автономией и предсказуемостью."

    report_text = (
        "<b>БЕСПЛАТНЫЙ ОТЧЕТ CORE (Диагностика системы)</b>\n\n"
        "<b>Ты в двух абзацах:</b>\n"
        "Ваша первичная конфигурация показывает сочетание высокого стремления к независимости и чувствительности к внешнему признанию.\n\n"
        f"<b>Главный инсайт:</b>\n<i>«{top_cf_text}»</i>\n\n"
        "<b>Граница знания:</b>\n"
        "Короткая диагностика показала наиболее заметную конфигурацию. Но мы видим ЧТО, но пока не знаем ПОЧЕМУ.\n\n"
        "───────────────\n"
        "<b>ЭТО БЫЛА НЕ ИНСТРУКЦИЯ. ЭТО БЫЛА ПЕРВАЯ СТРАНИЦА.</b>\n"
        "Полная «Инструкция к себе» покажет, как все 46 аспектов вашей личности связаны между собой."
    )

    payment_url = create_prodamus_payment_link(user_id=session.user_id, session_id=session.id)
    markup = get_paywall_keyboard(payment_url)

    await message.answer(report_text, parse_mode="HTML", reply_markup=markup)


async def render_full_report_and_pdf(message: Message, db, session):
    """Generate FULL report via LLM and deliver PDF to Telegram chat."""
    answers_map = await get_session_answers_map(db, session.id)
    scales = calculate_primary_scales(answers_map)
    patterns = evaluate_full_patterns(scales)
    conflicts = evaluate_full_conflicts(scales)

    input_package = {
        "meta": {"version": "1.3"},
        "primary_scales": scales,
        "patterns": patterns,
        "conflicts": conflicts
    }

    status_msg = await message.answer("🔄 <i>Система генерирует ваш персональный отчёт и PDF-инструкцию...</i>", parse_mode="HTML")

    # Generate LLM Report & PDF
    llm_report = await generate_full_report_llm(input_package)

    rules_text = "\n".join([f"• {r}" for r in llm_report.get("personal_rules", [])[:5]])
    full_text = (
        "<b>ПОЛНАЯ ИНСТРУКЦИЯ К СЕБЕ V1.3 ГОТОВА!</b>\n\n"
        f"<b>Ключевые правила обращения с собой:</b>\n{rules_text}\n\n"
    )

    try:
        pdf_path = generate_pdf_report(session.id, llm_report)
        full_text += "📄 Ваш детальный 12-страничный PDF-отчет сформирован и прикреплен ниже."
        await status_msg.edit_text(full_text, parse_mode="HTML")

        # Send PDF document directly to Telegram chat
        pdf_file = FSInputFile(pdf_path, filename=f"Инструкция_к_себе_{session.id[:8]}.pdf")
        await message.answer_document(pdf_file, caption="Ваш персональный PDF-отчет «Инструкция к себе» V1.3")
    except Exception as pdf_err:
        logger.error(f"Ошибка при генерации PDF: {pdf_err}", exc_info=True)
        full_text += "⚠️ <i>Не удалось сформировать PDF-документ, но ваш текстовый отчёт сгенерирован выше.</i>"
        await status_msg.edit_text(full_text, parse_mode="HTML")
