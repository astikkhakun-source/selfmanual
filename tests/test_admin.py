import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.db.base import Base
from src.db.models import User, AssessmentSession, AccessEntitlement
from src.services.assessment import get_or_create_user, start_new_session
from src.services.admin import get_admin_stats, grant_user_entitlement, list_questions_by_phase, get_question_bank_summary


async def _get_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return sm()


@pytest.mark.asyncio
async def test_admin_auto_grant_and_entitlement():
    """Test that configured admin usernames automatically get is_admin=True and active entitlement."""
    session = await _get_test_session()
    async with session:
        # 1. Create user with admin handle @AstiHakun
        user_asti = await get_or_create_user(
            session,
            telegram_user_id=111111111,
            chat_id=111111111,
            username="AstiHakun"
        )
        assert user_asti.is_admin is True

        # 2. Create active session and ensure entitlement is created
        sess = await start_new_session(session, user_asti.id)
        user_asti = await get_or_create_user(
            session,
            telegram_user_id=111111111,
            chat_id=111111111,
            username="AstiHakun"
        )

        stmt_ent = select(AccessEntitlement).where(AccessEntitlement.session_id == sess.id)
        res_ent = await session.execute(stmt_ent)
        ent = res_ent.scalars().first()
        assert ent is not None
        assert ent.source == "admin"


@pytest.mark.asyncio
async def test_sherlockdxb_admin_auto_grant():
    """Test that @sherlockdxb gets admin rights automatically."""
    session = await _get_test_session()
    async with session:
        user_sherlock = await get_or_create_user(
            session,
            telegram_user_id=222222222,
            chat_id=222222222,
            username="sherlockdxb"
        )
        assert user_sherlock.is_admin is True


@pytest.mark.asyncio
async def test_admin_stats_and_questions_list():
    """Test get_admin_stats and list_questions_by_phase."""
    session = await _get_test_session()
    async with session:
        stats = await get_admin_stats(session)
        assert "total_users" in stats
        assert "total_admins" in stats

        summary = get_question_bank_summary()
        assert summary["total_count"] > 100

        items, total = list_questions_by_phase("CORE", page=1, page_size=5)
        assert len(items) == 5
        assert total >= 24


@pytest.mark.asyncio
async def test_grant_user_entitlement_service():
    """Test granting admin entitlement to a regular user via service."""
    session = await _get_test_session()
    async with session:
        regular_user = await get_or_create_user(
            session,
            telegram_user_id=333333333,
            chat_id=333333333,
            username="regular_user"
        )
        assert regular_user.is_admin is False

        success, msg = await grant_user_entitlement(session, "regular_user")
        assert success is True
        assert "успешно предоставлены" in msg

        await session.refresh(regular_user)
        assert regular_user.is_admin is True
