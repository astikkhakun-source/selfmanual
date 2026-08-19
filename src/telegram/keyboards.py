import random
from typing import Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
    opt_a = (vfc_data["value_a"], vfc_data["text_a"])
    opt_b = (vfc_data["value_b"], vfc_data["text_b"])

    options = [opt_a, opt_b]
    # Deterministic or randomized shuffle per client_event_id
    if hash(client_event_id) % 2 == 1:
        options = [opt_b, opt_a]

    buttons = [
        [InlineKeyboardButton(text=f"А: {options[0][1]}", callback_data=f"vfc:{vfc_id}:{options[0][0]}:{client_event_id}")],
        [InlineKeyboardButton(text=f"Б: {options[1][1]}", callback_data=f"vfc:{vfc_id}:{options[1][0]}:{client_event_id}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_paywall_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Paywall checkout keyboard."""
    buttons = [
        [InlineKeyboardButton(text="💳 ПОЛУЧИТЬ ПОЛНУЮ ИНСТРУКЦИЮ", url=payment_url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_consent_keyboard() -> InlineKeyboardMarkup:
    """Consent agreement keyboard."""
    buttons = [
        [InlineKeyboardButton(text="✅ Принимаю условия и начинаю", callback_data="accept_consent")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
