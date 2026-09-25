import logging
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import verify_prodamus_signature
from src.db.models import User, AssessmentSession, Payment, AccessEntitlement

logger = logging.getLogger(__name__)


def create_prodamus_payment_link(user_id: str, session_id: str, amount: float = 999.0) -> str:
    """
    Generate Prodamus checkout URL with session_id as order_id metadata.
    """
    order_id = f"SELFMANUAL-{session_id[:8]}-{int(datetime.utcnow().timestamp())}"
    
    params = {
        "do": "pay",
        "order_id": order_id,
        "sum": f"{amount:.2f}",
        "customer_extra": session_id,
        "products[0][name]": "SelfCode полная диагностика",
        "products[0][price]": f"{amount:.2f}",
        "products[0][quantity]": "1",
        "sys": "selfmanual_telegram_v1_3"
    }

    base_url = settings.PRODAMUS_PAYMENT_URL.rstrip("/")
    return f"{base_url}/?{urllib.parse.urlencode(params)}"


async def process_prodamus_webhook(db: AsyncSession, payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Idempotent Prodamus webhook callback handler.
    Validates HMAC signature, records payment, grants entitlement, unlocks DEEP phase,
    and sends an instant notification to the user in Telegram.
    """
    logger.info(f"Received Prodamus webhook callback payload: {payload}")

    # 1. Verify signature
    if not verify_prodamus_signature(payload, settings.PRODAMUS_SECRET_KEY):
        logger.warning(f"Prodamus signature verification failed for payload keys: {list(payload.keys())}")
        return False, "Invalid signature"

    payment_status = str(payload.get("payment_status", "")).lower()
    order_id = payload.get("order_id") or payload.get("order_num")
    session_id = payload.get("customer_extra") or payload.get("customer_number")

    if not session_id:
        logger.warning("Prodamus webhook payload missing customer_extra / session_id")
        return False, "Missing session_id in payload"

    # Only process successful payments
    if payment_status not in ("success", "paid", "1", "true"):
        logger.info(f"Ignored non-success payment status: {payment_status}")
        return True, f"Ignored non-success status: {payment_status}"

    # Find assessment session
    stmt = select(AssessmentSession).where(AssessmentSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalars().first()

    if not session:
        logger.error(f"Session {session_id} not found for Prodamus payment")
        return False, f"Session {session_id} not found"

    # 2. Check idempotent entitlement
    stmt_ent = select(AccessEntitlement).where(
        AccessEntitlement.session_id == session.id,
        AccessEntitlement.entitlement_type == "FULL_REPORT"
    )
    res_ent = await db.execute(stmt_ent)
    existing_ent = res_ent.scalars().first()

    if existing_ent:
        logger.info(f"Entitlement already granted for session {session_id}")
        return True, "Entitlement already granted"

    # 3. Create or update payment record
    stmt_pay = select(Payment).where(Payment.prodamus_order_id == order_id)
    res_pay = await db.execute(stmt_pay)
    payment = res_pay.scalars().first()

    if not payment:
        payment = Payment(
            user_id=session.user_id,
            session_id=session.id,
            amount=float(payload.get("sum", 999.0)),
            status="PAID",
            prodamus_order_id=order_id,
            provider_payment_id=payload.get("payment_id"),
            payment_method=payload.get("payment_type")
        )
        db.add(payment)
    else:
        payment.status = "PAID"

    # 4. Grant access entitlement
    entitlement = AccessEntitlement(
        user_id=session.user_id,
        session_id=session.id,
        entitlement_type="FULL_REPORT",
        source="payment",
        status="ACTIVE"
    )
    db.add(entitlement)

    # 5. Transition session phase to DEEP_UNLOCKED
    session.phase = "DEEP_UNLOCKED"
    session.paid_at = datetime.utcnow()

    await db.commit()
    logger.info(f"Prodamus payment successfully verified for user {session.user_id}, session {session.id}")

    # 6. Push real-time Telegram notification to user
    try:
        if settings.TELEGRAM_BOT_TOKEN:
            from aiogram import Bot
            from src.telegram.keyboards import get_main_reply_keyboard

            stmt_u = select(User).where(User.id == session.user_id)
            res_u = await db.execute(stmt_u)
            user = res_u.scalars().first()
            if user:
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                target_chat = user.chat_id or user.telegram_user_id
                reply_kb = get_main_reply_keyboard(is_admin=user.is_admin, show_pay_button=False)
                pay_success_text = (
                    "🎉 <b>Оплата успешно подтверждена!</b>\n\n"
                    "Вам открыт полный доступ к <b>Этапу 2 (DEEP)</b>.\n"
                    "Нажмите кнопку <b>«▶️ Продолжить диагностику»</b> ниже, чтобы перейти к исследованию ваших 46 шкал личности!"
                )
                await bot.send_message(chat_id=target_chat, text=pay_success_text, parse_mode="HTML", reply_markup=reply_kb)
                await bot.session.close()
    except Exception as notify_err:
        logger.error(f"Failed to send Telegram notification after Prodamus webhook: {notify_err}")

    return True, "Payment verified and DEEP unlocked"

