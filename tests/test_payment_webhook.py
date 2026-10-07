import pytest
import prodamuspy
from sqlalchemy import select
from src.core.config import settings
from src.services.payment import process_prodamus_webhook
from src.db.models import User, AssessmentSession, Payment, AccessEntitlement

SECRET_KEY = "test_webhook_secret_key_123"

@pytest.mark.asyncio
async def test_prodamus_webhook_fallback_prefix_matching(db_session):
    # Setup test user and session
    user = User(telegram_user_id=999888777, chat_id=999888777, username="test_pay_user")
    db_session.add(user)
    await db_session.flush()

    full_session_id = "0ae3f044-1791-4385-b218-000000000000"
    session = AssessmentSession(
        id=full_session_id,
        user_id=user.id,
        phase="CORE_IN_PROGRESS",
        status="ACTIVE"
    )
    db_session.add(session)
    await db_session.commit()

    # Create payload where order_num contains prefix '0ae3f044' and customer_extra contains only prefix
    prodamus = prodamuspy.ProdamusPy(SECRET_KEY)
    payload = {
        "order_id": "49601648",
        "order_num": "SELFMANUAL-0ae3f044-1791385218",
        "sum": "999,00",  # Test comma float string parsing
        "customer_extra": "0ae3f044",  # Truncated or prefix session_id
        "payment_status": "success",
        "payment_type": "SBP"
    }
    signature = prodamus.sign(payload)
    payload["sign"] = signature

    # Override secret key for test execution
    original_key = settings.PRODAMUS_SECRET_KEY
    settings.PRODAMUS_SECRET_KEY = SECRET_KEY
    try:
        success, msg = await process_prodamus_webhook(db_session, payload)
        assert success is True
        assert msg == "Payment verified and DEEP unlocked"

        # Verify DB updates
        updated_session = (await db_session.execute(
            select(AssessmentSession).where(AssessmentSession.id == full_session_id)
        )).scalars().first()
        assert updated_session.phase == "DEEP_UNLOCKED"
        assert updated_session.paid_at is not None

        # Verify Entitlement
        entitlement = (await db_session.execute(
            select(AccessEntitlement).where(AccessEntitlement.session_id == full_session_id)
        )).scalars().first()
        assert entitlement is not None
        assert entitlement.entitlement_type == "FULL_REPORT"

        # Verify Payment amount parsed correctly from "999,00"
        payment = (await db_session.execute(
            select(Payment).where(Payment.session_id == full_session_id)
        )).scalars().first()
        assert payment is not None
        assert payment.amount == 999.0

    finally:
        settings.PRODAMUS_SECRET_KEY = original_key
