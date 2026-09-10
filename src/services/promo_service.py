import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from src.db.models import PromoCode, AccessEntitlement, AssessmentSession
from src.core.config import settings


def generate_random_promo_code(prefix: str = "SELFCODE") -> str:
    """Generate a clean, readable random promo code."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


async def create_promo_code(
    db: AsyncSession,
    code: str,
    max_uses: int = 1,
    duration_days: Optional[int] = None,
    creator_user_id: Optional[str] = None
) -> PromoCode:
    """Create a new promo code record in the database."""
    clean_code = code.strip().upper()
    
    expires_at = None
    if duration_days and duration_days > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
        
    promo = PromoCode(
        code=clean_code,
        max_uses=max_uses,
        used_count=0,
        duration_days=duration_days,
        expires_at=expires_at,
        is_active=True,
        created_by_user_id=creator_user_id
    )
    db.add(promo)
    await db.commit()
    await db.refresh(promo)
    return promo


async def get_all_promo_codes(db: AsyncSession) -> List[PromoCode]:
    """Get all promo codes ordered by creation date descending."""
    result = await db.execute(select(PromoCode).order_by(desc(PromoCode.created_at)))
    return list(result.scalars().all())


async def toggle_promo_code_status(db: AsyncSession, promo_id: str) -> Optional[PromoCode]:
    """Toggle is_active status of a promo code."""
    result = await db.execute(select(PromoCode).where(PromoCode.id == promo_id))
    promo = result.scalar_one_or_none()
    if promo:
        promo.is_active = not promo.is_active
        await db.commit()
        await db.refresh(promo)
    return promo


async def validate_and_use_promo_code(
    db: AsyncSession,
    code_str: str,
    user_id: str,
    session_id: str
) -> Tuple[bool, str, Optional[PromoCode]]:
    """
    Validates code_str and if valid, grants AccessEntitlement and updates AssessmentSession phase.
    Returns (success: bool, message: str, promo: Optional[PromoCode]).
    """
    clean_code = code_str.strip().upper()
    
    # 1. Check fallback test promo code in settings
    fallback_promo = getattr(settings, "TEST_GROUP_PROMO", "TESTGROUP2026")
    if clean_code == fallback_promo.upper():
        # Check existing entitlement
        ent_q = await db.execute(
            select(AccessEntitlement).where(
                AccessEntitlement.user_id == user_id,
                AccessEntitlement.session_id == session_id,
                AccessEntitlement.status == "ACTIVE"
            )
        )
        if not ent_q.scalar_one_or_none():
            ent = AccessEntitlement(
                user_id=user_id,
                session_id=session_id,
                entitlement_type="FULL_REPORT",
                source="promo:TESTGROUP"
            )
            db.add(ent)
            
        sess_q = await db.execute(select(AssessmentSession).where(AssessmentSession.id == session_id))
        session = sess_q.scalar_one_or_none()
        if session and session.phase in ("CORE_READY", "CORE_IN_PROGRESS"):
            session.phase = "DEEP_IN_PROGRESS"
            
        await db.commit()
        return True, "🎉 **Промокод успешно активирован!** Вам предоставлен полный доступ к SelfCode DEEP.", None

    # 2. Check DB promo codes
    result = await db.execute(select(PromoCode).where(PromoCode.code == clean_code))
    promo = result.scalar_one_or_none()

    if not promo:
        return False, "❌ **Неверный промокод.** Пожалуйста, проверьте правильность написания.", None

    if not promo.is_active:
        return False, "⚠️ **Этот промокод был деактивирован.**", promo

    if promo.expires_at:
        # Convert to timezone aware UTC if naive
        exp = promo.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > exp:
            return False, f"⏰ **Срок действия этого промокода истёк ({exp.strftime('%d.%m.%Y')}).**", promo

    if promo.used_count >= promo.max_uses:
        return False, f"🚫 **Лимит использования этого промокода исчерпан ({promo.used_count}/{promo.max_uses}).**", promo

    # 3. Apply promo code access
    # Check if entitlement already granted
    ent_q = await db.execute(
        select(AccessEntitlement).where(
            AccessEntitlement.user_id == user_id,
            AccessEntitlement.session_id == session_id,
            AccessEntitlement.status == "ACTIVE"
        )
    )
    if not ent_q.scalar_one_or_none():
        ent = AccessEntitlement(
            user_id=user_id,
            session_id=session_id,
            entitlement_type="FULL_REPORT",
            source=f"promo:{clean_code}"
        )
        db.add(ent)

    # Increment used count
    promo.used_count += 1

    # Unlock DEEP phase in assessment session
    sess_q = await db.execute(select(AssessmentSession).where(AssessmentSession.id == session_id))
    session = sess_q.scalar_one_or_none()
    if session and session.phase in ("CORE_READY", "CORE_IN_PROGRESS"):
        session.phase = "DEEP_IN_PROGRESS"

    await db.commit()
    await db.refresh(promo)

    return True, "🎉 **Промокод успешно активирован!** Вам предоставлен полный доступ к SelfCode DEEP.", promo
