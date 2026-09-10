import sys
import asyncio
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r"c:\Sher_AI_Studio\projects\selfmanual")

from src.db.base import engine, Base, AsyncSessionLocal
from src.db.models import User, AssessmentSession, PromoCode, AccessEntitlement
from src.services.promo_service import (
    create_promo_code, validate_and_use_promo_code, get_all_promo_codes,
    toggle_promo_code_status, generate_random_promo_code
)


async def run_promo_tests():
    print("=== Testing Promo Code System ===")

    # 1. Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Create test users and sessions
        import random
        r_id = random.randint(100000, 999999)
        u1 = User(telegram_user_id=1000000 + r_id, chat_id=1000000 + r_id, username=f"test_user_1_{r_id}")
        u2 = User(telegram_user_id=2000000 + r_id, chat_id=2000000 + r_id, username=f"test_user_2_{r_id}")
        u3 = User(telegram_user_id=3000000 + r_id, chat_id=3000000 + r_id, username=f"test_user_3_{r_id}")
        db.add_all([u1, u2, u3])
        await db.commit()
        await db.refresh(u1)
        await db.refresh(u2)
        await db.refresh(u3)

        s1 = AssessmentSession(user_id=u1.id, phase="CORE_READY")
        s2 = AssessmentSession(user_id=u2.id, phase="CORE_READY")
        s3 = AssessmentSession(user_id=u3.id, phase="CORE_READY")
        db.add_all([s1, s2, s3])
        await db.commit()
        await db.refresh(s1)
        await db.refresh(s2)
        await db.refresh(s3)

        # TEST A: Create Promo Code with max_uses = 2, duration = 7 days
        code_name = f"LIMITED_{r_id}"
        promo = await create_promo_code(db=db, code=code_name, max_uses=2, duration_days=7, creator_user_id=u1.id)
        assert promo.code == code_name
        assert promo.max_uses == 2
        assert promo.used_count == 0
        assert promo.expires_at is not None
        print(f"[OK] Test A Passed: Created promo '{promo.code}' (max_uses={promo.max_uses}, expires_at={promo.expires_at.strftime('%Y-%m-%d')})")

        # TEST B: Redeem 1st copy by User 1
        ok1, msg1, p1 = await validate_and_use_promo_code(db, code_name, u1.id, s1.id)
        assert ok1 is True
        assert p1.used_count == 1
        await db.refresh(s1)
        assert s1.phase == "DEEP_IN_PROGRESS"
        print(f"[OK] Test B Passed: User 1 redeemed promo. Used count: {p1.used_count}/2, session phase: {s1.phase}")

        # TEST C: Redeem 2nd copy by User 2
        ok2, msg2, p2 = await validate_and_use_promo_code(db, code_name, u2.id, s2.id)
        assert ok2 is True
        assert p2.used_count == 2
        print(f"[OK] Test C Passed: User 2 redeemed promo. Used count: {p2.used_count}/2")

        # TEST D: Redeem 3rd copy by User 3 (Should fail due to usage limit)
        ok3, msg3, p3 = await validate_and_use_promo_code(db, code_name, u3.id, s3.id)
        assert ok3 is False
        assert "лимит" in msg3.lower() or "исчерпан" in msg3.lower()
        print(f"[OK] Test D Passed: User 3 redemption correctly blocked with msg: '{msg3}'")

        # TEST E: Create Expired Code & Test Redemption
        expired_code = f"EXPIRED_{r_id}"
        p_exp = PromoCode(
            code=expired_code,
            max_uses=5,
            used_count=0,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            is_active=True
        )
        db.add(p_exp)
        await db.commit()

        ok_exp, msg_exp, _ = await validate_and_use_promo_code(db, expired_code, u3.id, s3.id)
        assert ok_exp is False
        assert "истёк" in msg_exp.lower() or "срок" in msg_exp.lower()
        print(f"[OK] Test E Passed: Expired promo redemption correctly blocked with msg: '{msg_exp}'")

        # TEST F: Toggle Status (Deactivate promo)
        tog_code = f"TOGGLE_{r_id}"
        p_tog = await create_promo_code(db=db, code=tog_code, max_uses=5, duration_days=30)
        assert p_tog.is_active is True

        p_tog = await toggle_promo_code_status(db, p_tog.id)
        assert p_tog.is_active is False

        ok_tog, msg_tog, _ = await validate_and_use_promo_code(db, tog_code, u3.id, s3.id)
        assert ok_tog is False
        assert "деактивирован" in msg_tog.lower()
        print(f"[OK] Test F Passed: Deactivated promo redemption correctly blocked with msg: '{msg_tog}'")

    print("\nALL PROMO SYSTEM TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_promo_tests())
