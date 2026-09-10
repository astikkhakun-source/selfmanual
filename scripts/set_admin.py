import asyncio
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
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
        allowed_ids = settings.admin_ids_list
        allowed_usernames = settings.admin_usernames_list

        res = await db.execute(select(User))
        all_users = res.scalars().all()

        for user in all_users:
            is_adm = bool((user.telegram_user_id in allowed_ids) or (user.username and user.username.lower() in allowed_usernames))
            if user.is_admin != is_adm:
                user.is_admin = is_adm
                print(f"[UPDATE] User ID {user.telegram_user_id} (@{user.username or 'no_username'}) -> is_admin={is_adm}")
            elif is_adm:
                print(f"[VERIFIED] Admin User ID {user.telegram_user_id} (@{user.username or 'no_username'}) is_admin=True")

            # Grant entitlement for active session if present
            stmt_sess = select(AssessmentSession).where(
                AssessmentSession.user_id == user.id,
                AssessmentSession.status == "ACTIVE"
            ).order_by(AssessmentSession.created_at.desc())
            res_sess = await db.execute(stmt_sess)
            session = res_sess.scalars().first()

            if session:
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
                    print(f"  └ Granted FULL_REPORT entitlement for active session {session.id[:8]}.")

        await db.commit()
    print("=== Admin update complete. ===")


if __name__ == "__main__":
    asyncio.run(main())
