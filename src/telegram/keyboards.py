from typing import Dict, Any, Optional
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)


def get_likert_keyboard(q_id: str, client_event_id: str, show_change_last: bool = False) -> InlineKeyboardMarkup:
    """
    Build 1..7 Likert Inline Keyboard for question.
    Format: ans:{q_id}:{score}:{client_event_id}
    """
    buttons = []
    row = []
    for score in range(1, 8):
        row.append(
            InlineKeyboardButton(
                text=str(score),
                callback_data=f"ans:{q_id}:{score}:{client_event_id}"
            )
        )
    buttons.append(row)

    if show_change_last:
        buttons.append([
            InlineKeyboardButton(
                text="↩️ Изменить последний ответ",
                callback_data=f"change_last:{q_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_vfc_keyboard(vfc_id: str, vfc_data: Dict[str, str], client_event_id: str) -> InlineKeyboardMarkup:
    """
    Build 2-option VFC forced-choice keyboard with randomized left/right presentation per session.
    Format: vfc:{vfc_id}:{selected_value}:{client_event_id}
    """
    opt_a = (vfc_data["value_a"], "Выбрать вариант А")
    opt_b = (vfc_data["value_b"], "Выбрать вариант Б")

    options = [opt_a, opt_b]
    # Deterministic or randomized shuffle per client_event_id
    if hash(client_event_id) % 2 == 1:
        options = [opt_b, opt_a]

    buttons = [
        [InlineKeyboardButton(text=f"{options[0][1]}", callback_data=f"vfc:{vfc_id}:{options[0][0]}:{client_event_id}")],
        [InlineKeyboardButton(text=f"{options[1][1]}", callback_data=f"vfc:{vfc_id}:{options[1][0]}:{client_event_id}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_paywall_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Paywall checkout keyboard."""
    buttons = [
        [InlineKeyboardButton(text="💳 ПОЛУЧИТЬ SELFCODE", url=payment_url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_consultation_discount_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for claiming 20% consultation discount."""
    buttons = [
        [InlineKeyboardButton(text="🎁 Записаться со скидкой 20% (SELFCODE)", callback_data="claim_consultation_discount")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def get_consent_keyboard() -> InlineKeyboardMarkup:
    """Consent agreement keyboard."""
    buttons = [
        [InlineKeyboardButton(text="🚀 Начать диагностику CORE", callback_data="accept_consent")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_paywall_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Paywall keyboard for Admin users with direct bypass option."""
    buttons = [
        [InlineKeyboardButton(text="🚀 ПЕРЕЙТИ К ЭТАПУ 2: DEEP (АДМИН-ДОСТУП)", callback_data="admin_start_deep")],
        [InlineKeyboardButton(text="💳 Тестовая ссылка на оплату", url=payment_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_reply_keyboard(is_admin: bool = False, show_pay_button: bool = False) -> ReplyKeyboardMarkup:
    """Persistent bottom ReplyKeyboard with optional Pay button and Admin button."""
    keyboard = [
        [KeyboardButton(text="▶️ Продолжить диагностику"), KeyboardButton(text="📊 Мой прогресс")],
        [KeyboardButton(text="❓ О системе"), KeyboardButton(text="🔄 Начать заново")]
    ]
    if show_pay_button:
        keyboard.insert(0, [KeyboardButton(text="💳 Оплатить полный доступ (DEEP)")])
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_admin_dashboard_keyboard(forwarding_enabled: bool = True) -> InlineKeyboardMarkup:
    """Inline control dashboard for admins."""
    fwd_status = "🟢 ВКЛ" if forwarding_enabled else "🔴 ВЫКЛ"
    buttons = [
        [InlineKeyboardButton(text=f"📫 Дублирование отчётов: {fwd_status}", callback_data="admin:toggle_forwarding")],
        [InlineKeyboardButton(text="🎟 Управление промокодами", callback_data="admin:promos")],
        [InlineKeyboardButton(text="📊 Статистика системы", callback_data="admin:stats")],
        [InlineKeyboardButton(text="📚 Просмотр банка вопросов", callback_data="admin:questions:CORE:1")],
        [InlineKeyboardButton(text="🔓 Выдать доступ пользователю", callback_data="admin:grant_prompt")],
        [InlineKeyboardButton(text="🚀 Запустить этап DEEP", callback_data="admin_start_deep")],
        [InlineKeyboardButton(text="⏩ Сгенерировать FULL отчет (тест)", callback_data="admin_fastforward")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_promo_menu_keyboard() -> InlineKeyboardMarkup:
    """Promo code admin management menu."""
    buttons = [
        [InlineKeyboardButton(text="➕ Создать промокод", callback_data="admin:promo:create")],
        [InlineKeyboardButton(text="📋 Список промокодов", callback_data="admin:promo:list")],
        [InlineKeyboardButton(text="🔙 В главное админ-меню", callback_data="admin:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_promo_uses_keyboard() -> InlineKeyboardMarkup:
    """Preset choices for promo max usages."""
    buttons = [
        [
            InlineKeyboardButton(text="1 шт", callback_data="promo_uses:1"),
            InlineKeyboardButton(text="5 шт", callback_data="promo_uses:5"),
            InlineKeyboardButton(text="10 шт", callback_data="promo_uses:10")
        ],
        [
            InlineKeyboardButton(text="50 шт", callback_data="promo_uses:50"),
            InlineKeyboardButton(text="100 шт", callback_data="promo_uses:100"),
            InlineKeyboardButton(text="✏️ Ввести число", callback_data="promo_uses:custom")
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:promos")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_promo_duration_keyboard() -> InlineKeyboardMarkup:
    """Preset choices for promo duration."""
    buttons = [
        [
            InlineKeyboardButton(text="1 день", callback_data="promo_dur:1"),
            InlineKeyboardButton(text="3 дня", callback_data="promo_dur:3"),
            InlineKeyboardButton(text="7 дней", callback_data="promo_dur:7")
        ],
        [
            InlineKeyboardButton(text="30 дней", callback_data="promo_dur:30"),
            InlineKeyboardButton(text="♾️ Без ограничений", callback_data="promo_dur:0")
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:promos")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_promo_list_keyboard(promos: list) -> InlineKeyboardMarkup:
    """List of promo codes with status toggle buttons."""
    buttons = []
    for p in promos:
        status_icon = "🟢" if p.is_active else "🔴"
        action = "Деактивировать" if p.is_active else "Активировать"
        uses = f"{p.used_count}/{p.max_uses}"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} {p.code} ({uses}) — {action}",
                callback_data=f"admin:promo:toggle:{p.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Создать ещё", callback_data="admin:promo:create")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад в меню промокодов", callback_data="admin:promos")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_questions_nav_keyboard(phase: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Navigation keyboard for question bank browser."""
    buttons = []
    
    # Phase selector row
    phase_row = [
        InlineKeyboardButton(text="CORE" + (" ✅" if phase == "CORE" else ""), callback_data="admin:questions:CORE:1"),
        InlineKeyboardButton(text="DEEP" + (" ✅" if phase == "DEEP" else ""), callback_data="admin:questions:DEEP:1"),
        InlineKeyboardButton(text="VFC" + (" ✅" if phase == "VFC" else ""), callback_data="admin:questions:VFC:1"),
    ]
    buttons.append(phase_row)

    # Page nav row
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin:questions:{phase}:{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"admin:questions:{phase}:{page+1}"))
    buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(text="🔙 Назад в меню админа", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def get_restart_confirm_keyboard() -> InlineKeyboardMarkup:
    """Inline confirmation for restarting assessment."""
    buttons = [
        [
            InlineKeyboardButton(text="⚠️ Да, сбросить и начать заново", callback_data="confirm_restart"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_restart")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

