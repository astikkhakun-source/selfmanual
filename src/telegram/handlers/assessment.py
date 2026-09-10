import json
import os
import uuid
import logging
from typing import Optional
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from src.db.base import AsyncSessionLocal
from src.db.models import User, AccessEntitlement, AssessmentSession
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
from src.domain.scoring.full_engine import calculate_full_profile
from src.domain.scoring.scales import calculate_primary_scales
from src.domain.scoring.patterns import evaluate_full_patterns
from src.domain.scoring.conflicts import evaluate_full_conflicts
from src.services.payment import create_prodamus_payment_link
from src.services.llm_report import generate_full_report_llm, generate_core_report_llm
from src.services.pdf_export import generate_pdf_report, generate_core_pdf_report
from src.telegram.keyboards import (
    get_likert_keyboard, get_vfc_keyboard, get_paywall_keyboard, get_consent_keyboard,
    get_restart_confirm_keyboard, get_admin_paywall_keyboard, 
    get_main_reply_keyboard, get_admin_dashboard_keyboard,
    get_admin_questions_nav_keyboard, get_consultation_discount_keyboard,
    get_promo_menu_keyboard, get_promo_uses_keyboard, get_promo_duration_keyboard, get_promo_list_keyboard
)
from src.telegram.states import PromoCreateFSM
from src.services.promo_service import (
    create_promo_code, validate_and_use_promo_code, get_all_promo_codes,
    toggle_promo_code_status, generate_random_promo_code
)
from src.services.settings_service import (
    is_report_forwarding_enabled, toggle_report_forwarding
)

logger = logging.getLogger(__name__)
router = Router()


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
ASSETS_IMAGES_DIR = os.path.join(ROOT_DIR, "assets", "images")

CONSULTATION_OFFER_TEXT = (
    "<b>Вы узнали больше о себе. Что дальше?</b>\n\n"
    "Возможно, в этом отчёте вы узнали свои привычные реакции и увидели то, что давно мешает вам жить так, как хочется. "
    "Теперь возникает вопрос: «Как с этим быть и с чего начать?»\n\n"
    "На личной консультации со мной мы разберём ваши результаты в контексте вашей жизни: что сейчас создаёт больше всего трудностей, "
    "как поддерживаются повторяющиеся сценарии и на что вы можете опереться, чтобы начать изменения. Вы сможете задать вопросы и определить конкретные следующие шаги.\n\n"
    "🎁 <b>Для вас как участника SelfCode — персональная скидка 20% на личную консультацию.</b> "
    "Предложение действует 3 дня с момента получения отчёта.\n\n"
    "Чтобы воспользоваться скидкой, при записи нажмите кнопку ниже или отправьте слово «<b>SELFCODE</b>» в ответ на это сообщение!"
)


async def send_consultation_offer(message: Message):
    """Send consultation offer message with 20% discount button after PDF delivery."""
    try:
        markup = get_consultation_discount_keyboard()
        await message.answer(CONSULTATION_OFFER_TEXT, parse_mode="HTML", reply_markup=markup)
    except Exception as err:
        logger.error(f"Failed to send consultation offer message: {err}")



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

        reply_kb = get_main_reply_keyboard(is_admin=user.is_admin, show_pay_button=(session and session.phase == 'CORE_READY'))
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
                "👁️ <b>Добро пожаловать в систему SelfCode V1.3!</b>\n\n"
                "Ваша личность — это не застывший набор мыслей, а живая система восприятия, постоянно редактирующая свой собственный код перед тем, как его заметит окружающая реальность.\n\n"
                "<b>📌 Как устроено исследование:</b>\n"
                "• <b>Этап 1 (CORE — Бесплатно):</b> 24 базовых + до 6 адаптивных вопросов. Алгоритм вскрывает вашу первичную архитектуру, ключевые опоры и главный парадокс вашей системы.\n"
                "• <b>Этап 2 (DEEP — Полный отчёт):</b> Анализ 46 шкал личности, 12 профильных глав и персональный 12-страничный PDF-отчет SelfCode.\n\n"
                "💡 <i>Здесь нет «правильных» или «угодных» ответов. Вы отвечаете не перед экзаменатором, а перед собственным проекционным аппаратом.</i>\n\n"
                "Нажмите кнопку ниже, чтобы начать первый этап CORE."
            )
            await message.answer(welcome_text, parse_mode="HTML", reply_markup=reply_kb)
            await message.answer("<b>Согласие на обработку данных:</b>", parse_mode="HTML", reply_markup=get_consent_keyboard())
            return

        # Resume session menu
        resume_text = (
            "👁️ <b>Вы вернулись в меню системы SelfCode V1.3.</b>\n\n"
            f"Ваше исследование находится в процессе (отвечено вопросов: <b>{len(answers_map)}</b>).\n\n"
            "• Нажмите <b>«▶️ Продолжить диагностику»</b>, чтобы перейти к очередному вопросу.\n"
            "• Нажмите <b>«🔄 Начать заново»</b>, чтобы сбросить сессию и пройти онбординг с нуля."
        )
        await message.answer(resume_text, parse_mode="HTML", reply_markup=reply_kb)



@router.message(F.text == "▶️ Продолжить диагностику")
async def btn_continue(message: Message):
    """Handle 'Continue' button press from bottom reply menu."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username
        )
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)
        
        if session.phase == "CONSENT_PENDING":
            await message.answer("Пожалуйста, примите условия перед началом исследования.", reply_markup=get_consent_keyboard())
            return

        if session.phase == "CORE_READY":
            stmt_ent = select(AccessEntitlement).where(
                AccessEntitlement.session_id == session.id,
                AccessEntitlement.status == "ACTIVE"
            )
            res_ent = await db.execute(stmt_ent)
            has_ent = res_ent.scalars().first() is not None

            if user.is_admin or has_ent:
                session.phase = "DEEP_IN_PROGRESS"
                await db.commit()
                await message.answer("🚀 <b>Переходим к Этапу 2 (DEEP)...</b>", parse_mode="HTML")
                await send_next_question(message, db, session)
                return
            else:
                payment_url = create_prodamus_payment_link(user_id=session.user_id, session_id=session.id)
                await message.answer(
                    "🪞 <b>Ваша карта-отчет CORE уже готова!</b>\n\n"
                    "Для продолжения исследования и перехода к 175 вопросам <b>Этапа 2 (DEEP)</b> откройте доступ по кнопке ниже:",
                    parse_mode="HTML",
                    reply_markup=get_paywall_keyboard(payment_url)
                )
                return

        await send_next_question(message, db, session)



@router.message(F.text == "💳 Оплатить полный доступ (DEEP)")
async def btn_pay_full_access(message: Message):
    """Show paywall when user clicks the payment button in the main menu."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id
        )
        session = await get_active_session(db, user.id)
        if not session or session.phase != "CORE_READY":
            await message.answer("Оплата полного отчета сейчас недоступна. Пожалуйста, завершите первый этап тестирования.")
            return

        payment_url = create_prodamus_payment_link(user_id=session.user_id, session_id=session.id)
        await message.answer(
            "🪞 <b>Доступ к Этапу 2 (DEEP)</b>\n\n"
            "Оплатите доступ по ссылке ниже, чтобы разблокировать оставшиеся 145 вопросов и получить полный PDF-отчёт SelfCode.",
            parse_mode="HTML",
            reply_markup=get_paywall_keyboard(payment_url)
        )

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
        "<b>🧠 О системе SelfCode V1.3</b>\n\n"
        "Система совмещает детерминированный математический скоринг 46 шкал личности и глубинный синтез смыслов.\n\n"
        "<b>Архитектура исследования:</b>\n"
        "• <b>CORE:</b> 24 базовых + адаптивные вопросы для первичного вскрытия алгоритмов восприятия.\n"
        "• <b>46 Primary Scales:</b> Измерение автономии, регуляции самоценности, близости, проявленности и работы с неопределенностью.\n"
        "• <b>10 Персональных правил:</b> Фундаментальные ориентиры взаимодействия с собственной психикой.\n"
        "• <b>PDF Export:</b> Формирование персонального отчета SelfCode формата A4."
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
        
        reply_kb = get_main_reply_keyboard(is_admin=user.is_admin, show_pay_button=(session and session.phase == 'CORE_READY'))
        welcome_text = (
            "👁️ <b>Добро пожаловать в систему SelfCode V1.3!</b>\n\n"
            "Ваша личность — это не застывший набор мыслей, а живая система восприятия, постоянно редактирующая свой собственный код перед тем, как его заметит окружающая реальность.\n\n"
            "<b>📌 Как устроено исследование:</b>\n"
            "• <b>Этап 1 (CORE — Бесплатно):</b> 24 базовых + до 6 адаптивных вопросов. Алгоритм вскрывает вашу первичную архитектуру, ключевые опоры и главный парадокс вашей системы.\n"
            "• <b>Этап 2 (DEEP — Полный отчёт):</b> Анализ 46 шкал личности, 12 профильных глав и персональный 12-страничный PDF-отчет SelfCode.\n\n"
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

        old_phase = session.phase
        await save_answer(
            db,
            session_id=session.id,
            question_id=q_id,
            raw_answer=raw_answer,
            phase=old_phase,
            client_event_id=client_event_id
        )

        if old_phase in ("CORE_READY", "FULL_ASSESSMENT_COMPLETED"):
            await callback.answer("Ответ сохранён!", show_alert=False)
            return

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

        old_phase = session.phase
        await save_answer(
            db,
            session_id=session.id,
            question_id=vfc_id,
            raw_answer=1 if selected_val == "autonomy" else 2,
            phase="VFC",
            client_event_id=client_event_id,
            selected_value=selected_val
        )

        if old_phase == "FULL_ASSESSMENT_COMPLETED":
            await callback.answer("Ответ сохранён!", show_alert=False)
            return

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

    # Pelevin-style milestone communication
    pelevin_intro = ""
    if progress == 50:
        pelevin_intro = "👁 <i>Пятьдесят вопросов позади. Мы уже видим контуры вашей проекции. Не пытайтесь казаться лучше, алгоритм всё равно заметит склейки. Продолжаем.</i>\n\n"
    elif progress == 100:
        pelevin_intro = "⏳ <i>Сотня вопросов загружена. Эго начинает уставать удерживать фасад, и это прекрасно — именно сейчас сквозь трещины проступает настоящий код. Идём дальше.</i>\n\n"
    elif progress == 148:
        pelevin_intro = "🧬 <b>Базовые паттерны отсканированы.</b>\n\n<i>Ваш личностный каркас зафиксирован. Но любой каркас помещен в конкретное пространство. Следующие несколько вопросов замерят ваш текущий контекст и остаток ресурса. Как вы чувствуете себя прямо сейчас, в этой точке симуляции?</i>\n\n"
    elif progress == 160:
        pelevin_intro = "🚬 <b>Основной массив данных загружен.</b>\n\n<i>Любая система проверяется не в статике, а в моменты сбоя. Мы переходим к финальному этапу. Здесь нет градиентов и спасительной середины. Вам предстоит выбрать между двумя конфликтующими ценностями. Что для вас важнее, когда реальность заставляет платить по счетам?</i>\n\n"

    if next_q["phase"] == "VFC":
        vfc_data = next_q.get("vfc_data") or {"value_a": "A", "text_a": "Вариант А", "value_b": "B", "text_b": "Вариант Б"}
        text = (
            f"{pelevin_intro}"
            f"<b>Вопрос {progress + 1} из {target} (Выбор приоритета):</b>\n\n"
            f"Что для вас представляет большую ценность?\n\n"
            f"<b>А:</b> {vfc_data['text_a']}\n"
            f"<b>Б:</b> {vfc_data['text_b']}"
        )
        markup = get_vfc_keyboard(q_id, vfc_data, client_event_id)
    elif next_q["phase"] == "CORE_ADAPTIVE":
        adaptive_idx = next_q.get("adaptive_index", 1)
        text = (
            f"{pelevin_intro}"
            f"<b>Уточняющий вопрос {adaptive_idx} из 6 (Адаптивный блок CORE):</b>\n\n"
            f"«{q_text}»\n\n"
            f"<i>1 — полностью не согласен\n7 — полностью согласен</i>"
        )
        markup = get_likert_keyboard(q_id, client_event_id)
    else:
        text = (
            f"{pelevin_intro}"
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


async def forward_report_to_admins(
    db,
    bot,
    user: User,
    session: AssessmentSession,
    report_type: str,
    report_text: str = "",
    pdf_path: Optional[str] = None
):
    """
    If report forwarding to admins is enabled, send duplicate of the report with user details.
    """
    try:
        if not await is_report_forwarding_enabled(db):
            return

        stmt_admins = select(User).where(User.is_admin == True)
        res_admins = await db.execute(stmt_admins)
        admins = res_admins.scalars().all()

        if not admins:
            return

        user_name = user.username or f"User_{user.telegram_user_id}"
        username_str = f"@{user.username}" if user.username else "нет username"
        user_mention = f'<a href="tg://user?id={user.telegram_user_id}">{user_name}</a>'
        now_str = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")

        header_text = (
            f"📬 <b>ДУБЛИКАТ ОТЧЁТА ПОЛЬЗОВАТЕЛЯ ({report_type})</b>\n\n"
            f"👤 <b>Пользователь:</b> {user_mention} ({username_str})\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.telegram_user_id}</code>\n"
            f"📋 <b>Сессия:</b> <code>{session.id[:8]}</code>\n"
            f"🕒 <b>Время:</b> {now_str}\n\n"
            f"{report_text[:1000]}"
        )

        for admin in admins:
            try:
                target_chat = admin.chat_id or admin.telegram_user_id
                if pdf_path and os.path.exists(pdf_path):
                    doc_filename = f"SelfCode_{report_type.replace(' ', '_')}_{user_name}.pdf"
                    pdf_file = FSInputFile(pdf_path, filename=doc_filename)
                    await bot.send_document(chat_id=target_chat, document=pdf_file, caption=header_text, parse_mode="HTML")
                else:
                    await bot.send_message(chat_id=target_chat, text=header_text, parse_mode="HTML")
            except Exception as send_err:
                logger.error(f"Failed to forward report duplicate to admin {admin.telegram_user_id}: {send_err}")
    except Exception as err:
        logger.error(f"Error in forward_report_to_admins: {err}", exc_info=True)


async def render_free_core_report(message: Message, db, session):
    """Render the new 3-page PDF FREE report (SelfCore) and personalized Paywall."""
    answers_map = await get_session_answers_map(db, session.id)
    
    # Format answers for the scoring engine
    answers_text = ""
    for q_id, ans in answers_map.items():
        q_info = get_question_info(q_id)
        q_text = q_info.get("text_ru", f"Вопрос {q_id}")
        answers_text += f"{q_id}:\nQuestion: {q_text}\nAnswer: {ans}\n\n"

    status_msg = await message.answer("🔄 <i>Формируем вашу персональную архитектуру SelfCore...</i>", parse_mode="HTML")

    # Call LLM logic
    report_data = await generate_core_report_llm(answers_text)
    
    pdf_path = None
    try:
        # Generate PDF
        pdf_path = generate_core_pdf_report(session.id, report_data)
    except Exception as e:
        logger.error(f"Failed to generate CORE pdf: {e}", exc_info=True)
        await status_msg.edit_text("⚠️ Ошибка при формировании PDF. Попробуйте еще раз.")
        return

    # Check if user is admin or entitled
    stmt_u = select(User).where(User.id == session.user_id)
    res_u = await db.execute(stmt_u)
    user = res_u.scalars().first()

    stmt_ent = select(AccessEntitlement).where(
        AccessEntitlement.session_id == session.id,
        AccessEntitlement.status == "ACTIVE"
    )
    res_ent = await db.execute(stmt_ent)
    has_ent = res_ent.scalars().first() is not None
    is_admin = user.is_admin if user else False

    payment_url = create_prodamus_payment_link(user_id=session.user_id, session_id=session.id)
    if is_admin or has_ent:
        markup = get_admin_paywall_keyboard(payment_url)
    else:
        markup = get_paywall_keyboard(payment_url)

    report_text = (
        "🪞 <b>ВАШ БЕСПЛАТНЫЙ ОТЧЕТ SELFCORE ГОТОВ</b>\n\n"
        "PDF-документ сформирован и прикреплен ниже. В нем вы найдете свою первичную архитектуру, "
        "ключевые показатели, внутренний цикл и правила обращения с собой.\n\n"
        "<i>Мы уже видим несколько противоречий в ваших ответах. Но данных CORE недостаточно, чтобы определить, "
        "являются ли они случайными или образуют устойчивый внутренний конфликт. Для этого нужен следующий уровень диагностики (DEEP).</i>"
    )

    if is_admin or has_ent:
        report_text += "\n\n👑 <b>Административный доступ:</b> Вам разблокирован полный доступ к Этапу 2 (DEEP)."

    try:
        await status_msg.delete()
    except Exception:
        pass

    pdf_file = FSInputFile(pdf_path, filename=f"SelfCore_{session.id[:8]}.pdf")
    try:
        await message.answer_document(pdf_file, caption=report_text, parse_mode="HTML", reply_markup=markup)
    except Exception as doc_err:
        logger.error(f"Failed to send CORE PDF document: {doc_err}")
        await message.answer(report_text, parse_mode="HTML", reply_markup=markup)

    # Forward duplicate to admin monitoring if enabled
    if user:
        await forward_report_to_admins(db, message.bot, user, session, "CORE FREE", report_text=report_text, pdf_path=pdf_path)

    # Deliver consultation offer message with 20% discount button
    await send_consultation_offer(message)


async def render_full_report_and_pdf(message: Message, db, session, precomputed_answers: dict = None):
    """Generate FULL report via LLM and deliver PDF to Telegram chat."""
    stmt_u = select(User).where(User.id == session.user_id)
    res_u = await db.execute(stmt_u)
    user = res_u.scalars().first()

    if precomputed_answers is not None:
        answers_map = precomputed_answers
    else:
        answers_map = await get_session_answers_map(db, session.id)
        
    input_package = calculate_full_profile(answers_map)

    status_msg = await message.answer("🔄 <i>Система генерирует ваш персональный отчёт SelfCode PDF...</i>", parse_mode="HTML")

    # Generate LLM Report & PDF
    llm_report = await generate_full_report_llm(input_package)

    rules_text = "\n".join([f"• {r}" for r in llm_report.get("personal_rules", [])[:5]])
    full_text = (
        "<b>ПОЛНЫЙ ОТЧЕТ SELFCODE V1.3 ГОТОВ!</b>\n\n"
        f"<b>Ключевые правила обращения с собой:</b>\n{rules_text}\n\n"
    )

    pdf_path = None
    try:
        pdf_path = generate_pdf_report(session.id, llm_report)
        full_text += "📄 Ваш детальный 12-страничный PDF-отчет сформирован и прикреплен ниже."
        await status_msg.edit_text(full_text, parse_mode="HTML")

        # Send PDF document directly to Telegram chat
        pdf_file = FSInputFile(pdf_path, filename=f"SelfCode_{session.id[:8]}.pdf")
        await message.answer_document(pdf_file, caption="Ваш персональный PDF-отчет SelfCode V1.3")
    except Exception as pdf_err:
        logger.error(f"Ошибка при генерации PDF: {pdf_err}", exc_info=True)
        full_text += "⚠️ <i>Не удалось сформировать PDF-документ, но ваш текстовый отчёт сгенерирован выше.</i>"
        await status_msg.edit_text(full_text, parse_mode="HTML")

    # Forward duplicate to admin monitoring if enabled
    if user:
        await forward_report_to_admins(db, message.bot, user, session, "FULL DEEP", report_text=full_text, pdf_path=pdf_path)

    # Deliver consultation offer message with 20% discount button
    await send_consultation_offer(message)


async def process_consultation_request(event, db, user):
    """
    Process consultation request for 20% discount:
    - Send user confirmation message
    - Send alert to all bot admins with user contact info and session ID
    """
    confirm_text = (
        "✅ <b>Ваша заявка на личную консультацию со скидкой 20% получена!</b>\n\n"
        "Персональная скидка по промокоду <b>SELFCODE</b> успешно зафиксирована за вашим аккаунтом. "
        "Мы свяжемся с вами в ближайшее время для согласования удобного времени."
    )
    
    session = await get_active_session(db, user.id)
    session_id = session.id if session else f"demo_{user.telegram_user_id}"

    user_tg = event.from_user
    bot = event.bot

    if isinstance(event, CallbackQuery):
        try:
            await event.answer("Заявка принята!")
        except Exception:
            pass
        await event.message.answer(confirm_text, parse_mode="HTML")
    else:
        await event.answer(confirm_text, parse_mode="HTML")

    user_name = user_tg.full_name or "Пользователь"
    username_str = f"@{user_tg.username}" if user_tg.username else "нет username"
    user_mention = f'<a href="tg://user?id={user_tg.id}">{user_name}</a>'
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    admin_alert_text = (
        "🔔 <b>НОВАЯ ЗАЯВКА НА ЛИЧНУЮ КОНСУЛЬТАЦИЮ (СКИДКА 20% SELFCODE)!</b>\n\n"
        f"• <b>Пользователь:</b> {user_mention} ({username_str})\n"
        f"• <b>Telegram ID:</b> <code>{user_tg.id}</code>\n"
        f"• <b>Промокод:</b> <code>SELFCODE</code> (Скидка 20%)\n"
        f"• <b>Сессия:</b> <code>{session_id[:8]}</code>\n"
        f"• <b>Дата заявки:</b> {now_str}"
    )

    # Broadcast notification to all registered admins
    stmt_admins = select(User).where(User.is_admin == True)
    res_admins = await db.execute(stmt_admins)
    admin_users = res_admins.scalars().all()

    for admin in admin_users:
        try:
            target_chat = admin.chat_id or admin.telegram_user_id
            await bot.send_message(chat_id=target_chat, text=admin_alert_text, parse_mode="HTML")
        except Exception as err:
            logger.error(f"Failed to notify admin {admin.telegram_user_id}: {err}")


@router.callback_query(F.data == "claim_consultation_discount")
async def cb_claim_consultation_discount(callback: CallbackQuery):
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        await process_consultation_request(callback, db, user)


@router.message(Command("selfcode"))
@router.message(F.text.icontains("SELFCODE"))
async def msg_claim_consultation_discount(message: Message):
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username
        )
        await process_consultation_request(message, db, user)




@router.callback_query(F.data == "admin_fastforward")
async def cq_admin_fastforward(callback: CallbackQuery):
    """Fast-forward test to completion for admins via inline button."""
    await callback.answer() # Immediately answer to stop loading animation
    
    try:
        async with AsyncSessionLocal() as db:
            user = await get_or_create_user(
                db,
                telegram_user_id=callback.from_user.id,
                chat_id=callback.message.chat.id,
                username=callback.from_user.username
            )
            if not user.is_admin:
                await callback.message.answer("У вас нет прав администратора.")
                return
                
            session = await get_active_session(db, user.id)
            if not session:
                await callback.message.answer("Нет активной сессии.")
                return

            status_msg = await callback.message.answer("⏩ <i>Прокручиваем 175 вопросов (это займет пару секунд)...</i>", parse_mode="HTML")

            answers_map = await get_session_answers_map(db, session.id)
            
            # We need all 175 questions. Fill the gaps in memory.
            import random
            random.seed(42)
            # q1-q160 are Likert (1-7), q161-q175 are VFC (A/B)
            for i in range(1, 161):
                q_id = f"q{i}"
                if q_id not in answers_map:
                    answers_map[q_id] = random.choice([1, 2, 6, 7])
            for i in range(161, 176):
                q_id = f"q{i}"
                if q_id not in answers_map:
                    answers_map[q_id] = random.choice(["A", "B"])
                    
            session.phase = "ASSESSMENT_COMPLETED"
            await db.commit()
            
            await status_msg.edit_text("⏩ <b>Тест прокручен до конца.</b>\nФормирую финальный отчет LLM...", parse_mode="HTML")
            await render_full_report_and_pdf(callback.message, db, session, precomputed_answers=answers_map)
    except Exception as e:
        import traceback
        err_str = traceback.format_exc()
        await callback.message.answer(f"❌ ОШИБКА:\n<pre>{err_str[-1500:]}</pre>", parse_mode="HTML")


@router.message(Command("ff"))
async def cmd_ff(message: Message):
    """Fast-forward test to completion for admins."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username
        )
        if not user.is_admin:
            return
            
        session = await get_active_session(db, user.id)
        if not session:
            await message.answer("Нет активной сессии.")
            return

        answers_map = await get_session_answers_map(db, session.id)
        
        import random
        random.seed(42)
        # We need all 175 questions
        for i in range(1, 161):
            q_id = f"q{i}"
            if q_id not in answers_map:
                answers_map[q_id] = random.choice([1, 2, 6, 7])
        for i in range(161, 176):
            q_id = f"q{i}"
            if q_id not in answers_map:
                answers_map[q_id] = random.choice(["A", "B"])
                
        session.phase = "ASSESSMENT_COMPLETED"
        await db.commit()
        
        await message.answer("⏩ Тест прокручен до конца. Формирую финальный отчет...")
        await render_full_report_and_pdf(message, db, session, precomputed_answers=answers_map)



@router.message(Command("promo"))
async def cmd_promo(message: Message):
    """Activate promo code for free access."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Пожалуйста, укажите промокод. Пример:\n<code>/promo GIFT2026</code>", parse_mode="HTML")
        return

    code = parts[1].strip()

    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username
        )
        session = await get_active_session(db, user.id)
        if not session:
            session = await start_new_session(db, user.id)

        success, msg, promo = await validate_and_use_promo_code(db, code, user.id, session.id)

        if success:
            full_msg = (
                f"{msg}\n\n"
                "Нажмите «▶️ Продолжить диагностику», чтобы перейти к следующим вопросам."
            )
            await message.answer(full_msg, parse_mode="HTML")
        else:
            await message.answer(msg, parse_mode="HTML")


# ------------------------------------------------------------------
# PROMO CODE ADMIN HANDLERS
# ------------------------------------------------------------------

@router.callback_query(F.data == "admin:promos")
async def cb_admin_promos(callback: CallbackQuery, state: FSMContext):
    """Promo code admin management menu."""
    await state.clear()
    text = (
        "🎟 <b>УПРАВЛЕНИЕ ПРОМОКОДАМИ SELFCODE</b>\n\n"
        "Здесь вы можете генерировать промокоды с настраиваемым лимитом копий "
        "и временем действия, а также просматривать и деактивировать активные коды."
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_promo_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:promo:create")
async def cb_admin_promo_create(callback: CallbackQuery, state: FSMContext):
    """Step 1: Start promo creation, ask for code name."""
    await state.set_state(PromoCreateFSM.waiting_for_code)
    
    random_code = generate_random_promo_code()
    buttons = [
        [InlineKeyboardButton(text=f"🎲 Использовать {random_code}", callback_data=f"use_code:{random_code}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:promos")]
    ]
    
    text = (
        "➕ <b>СОЗДАНИЕ НОВОГО ПРОМОКОДА (Шаг 1 из 3)</b>\n\n"
        "Отправьте название промокода текстом (например, <code>GIFT2026</code>) "
        "или нажмите кнопку ниже для случайной генерации:"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("use_code:"))
async def cb_admin_use_random_code(callback: CallbackQuery, state: FSMContext):
    """Handle choice of auto-generated code."""
    code = callback.data.split(":", 1)[1]
    await state.update_data(code=code)
    await state.set_state(PromoCreateFSM.waiting_for_uses)
    
    text = (
        f"🎫 Промокод: <code>{code}</code>\n\n"
        "👥 <b>Укажите количество активаций (копий) (Шаг 2 из 3):</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_promo_uses_keyboard())
    await callback.answer()


@router.message(PromoCreateFSM.waiting_for_code)
async def msg_admin_promo_code_input(message: Message, state: FSMContext):
    """Handle text input for promo code name."""
    code = message.text.strip().upper()
    if len(code) < 3:
        await message.answer("⚠️ Название промокода должно содержать минимум 3 символа.")
        return
        
    await state.update_data(code=code)
    await state.set_state(PromoCreateFSM.waiting_for_uses)
    
    text = (
        f"🎫 Промокод: <code>{code}</code>\n\n"
        "👥 <b>Укажите количество активаций (копий) (Шаг 2 из 3):</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_promo_uses_keyboard())


@router.callback_query(F.data.startswith("promo_uses:"))
async def cb_admin_promo_uses(callback: CallbackQuery, state: FSMContext):
    """Handle choice for max uses."""
    val = callback.data.split(":")[1]
    if val == "custom":
        await callback.message.edit_text(
            "✏️ <b>Введите количество копий/активаций числом:</b>",
            parse_mode="HTML"
        )
        await callback.answer()
        return
        
    uses = int(val)
    await state.update_data(max_uses=uses)
    await state.set_state(PromoCreateFSM.waiting_for_duration)
    
    data = await state.get_data()
    text = (
        f"🎫 Промокод: <code>{data.get('code')}</code>\n"
        f"👥 Количество активаций: <b>{uses}</b>\n\n"
        "⏳ <b>Укажите срок действия (длительность) (Шаг 3 из 3):</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_promo_duration_keyboard())
    await callback.answer()


@router.message(PromoCreateFSM.waiting_for_uses)
async def msg_admin_promo_uses_custom(message: Message, state: FSMContext):
    """Handle custom integer input for max uses."""
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("⚠️ Пожалуйста, введите положительное целое число (например, 25).")
        return
        
    uses = int(message.text)
    await state.update_data(max_uses=uses)
    await state.set_state(PromoCreateFSM.waiting_for_duration)
    
    data = await state.get_data()
    text = (
        f"🎫 Промокод: <code>{data.get('code')}</code>\n"
        f"👥 Количество активаций: <b>{uses}</b>\n\n"
        "⏳ <b>Укажите срок действия (длительность) (Шаг 3 из 3):</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_promo_duration_keyboard())


@router.callback_query(F.data.startswith("promo_dur:"))
async def cb_admin_promo_duration(callback: CallbackQuery, state: FSMContext):
    """Final step: Handle duration choice and save promo code to DB."""
    dur_days = int(callback.data.split(":")[1])
    data = await state.get_data()
    code = data.get("code")
    max_uses = data.get("max_uses", 1)
    
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        promo = await create_promo_code(
            db=db,
            code=code,
            max_uses=max_uses,
            duration_days=dur_days if dur_days > 0 else None,
            creator_user_id=user.id
        )
        
    await state.clear()
    
    expiry_str = f"{dur_days} дн." if dur_days > 0 else "♾️ Без ограничений"
    if promo.expires_at:
        expiry_str += f" (до {promo.expires_at.strftime('%d.%m.%Y %H:%M')})"
        
    text = (
        "🎉 <b>ПРОМОКОД УСПЕШНО СОЗДАН!</b>\n\n"
        f"🎫 Код: <code>{promo.code}</code>\n"
        f"👥 Лимит активаций: <b>{promo.max_uses}</b>\n"
        f"⏳ Срок действия: <b>{expiry_str}</b>\n\n"
        "Вы можете скопировать код нажатием на него и передать пользователю.\n"
        "Пользователь активирует его в боте командой:\n"
        f"<code>/promo {promo.code}</code>"
    )
    
    buttons = [
        [InlineKeyboardButton(text="➕ Создать ещё", callback_data="admin:promo:create")],
        [InlineKeyboardButton(text="📋 К списку промокодов", callback_data="admin:promo:list")]
    ]
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data == "admin:promo:list")
async def cb_admin_promo_list(callback: CallbackQuery):
    """View active and expired promo codes."""
    async with AsyncSessionLocal() as db:
        promos = await get_all_promo_codes(db)
        
    if not promos:
        text = "📋 <b>Список промокодов пуст.</b>\n\nНажмите кнопку ниже, чтобы создать ваш первый промокод."
        buttons = [
            [InlineKeyboardButton(text="➕ Создать промокод", callback_data="admin:promo:create")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:promos")]
        ]
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await callback.answer()
        return

    lines = ["📋 <b>СПИСОК ПРОМОКОДОВ SELFCODE</b>\n"]
    for p in promos:
        icon = "🟢" if p.is_active else "🔴"
        uses = f"{p.used_count}/{p.max_uses}"
        dur = f"{p.duration_days} дн." if p.duration_days else "♾️"
        lines.append(f"{icon} <code>{p.code}</code> | Использовано: <b>{uses}</b> | Срок: <b>{dur}</b>")
        
    lines.append("\nНажмите на код в списке ниже, чтобы включить/отключить его:")
    text = "\n".join(lines)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_promo_list_keyboard(promos))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:promo:toggle:"))
async def cb_admin_promo_toggle(callback: CallbackQuery):
    """Toggle active/inactive status of promo code."""
    promo_id = callback.data.split(":")[3]
    async with AsyncSessionLocal() as db:
        await toggle_promo_code_status(db, promo_id)
        promos = await get_all_promo_codes(db)
        
    lines = ["📋 <b>СПИСОК ПРОМОКОДОВ SELFCODE</b>\n"]
    for p in promos:
        icon = "🟢" if p.is_active else "🔴"
        uses = f"{p.used_count}/{p.max_uses}"
        dur = f"{p.duration_days} дн." if p.duration_days else "♾️"
        lines.append(f"{icon} <code>{p.code}</code> | Использовано: <b>{uses}</b> | Срок: <b>{dur}</b>")
        
    lines.append("\nНажмите на код в списке ниже, чтобы включить/отключить его:")
    text = "\n".join(lines)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_promo_list_keyboard(promos))
    await callback.answer("Статус промокода обновлён")


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
        fwd_enabled = await is_report_forwarding_enabled(db)

        text = (
            "👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА СИСТЕМЫ</b>\n\n"
            f"<b>Администратор:</b> @{user.username or user.telegram_user_id}\n\n"
            f"📊 <b>Общая статистика:</b>\n"
            f"• Пользователей в системе: <b>{stats['total_users']}</b> (Админов: <b>{stats['total_admins']}</b>)\n"
            f"• Активных сессий: <b>{stats['active_sessions']}</b>\n"
            f"• Активных доступов (Entitlements): <b>{stats['active_entitlements']}</b>\n"
            f"• Оплаченных заказов: <b>{stats['successful_payments']}</b>\n"
            f"• Сформировано SelfCode PDF: <b>{stats['pdf_exports']}</b>\n\n"
            f"📚 <b>Банк вопросов ({q_summary['total_count']} всего):</b>\n"
            f"• CORE Базовые: <b>{q_summary['core_base_count']}</b>\n"
            f"• DEEP Шкалы (Traits): <b>{q_summary['deep_trait_count']}</b>\n"
            f"• State/Context: <b>{q_summary['deep_state_context_count']}</b>\n"
            f"• VFC Выбор ценностей: <b>{q_summary['vfc_count']}</b>\n\n"
            "Выберите нужное действие ниже:"
        )
        await message.answer(text, parse_mode="HTML", reply_markup=get_admin_dashboard_keyboard(forwarding_enabled=fwd_enabled))


@router.callback_query(F.data == "admin:toggle_forwarding")
async def cb_admin_toggle_forwarding(callback: CallbackQuery):
    """Toggle report forwarding to admins."""
    async with AsyncSessionLocal() as db:
        new_state = await toggle_report_forwarding(db)
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
        q_summary = get_question_bank_summary()

        text = (
            "👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА СИСТЕМЫ</b>\n\n"
            f"<b>Администратор:</b> @{user.username or user.telegram_user_id}\n\n"
            f"📊 <b>Общая статистика:</b>\n"
            f"• Пользователей в системе: <b>{stats['total_users']}</b> (Админов: <b>{stats['total_admins']}</b>)\n"
            f"• Активных сессий: <b>{stats['active_sessions']}</b>\n"
            f"• Активных доступов (Entitlements): <b>{stats['active_entitlements']}</b>\n"
            f"• Оплаченных заказов: <b>{stats['successful_payments']}</b>\n"
            f"• Сформировано SelfCode PDF: <b>{stats['pdf_exports']}</b>\n\n"
            f"📚 <b>Банк вопросов ({q_summary['total_count']} всего):</b>\n"
            f"• CORE Базовые: <b>{q_summary['core_base_count']}</b>\n"
            f"• DEEP Шкалы (Traits): <b>{q_summary['deep_trait_count']}</b>\n"
            f"• State/Context: <b>{q_summary['deep_state_context_count']}</b>\n"
            f"• VFC Выбор ценностей: <b>{q_summary['vfc_count']}</b>\n\n"
            "Выберите нужное действие ниже:"
        )

        status_str = "🟢 ВКЛ" if new_state else "🔴 ВЫКЛ"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_dashboard_keyboard(forwarding_enabled=new_state))
        await callback.answer(f"Дублирование отчётов: {status_str}")


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
        fwd_enabled = await is_report_forwarding_enabled(db)

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
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_dashboard_keyboard(forwarding_enabled=fwd_enabled))


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
        if not res_ent.scalars().first():
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


@router.callback_query(F.data == "admin_fastforward")
async def cb_admin_fastforward(callback: CallbackQuery):
    """Generate and send FULL PDF report directly to Admin user for instant testing."""
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username
        )
        if not user.is_admin:
            await callback.answer("⛔ Отказано в доступе.")
            return

        await callback.answer("⏳ Генерируем полный тестовый PDF-отчет...")
        await callback.message.answer("⏳ <b>Генерация полной 12-страничной инструкции к себе V1.3 (FULL)...</b>", parse_mode="HTML")

        session = await get_active_session(db, user.id)
        session_id = session.id if session else f"admin_demo_{user.telegram_user_id}"

        # 1. Obtain full report data
        full_data = await generate_full_report_llm({"session_id": session_id, "mode": "admin_demo"})

        # 2. Export PDF
        pdf_path = generate_pdf_report(session_id, full_data)

        if os.path.exists(pdf_path):
            doc_file = FSInputFile(pdf_path, filename="SelfManual_Full_Report_V1.3.pdf")
            await callback.message.answer_document(
                document=doc_file,
                caption="📄 <b>Ваш тестовый полный PDF-отчет (12 глав + 10 правил + Синтез):</b>",
                parse_mode="HTML"
            )
        else:
            await callback.message.answer("❌ Ошибка при генерации PDF-файла.")


