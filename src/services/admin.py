from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, AssessmentSession, Payment, AccessEntitlement, PDFExport, Answer
from src.services.config_loader import (
    CORE_BASE_ITEMS, DEEP_TRAIT_ORDER, DEEP_STATE_CONTEXT_ORDER, VFC_ORDER, VFC_PAIRS,
    get_question_info
)


async def get_admin_stats(db: AsyncSession) -> Dict[str, Any]:
    """Retrieve comprehensive system statistics for Admin Dashboard."""
    # 1. Total users and admins count
    res_users = await db.execute(select(func.count(User.id)))
    total_users = res_users.scalar() or 0

    res_admins = await db.execute(select(func.count(User.id)).where(User.is_admin == True))
    total_admins = res_admins.scalar() or 0

    # 2. Session phase breakdown
    stmt_phases = select(AssessmentSession.phase, func.count(AssessmentSession.id)).group_by(AssessmentSession.phase)
    res_phases = await db.execute(stmt_phases)
    phase_counts = {row[0]: row[1] for row in res_phases.all()}

    res_active = await db.execute(select(func.count(AssessmentSession.id)).where(AssessmentSession.status == "ACTIVE"))
    active_sessions = res_active.scalar() or 0

    # 3. Entitlements count
    res_ent = await db.execute(select(func.count(AccessEntitlement.id)).where(AccessEntitlement.status == "ACTIVE"))
    active_entitlements = res_ent.scalar() or 0

    # 4. Total payments
    res_pay = await db.execute(select(func.count(Payment.id)).where(Payment.status == "PAID"))
    successful_payments = res_pay.scalar() or 0

    # 5. PDF exports generated
    res_pdf = await db.execute(select(func.count(PDFExport.id)))
    pdf_exports = res_pdf.scalar() or 0

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "active_sessions": active_sessions,
        "phase_breakdown": phase_counts,
        "active_entitlements": active_entitlements,
        "successful_payments": successful_payments,
        "pdf_exports": pdf_exports
    }


async def grant_user_entitlement(db: AsyncSession, identifier: str) -> Tuple[bool, str]:
    """Grant full admin entitlement & status to a target user by username or Telegram user ID."""
    clean_id = identifier.strip().lstrip("@")

    user: Optional[User] = None
    if clean_id.isdigit():
        tg_id = int(clean_id)
        stmt = select(User).where(User.telegram_user_id == tg_id)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
    else:
        stmt = select(User).where(func.lower(User.username) == clean_id.lower())
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

    if not user:
        return False, f"Пользователь «{identifier}» не найден в базе данных."

    user.is_admin = True

    # Find or activate session entitlement
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
        existing_ent = res_ent.scalar_one_or_none()

        if not existing_ent:
            ent = AccessEntitlement(
                user_id=user.id,
                session_id=session.id,
                entitlement_type="FULL_REPORT",
                source="admin",
                status="ACTIVE"
            )
            db.add(ent)

        if session.phase == "CORE_READY":
            session.phase = "DEEP_UNLOCKED"

    await db.commit()
    return True, f"✅ Права администратора и полный доступ к DEEP успешно предоставлены пользователю @{user.username or user.telegram_user_id}!"


def get_question_bank_summary() -> Dict[str, Any]:
    """Return overview of all items in question bank."""
    return {
        "core_base_count": len(CORE_BASE_ITEMS),
        "deep_trait_count": len(DEEP_TRAIT_ORDER),
        "deep_state_context_count": len(DEEP_STATE_CONTEXT_ORDER),
        "vfc_count": len(VFC_ORDER),
        "total_count": len(CORE_BASE_ITEMS) + len(DEEP_TRAIT_ORDER) + len(DEEP_STATE_CONTEXT_ORDER) + len(VFC_ORDER)
    }


def list_questions_by_phase(phase: str = "CORE", page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    """List questions with text pagination for admin inspection."""
    items: List[Dict[str, Any]] = []

    if phase.upper() == "CORE":
        q_ids = [item["question_id"] for item in CORE_BASE_ITEMS]
    elif phase.upper() == "DEEP":
        q_ids = DEEP_TRAIT_ORDER + DEEP_STATE_CONTEXT_ORDER
    elif phase.upper() == "VFC":
        q_ids = VFC_ORDER
    else:
        q_ids = [item["question_id"] for item in CORE_BASE_ITEMS] + DEEP_TRAIT_ORDER + DEEP_STATE_CONTEXT_ORDER + VFC_ORDER

    total = len(q_ids)
    start = (page - 1) * page_size
    end = start + page_size
    page_qids = q_ids[start:end]

    for qid in page_qids:
        if qid.startswith("VFC"):
            vfc_data = next((v for v in VFC_PAIRS if v["vfc_id"] == qid), {})
            items.append({
                "question_id": qid,
                "type": "VFC",
                "text_ru": f"A: {vfc_data.get('text_a', '')} | B: {vfc_data.get('text_b', '')}"
            })
        else:
            q_info = get_question_info(qid)
            items.append({
                "question_id": qid,
                "type": "LIKERT_1_7",
                "scale_id": q_info.get("scale_id", ""),
                "direction": q_info.get("direction", "+"),
                "text_ru": q_info.get("text_ru", f"Вопрос {qid}")
            })

    return items, total
