import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import verify_prodamus_signature
from src.db.models import User, AssessmentSession, Payment, AccessEntitlement


def create_prodamus_payment_link(user_id: str, session_id: str, amount: float = 1990.0) -> str:
    """
    Generate Prodamus checkout URL with session_id as order_id metadata.
    """
    order_id = f"SELFMANUAL-{session_id[:8]}-{int(datetime.utcnow().timestamp())}"
    
    params = {
        "do": "pay",
        "order_id": order_id,
        "sum": f"{amount:.2f}",
        "currency": "RUB",
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
    Validates HMAC signature, records payment, grants entitlement, and unlocks DEEP phase.
    """
    # 1. Verify signature
    if not verify_prodamus_signature(payload, settings.PRODAMUS_SECRET_KEY):
        return False, "Invalid signature"

    payment_status = str(payload.get("payment_status", "")).lower()
    order_id = payload.get("order_id") or payload.get("order_num")
    session_id = payload.get("customer_extra") or payload.get("customer_number")

    if not session_id:
        return False, "Missing session_id in payload"

    # Only process successful payments
    if payment_status not in ("success", "paid", "1", "true"):
        return True, f"Ignored non-success status: {payment_status}"

    # Find assessment session
    stmt = select(AssessmentSession).where(AssessmentSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalars().first()

    if not session:
        return False, f"Session {session_id} not found"

    # 2. Check idempotent entitlement
    stmt_ent = select(AccessEntitlement).where(
        AccessEntitlement.session_id == session.id,
        AccessEntitlement.entitlement_type == "FULL_REPORT"
    )
    res_ent = await db.execute(stmt_ent)
    existing_ent = res_ent.scalars().first()

    if existing_ent:
        # Entitlement already active, return idempotent success
        return True, "Entitlement already granted"

    # 3. Create or update payment record
    stmt_pay = select(Payment).where(Payment.prodamus_order_id == order_id)
    res_pay = await db.execute(stmt_pay)
    payment = res_pay.scalars().first()

    if not payment:
        payment = Payment(
            user_id=session.user_id,
            session_id=session.id,
            amount=float(payload.get("sum", 1990.0)),
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
    return True, "Payment verified and DEEP unlocked"
