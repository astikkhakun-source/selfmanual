import asyncio
import sys
import os
from sqlalchemy import select, update, text

# Add parent dir to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.base import AsyncSessionLocal, engine, Base
from src.db.models import User, AssessmentSession, AccessEntitlement
from src.core.config import settings


async def main():
    print("=== Selfmanual Admin Grant Utility ===")
    
    # 1. Initialize DB tables & run column migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;"))
        except Exception as mig_err:
            print(f"[INFO] Migration note: {mig_err}")

    target_handles = sys.argv[1:] if len(sys.argv) > 1 else settings.admin_usernames_list
    print(f"Target admin handles to verify/grant: {target_handles}")

    async with AsyncSessionLocal() as db:
        for handle in target_handles:
            clean_handle = handle.lstrip("@").lower()
            stmt = select(User).where(User.username.ilike(clean_handle))
            res = await db.execute(stmt)
            user = res.scalar_one_or_none()

            if not user:
                print(f"[INFO] User @{clean_handle} not yet registered in DB (will auto-grant admin upon first /start).")
                continue

            user.is_admin = True
            print(f"[SUCCESS] Updated user @{user.username} (ID: {user.telegram_user_id}) to is_admin=True.")

            # Grant entitlement for active session if present
            stmt_sess = select(AssessmentSession).where(
                AssessmentSession.user_id == user.id,
                AssessmentSession.status == "ACTIVE"
            ).order_by(AssessmentSession.created_at.desc())
            res_sess = await db.execute(stmt_sess)
            session = res_sess.scalar_one_or_none()

            if session:
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
                    print(f"  └ Granted FULL_REPORT entitlement for active session {session.id[:8]}.")

        await db.commit()
    print("=== Admin update complete. ===")


if __name__ == "__main__":
    asyncio.run(main())
