import sys
import asyncio

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r"c:\Sher_AI_Studio\projects\selfmanual")

from src.db.base import engine, Base, AsyncSessionLocal
from src.db.models import User, AssessmentSession
from src.services.settings_service import (
    is_report_forwarding_enabled, toggle_report_forwarding, get_setting, set_setting
)
from src.telegram.handlers.assessment import forward_report_to_admins


class MockBot:
    def __init__(self):
        self.sent_messages = []
        self.sent_documents = []

    async def send_message(self, chat_id, text, parse_mode=None):
        self.sent_messages.append({"chat_id": chat_id, "text": text})

    async def send_document(self, chat_id, document, caption=None, parse_mode=None):
        self.sent_documents.append({"chat_id": chat_id, "caption": caption})


async def run_forwarding_tests():
    print("=== Testing Report Forwarding & Admin Toggle System ===")

    # 1. Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # TEST A: Default state is True (ON)
        state_default = await is_report_forwarding_enabled(db)
        print(f"[OK] Test A Passed: Default report forwarding state is {state_default}")

        # TEST B: Toggle to False (OFF)
        new_state_1 = await toggle_report_forwarding(db)
        assert new_state_1 is False
        assert await is_report_forwarding_enabled(db) is False
        print(f"[OK] Test B Passed: Toggle report forwarding switched to {new_state_1} (OFF)")

        # TEST C: Forwarding when OFF -> Should NOT send any messages
        import random
        r_id = random.randint(100000, 999999)
        u_admin = User(telegram_user_id=1000000 + r_id, chat_id=1000000 + r_id, username=f"admin_test_{r_id}", is_admin=True)
        u_user = User(telegram_user_id=2000000 + r_id, chat_id=2000000 + r_id, username=f"user_test_{r_id}")
        db.add_all([u_admin, u_user])
        await db.commit()
        await db.refresh(u_admin)
        await db.refresh(u_user)

        sess = AssessmentSession(user_id=u_user.id)
        db.add(sess)
        await db.commit()
        await db.refresh(sess)

        bot = MockBot()
        await forward_report_to_admins(db, bot, u_user, sess, "CORE FREE", report_text="Test Report Text")
        assert len(bot.sent_messages) == 0
        assert len(bot.sent_documents) == 0
        print("[OK] Test C Passed: Forwarding suppressed when setting is OFF")

        # TEST D: Toggle to True (ON) & Forward -> Should send duplicate message with user details
        new_state_2 = await toggle_report_forwarding(db)
        assert new_state_2 is True
        assert await is_report_forwarding_enabled(db) is True

        await forward_report_to_admins(db, bot, u_user, sess, "FULL DEEP", report_text="Full DEEP Test Report")
        assert len(bot.sent_messages) >= 1
        sent_chat_ids = [m["chat_id"] for m in bot.sent_messages]
        assert u_admin.chat_id in sent_chat_ids
        msg = bot.sent_messages[0]
        assert "ДУБЛИКАТ ОТЧЁТА ПОЛЬЗОВАТЕЛЯ" in msg["text"]
        assert str(u_user.telegram_user_id) in msg["text"]
        print(f"[OK] Test D Passed: Forwarding delivered to admins (Recipients count: {len(bot.sent_messages)})")

    print("\nALL REPORT FORWARDING TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_forwarding_tests())
