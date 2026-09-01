import json
import os
import uuid
import logging
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from src.db.base import AsyncSessionLocal
from src.db.models import User, AccessEntitlement
from src.services.config_loader import (
    CORE_BASE_ITEMS, VFC_PAIRS, CONFIG_DIR, get_question_info
)
from src.services.assessment import (
    get_or_create_user, get_active_session, start_new_session,
    save_answer, get_next_question_for_session, get_session_answers_map,
    clear_session_answers_cache
)
from src.services.admin import (
    get_admin_stats, grant_user_entitlement, get_question_bank_summary, list_questions_by_phase
)
from src.domain.scoring.core_engine import calculate_core_signals, evaluate_core_conflicts
from src.domain.scoring.scales import calculate_primary_scales
from src.domain.scoring.patterns import evaluate_full_patterns
from src.domain.scoring.conflicts import evaluate_full_conflicts
from src.services.payment import create_prodamus_payment_link
from src.services.llm_report import generate_full_report_llm
from src.services.pdf_export import generate_pdf_report
from src.telegram.keyboards import (
    get_likert_keyboard, get_vfc_keyboard, get_paywall_keyboard, get_consent_keyboard,
    get_main_reply_keyboard, get_restart_confirm_keyboard,
    get_admin_paywall_keyboard, get_admin_main_reply_keyboard, get_admin_dashboard_keyboard,
    get_admin_questions_nav_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
ASSETS_IMAGES_DIR = os.path.join(ROOT_DIR, "assets", "images")


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handler for /start command with onboarding explanation and bottom menu."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            language=message.from_user.language_code or "ru"
        )
        
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)

        reply_kb = get_admin_main_reply_keyboard(is_admin=user.is_admin)
        answers_map = await get_session_answers_map(db, session.id)

        # Send 16:9 Onboarding Banner image if available
        onboarding_img = os.path.join(ASSETS_IMAGES_DIR, "onboarding.png")
        if os.path.exists(onboarding_img):
            try:
                await message.answer_photo(FSInputFile(onboarding_img))
            except Exception as img_err:
                logger.error(f"Failed to send onboarding photo: {img_err}")

        # Show Onboarding / Consent first if pending OR no answers yet
        if session.phase == "CONSENT_PENDING" or len(answers_map) == 0:
            welcome_text = (
                "👁️ <b>Добро пожаловать в систему «Инструкция к себе» V1.3!</b>\n\n"
                "Ваша личность — это не застывший набор мыслей, а сложная операционная система восприятия, постоянно редактирующая свой собственный код перед тем, как его заметит окружающая реальность.\n\n"
                "<b>📌 Как устроено исследование:</b>\n"
                "• <b>Этап 1 (CORE — Бесплатно):</b> 24 базовых + до 6 адаптивных вопросов. Алгоритм вскрывает вашу первичную архитектуру, ключевые опоры и главный парадокс вашей системы.\n"
                "• <b>Этап 2 (DEEP — Полный отчёт):</b> Анализ 46 шкал личности, 12 профильных глав и персональная 12-страничная PDF-инструкция.\n\n"
                "💡 <i>Здесь нет «правильных» или «угодных» ответов. Вы отвечаете не перед экзаменатором, а перед собственным проекционным аппаратом.</i>\n\n"
                "Нажмите кнопку ниже, чтобы начать первый этап CORE."
            )
            await message.answer(welcome_text, parse_mode="HTML", reply_markup=reply_kb)
            await message.answer("<b>Согласие на обработку данных:</b>", parse_mode="HTML", reply_markup=get_consent_keyboard())
            return

        # Resume session menu
        resume_text = (
            "👁️ <b>Вы вернулись в меню системы «Инструкция к себе» V1.3.</b>\n\n"
            f"Ваше исследование находится в процессе (отвечено вопросов: <b>{len(answers_map)}</b>).\n\n"
            "• Нажмите <b>«▶️ Продолжить диагностику»</b>, чтобы перейти к очередному вопросу.\n"
            "• Нажмите <b>«🔄 Начать заново»</b>, чтобы сбросить сессию и пройти онбординг с нуля."
        )
        await message.answer(resume_text, parse_mode="HTML", reply_markup=reply_kb)


@router.message(F.text == "▶️ Продолжить диагностику")
async def btn_continue(message: Message):
    """Handle 'Continue' button press from bottom reply menu."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, message.from_user.id, message.chat.id)
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)
        
        if session.phase == "CONSENT_PENDING":
            await message.answer("Пожалуйста, примите условия перед началом исследования.", reply_markup=get_consent_keyboard())
            return

        await send_next_question(message, db, session)


@router.message(F.text == "📊 Мой прогресс")
async def btn_progress(message: Message):
    """Show current progress."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, message.from_user.id, message.chat.id)
        session = await get_active_session(db, user.id)
        if not session:
            await message.answer("У вас нет активной сессии. Нажмите /start для начала.")
            return

        answers_map = await get_session_answers_map(db, session.id)
        count = len(answers_map)
        phase_labels = {
            "CONSENT_PENDING": "Ожидание согласия",
            "CORE_IN_PROGRESS": "Этап 1: CORE (Первичный анализ)",
            "CORE_READY": "CORE Завершён (Бесплатный отчет готов)",
            "DEEP_IN_PROGRESS": "Этап 2: DEEP (Глубокое исследование)",
            "VFC_IN_PROGRESS": "Этап 2: VFC (Ценностный выбор)",
            "FULL_ASSESSMENT_COMPLETED": "Исследование полностью завершено"
        }
        label = phase_labels.get(session.phase, session.phase)
        text = (
            f"<b>📊 Прогресс вашей системы:</b>\n\n"
            f"• <b>Статус:</b> {label}\n"
            f"• <b>Зафиксировано ответов:</b> {count}\n\n"
            f"Нажмите «▶️ Продолжить диагностику» для перехода к следующему вопросу."
        )
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "❓ О системе")
async def btn_info(message: Message):
    """Show information about system architecture."""
    info_text = (
        "<b>🧠 О системе «Инструкция к себе» V1.3</b>\n\n"
        "Система совмещает детерминированный математический скоринг 46 шкал личности и глубинный синтез смыслов.\n\n"
        "<b>Архитектура исследования:</b>\n"
        "• <b>CORE:</b> 24 базовых + адаптивные вопросы для первичного вскрытия алгоритмов восприятия.\n"
        "• <b>46 Primary Scales:</b> Измерение автономии, регуляции самоценности, близости, проявленности и работы с неопределенностью.\n"
        "• <b>10 Персональных правил:</b> Фундаментальные ориентиры взаимодействия с собственной психикой.\n"
        "• <b>PDF Export:</b> Формирование персональной инструкции формата A4."
    )
    await message.answer(info_text, parse_mode="HTML")


@router.message(F.text == "🔄 Начать заново")
@router.message(Command("reset"))
@router.message(Command("restart"))
async def btn_restart_prompt(message: Message):
    """Ask confirmation before resetting session."""
    text = (
        "⚠️ <b>Вы уверены, что хотите сбросить текущую сессию и начать заново?</b>\n\n"
        "<i>Все ответы в текущей сессии будут архивированы, и диагностика начнётся с первого вопроса.</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_restart_confirm_keyboard())


@router.callback_query(F.data == "confirm_restart")
async def cb_confirm_restart(callback: CallbackQuery):
    """Execute session reset and start fresh."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, callback.from_user.id, callback.message.chat.id)
        session = await get_active_session(db, user.id)
        if session:
            session.status = "CANCELLED"
            clear_session_answers_cache(session.id)
            await db.commit()

        new_session = await start_new_session(db, user.id)
        await callback.answer("Сессия сброшена!")
        await callback.message.edit_text("✅ <b>Сессия сброшена.</b> Диагностика начнется заново.", parse_mode="HTML")
        
        reply_kb = get_main_reply_keyboard()
        welcome_text = (
            "👁️ <b>Добро пожаловать в систему «Инструкция к себе» V1.3!</b>\n\n"
            "Ваша личность — это не застывший набор мыслей, а сложная операционная система восприятия, постоянно редактирующая свой собственный код перед тем, как его заметит окружающая реальность.\n\n"
            "<b>📌 Как устроено исследование:</b>\n"
            "• <b>Этап 1 (CORE — Бесплатно):</b> 24 базовых + до 6 адаптивных вопросов. Алгоритм вскрывает вашу первичную архитектуру, ключевые опоры и главный парадокс вашей системы.\n"
            "• <b>Этап 2 (DEEP — Полный отчёт):</b> Анализ 46 шкал личности, 12 профильных глав и персональная 12-страничная PDF-инструкция.\n\n"
            "💡 <i>Здесь нет «правильных» или «угодных» ответов. Вы отвечаете не перед экзаменатором, а перед собственным проекционным аппаратом.</i>\n\n"
            "Нажмите кнопку ниже, чтобы начать первый этап CORE."
        )

        onboarding_img = os.path.join(ASSETS_IMAGES_DIR, "onboarding.png")
        if os.path.exists(onboarding_img):
            try:
                await callback.message.answer_photo(FSInputFile(onboarding_img))
            except Exception as img_err:
                logger.error(f"Failed to send restart photo: {img_err}")

        await callback.message.answer(welcome_text, parse_mode="HTML", reply_markup=reply_kb)
        await callback.message.answer("<b>Согласие на обработку данных:</b>", parse_mode="HTML", reply_markup=get_consent_keyboard())


@router.callback_query(F.data == "cancel_restart")
async def cb_cancel_restart(callback: CallbackQuery):
    """Cancel restart."""
    await callback.answer("Сброс отменен")
    await callback.message.edit_text("❌ Сброс отменен. Вы можете продолжать диагностику.")


@router.callback_query(F.data == "accept_consent")
async def cb_accept_consent(callback: CallbackQuery):
    """Handle consent agreement."""
    await callback.answer("Согласие принято!")
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

        await send_next_question(callback.message, db, session)


@router.callback_query(F.data.startswith("ans:"))
async def cb_answer_likert(callback: CallbackQuery):
    """Handle Likert 1-7 answer selection with instant UI response."""
    # Acknowledge callback immediately so Telegram unlocks button spinner instantly (<10ms)
    await callback.answer()

    parts = callback.data.split(":")
    if len(parts) < 4:
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
            await callback.message.answer("Сессия не найдена. Нажмите /start.")
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

        await send_next_question(callback.message, db, session, edit_existing=True)


@router.callback_query(F.data.startswith("vfc:"))
async def cb_answer_vfc(callback: CallbackQuery):
    """Handle VFC 2-choice value selection with instant UI response."""
    await callback.answer()

    parts = callback.data.split(":")
    if len(parts) < 4:
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
            await callback.message.answer("Сессия не найдена.")
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

    # Fast in-memory question text lookup (no disk I/O)
    q_info = get_question_info(q_id)
    q_text = q_info.get("text_ru", f"Вопрос {q_id}")

    if next_q["phase"] == "VFC":
        vfc_data = next_q.get("vfc_data") or {"value_a": "A", "text_a": "Вариант А", "value_b": "B", "text_b": "Вариант Б"}
        text = (
            f"<b>Вопрос {progress + 1} из {target} (Выбор приоритета):</b>\n\n"
            f"Что для вас представляет большую ценность?"
        )
        markup = get_vfc_keyboard(q_id, vfc_data, client_event_id)
    elif next_q["phase"] == "CORE_ADAPTIVE":
        adaptive_idx = next_q.get("adaptive_index", 1)
        text = (
            f"<b>Уточняющий вопрос {adaptive_idx} из 6 (Адаптивный блок CORE):</b>\n\n"
            f"«{q_text}»\n\n"
            f"<i>1 — полностью не согласен\n7 — полностью согласен</i>"
        )
        markup = get_likert_keyboard(q_id, client_event_id)
    else:
        text = (
            f"<b>Вопрос {progress + 1} из {target}:</b>\n\n"
            f"«{q_text}»\n\n"
            f"<i>1 — полностью не согласен\n7 — полностью согласен</i>"
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

    # Check if user is admin or entitled
    stmt_u = select(User).where(User.id == session.user_id)
    res_u = await db.execute(stmt_u)
    user = res_u.scalar_one_or_none()

    stmt_ent = select(AccessEntitlement).where(
        AccessEntitlement.session_id == session.id,
        AccessEntitlement.status == "ACTIVE"
    )
    res_ent = await db.execute(stmt_ent)
    has_ent = res_ent.scalar_one_or_none() is not None
    is_admin = user.is_admin if user else False

    report_text = (
        "🪞 <b>БЕСПЛАТНАЯ КАРТА-ОТЧЕТ CORE (Первичная архитектура)</b>\n\n"
        "<b>Ты в двух абзацах:</b>\n"
        "Ваша первичная конфигурация показывает сочетание высокого стремления к независимости и тонкой чувствительности к внешнему признанию.\n\n"
        f"<b>Главный инсайт вашей системы:</b>\n<i>«{top_cf_text}»</i>\n\n"
        "<b>Граница знания:</b>\n"
        "Короткая диагностика показала наиболее заметную конфигурацию. Но мы видим <b>ЧТО</b> происходит в вашей операционной системе, но пока не знаем <b>ПОЧЕМУ</b>.\n\n"
        "───────────────\n"
        "<b>ЭТО БЫЛА НЕ ИНСТРУКЦИЯ. ЭТО БЫЛА ПЕРВАЯ СТРАНИЦА.</b>\n"
        "Полная «Инструкция к себе» покажет, как все 46 аспектов вашей личности связаны между собой."
    )

    if is_admin or has_ent:
        report_text += "\n\n👑 <b>Административный доступ:</b> Вам разблокирован полный доступ к Этапу 2 (DEEP)."

    payment_url = create_prodamus_payment_link(user_id=session.user_id, session_id=session.id)
    if is_admin or has_ent:
        markup = get_admin_paywall_keyboard(payment_url)
    else:
        markup = get_paywall_keyboard(payment_url)

    core_img = os.path.join(ASSETS_IMAGES_DIR, "core_report.png")
    if os.path.exists(core_img):
        try:
            await message.answer_photo(FSInputFile(core_img))
        except Exception as img_err:
            logger.error(f"Failed to send CORE report photo: {img_err}")

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


# --- ADMIN HANDLERS & COMMANDS ---

@router.message(Command("admin"))
@router.message(F.text == "👑 Админ-панель")
async def cmd_admin(message: Message):
    """Admin control panel dashboard."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username
        )
        if not user.is_admin:
            await message.answer("⛔ <i>У вас нет прав администратора.</i>", parse_mode="HTML")
            return

        stats = await get_admin_stats(db)
        q_summary = get_question_bank_summary()

        text = (
            "👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА СИСТЕМЫ</b>\n\n"
            f"<b>Администратор:</b> @{user.username or user.telegram_user_id}\n\n"
            f"📊 <b>Общая статистика:</b>\n"
            f"• Пользователей в системе: <b>{stats['total_users']}</b> (Админов: <b>{stats['total_admins']}</b>)\n"
            f"• Активных сессий: <b>{stats['active_sessions']}</b>\n"
            f"• Активных доступов (Entitlements): <b>{stats['active_entitlements']}</b>\n"
            f"• Оплаченных заказов: <b>{stats['successful_payments']}</b>\n"
            f"• Сформировано PDF-инструкций: <b>{stats['pdf_exports']}</b>\n\n"
            f"📚 <b>Банк вопросов ({q_summary['total_count']} всего):</b>\n"
            f"• CORE Базовые: <b>{q_summary['core_base_count']}</b>\n"
            f"• DEEP Шкалы (Traits): <b>{q_summary['deep_trait_count']}</b>\n"
            f"• State/Context: <b>{q_summary['deep_state_context_count']}</b>\n"
            f"• VFC Выбор ценностей: <b>{q_summary['vfc_count']}</b>\n\n"
            "Выберите нужное действие ниже:"
        )
        await message.answer(text, parse_mode="HTML", reply_markup=get_admin_dashboard_keyboard())


@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(callback: CallbackQuery):
    """Return to admin main menu inline."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        if not user.is_admin:
            await callback.answer("У вас нет прав администратора.")
            return

        stats = await get_admin_stats(db)
        text = (
            "👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА СИСТЕМЫ</b>\n\n"
            f"<b>Администратор:</b> @{user.username or user.telegram_user_id}\n\n"
            f"📊 <b>Общая статистика:</b>\n"
            f"• Пользователей: <b>{stats['total_users']}</b> (Админов: <b>{stats['total_admins']}</b>)\n"
            f"• Активных сессий: <b>{stats['active_sessions']}</b>\n"
            f"• Активных доступов: <b>{stats['active_entitlements']}</b>\n"
            f"• Оплаченных заказов: <b>{stats['successful_payments']}</b>\n"
            f"• Сформировано PDF: <b>{stats['pdf_exports']}</b>\n\n"
            "Выберите нужное действие ниже:"
        )
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_dashboard_keyboard())


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Show detailed admin stats callback."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        if not user.is_admin:
            await callback.answer("Отказано в доступе.")
            return

        stats = await get_admin_stats(db)
        phase_str = "\n".join([f"  • {k}: {v}" for k, v in stats["phase_breakdown"].items()])
        text = (
            "📊 <b>ДЕТАЛЬНАЯ СТАТИСТИКА СИСТЕМЫ</b>\n\n"
            f"• <b>Всего пользователей:</b> {stats['total_users']}\n"
            f"• <b>Администраторов:</b> {stats['total_admins']}\n"
            f"• <b>Активных сессий:</b> {stats['active_sessions']}\n"
            f"• <b>Активных доступов (DEEP):</b> {stats['active_entitlements']}\n"
            f"• <b>Успешных оплат:</b> {stats['successful_payments']}\n"
            f"• <b>Сгенерировано PDF:</b> {stats['pdf_exports']}\n\n"
            f"📌 <b>Распределение по фазам сессий:</b>\n{phase_str if phase_str else '  • Нет данных'}\n"
        )
        markup = get_admin_dashboard_keyboard()
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("admin:questions:"))
async def cb_admin_questions(callback: CallbackQuery):
    """Question bank paginated viewer."""
    parts = callback.data.split(":")
    phase = parts[2] if len(parts) > 2 else "CORE"
    page = int(parts[3]) if len(parts) > 3 else 1

    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        if not user.is_admin:
            await callback.answer("Отказано в доступе.")
            return

        page_size = 5
        items, total = list_questions_by_phase(phase, page=page, page_size=page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)

        lines = [f"📚 <b>Банк вопросов [{phase}] (Стр. {page}/{total_pages}, всего {total}):</b>\n"]
        for idx, item in enumerate(items, start=(page-1)*page_size + 1):
            qid = item["question_id"]
            if item["type"] == "VFC":
                lines.append(f"<b>{idx}. [{qid}] (VFC)</b>\n{item['text_ru']}\n")
            else:
                scale = item.get("scale_id", "")
                direction = item.get("direction", "+")
                lines.append(f"<b>{idx}. [{qid}]</b> ({scale}, {direction})\n«{item['text_ru']}»\n")

        nav_kb = get_admin_questions_nav_keyboard(phase, page, total_pages)
        await callback.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=nav_kb)


@router.callback_query(F.data == "admin:grant_prompt")
async def cb_admin_grant_prompt(callback: CallbackQuery):
    """Instruction on how to grant admin access to another user."""
    text = (
        "🔓 <b>Выдача прав администратора и доступа:</b>\n\n"
        "Чтобы выдать пользователю права админа и полный доступ к DEEP, отправьте команду:\n\n"
        "<code>/grant @username</code> или <code>/grant 123456789</code>\n\n"
        "<i>Например: /grant @AstiHakun или /grant @sherlockdxb</i>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_dashboard_keyboard())


@router.message(Command("grant"))
@router.message(Command("admin_grant"))
async def cmd_grant(message: Message):
    """Command handler to grant admin access by username or Telegram user ID."""
    async with AsyncSessionLocal() as db:
        admin_user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username
        )
        if not admin_user.is_admin:
            await message.answer("⛔ <i>У вас нет прав администратора.</i>", parse_mode="HTML")
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("⚠️ Укажите username или Telegram ID. Пример:\n<code>/grant @username</code>")
            return

        target_id = parts[1].strip()
        success, res_msg = await grant_user_entitlement(db, target_id)
        await message.answer(res_msg, parse_mode="HTML")


@router.callback_query(F.data == "admin_start_deep")
async def cb_admin_start_deep(callback: CallbackQuery):
    """Direct transition to DEEP phase for Admin users."""
    await callback.answer("Переход к этапу DEEP...")
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)

        # Grant active entitlement if missing
        stmt_ent = select(AccessEntitlement).where(
            AccessEntitlement.session_id == session.id,
            AccessEntitlement.entitlement_type == "FULL_REPORT"
        )
        res_ent = await db.execute(stmt_ent)
        if not res_ent.scalar_one_or_none():
            ent = AccessEntitlement(
                user_id=user.id,
                session_id=session.id,
                entitlement_type="FULL_REPORT",
                source="admin",
                status="ACTIVE"
            )
            db.add(ent)

        session.phase = "DEEP_IN_PROGRESS"
        await db.commit()

        await callback.message.answer("🚀 <b>Этап 2: DEEP (Глубокое исследование) успешно разблокирован!</b>\n\nНачинаем диагностику шкал личности.", parse_mode="HTML")
        await send_next_question(callback.message, db, session)

