from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, AssessmentSession, Answer, CoreAnalysis
from src.services.config_loader import (
    CORE_BASE_ITEMS, DEEP_TRAIT_ORDER, DEEP_STATE_CONTEXT_ORDER, VFC_ORDER, VFC_PAIRS
)
from src.domain.scoring.core_engine import (
    calculate_core_signals, select_next_adaptive_question, evaluate_core_conflicts
)


async def get_or_create_user(db: AsyncSession, telegram_user_id: int, chat_id: int, language: str = "ru") -> User:
    """Find existing user by Telegram ID or create a new user."""
    stmt = select(User).where(User.telegram_user_id == telegram_user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
            language=language
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_active_session(db: AsyncSession, user_id: str) -> Optional[AssessmentSession]:
    """Retrieve current ACTIVE assessment session for user."""
    stmt = select(AssessmentSession).where(
        AssessmentSession.user_id == user_id,
        AssessmentSession.status == "ACTIVE"
    ).order_by(AssessmentSession.created_at.desc())
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def start_new_session(db: AsyncSession, user_id: str) -> AssessmentSession:
    """Start a brand new assessment session in CONSENT_PENDING phase."""
    session = AssessmentSession(
        user_id=user_id,
        versions_json={
            "PRODUCT_ARCHITECTURE_VERSION": "1.3",
            "QUESTION_BANK_VERSION": "1.2",
            "CORE_BANK_VERSION": "1.0",
            "SCORING_VERSION": "1.2"
        },
        phase="CONSENT_PENDING",
        status="ACTIVE",
        current_position=0
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


# In-memory RAM cache for active session answers to eliminate SQL read latency on every click
_SESSION_ANSWERS_CACHE: Dict[str, Dict[str, int]] = {}


def update_session_answers_cache(session_id: str, question_id: str, raw_answer: int):
    """Instantly record answer in RAM cache."""
    if session_id not in _SESSION_ANSWERS_CACHE:
        _SESSION_ANSWERS_CACHE[session_id] = {}
    _SESSION_ANSWERS_CACHE[session_id][question_id] = raw_answer


def clear_session_answers_cache(session_id: str):
    """Remove session from cache when cancelled or reset."""
    _SESSION_ANSWERS_CACHE.pop(session_id, None)


async def save_answer(
    db: AsyncSession,
    session_id: str,
    question_id: str,
    raw_answer: int,
    phase: str,
    client_event_id: str,
    selected_value: Optional[str] = None,
    response_time_ms: int = 0
) -> Answer:
    """
    Autosave answer with RAM cache + DB write.
    """
    # 1. Update RAM cache instantly (<1ms)
    update_session_answers_cache(session_id, question_id, raw_answer)

    # 2. Persist to DB asynchronously
    stmt = select(Answer).where(
        Answer.session_id == session_id,
        Answer.question_id == question_id
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    if existing:
        existing.raw_answer = raw_answer
        existing.selected_value = selected_value
        existing.response_time_ms = response_time_ms
        existing.client_event_id = client_event_id
        await db.commit()
        return existing

    answer = Answer(
        session_id=session_id,
        question_id=question_id,
        raw_answer=raw_answer,
        selected_value=selected_value,
        phase_answered=phase,
        client_event_id=client_event_id,
        response_time_ms=response_time_ms
    )
    db.add(answer)
    await db.commit()
    return answer


async def get_session_answers_map(db: AsyncSession, session_id: str) -> Dict[str, int]:
    """Get all raw answers dictionary for a session using RAM cache fallback."""
    if session_id in _SESSION_ANSWERS_CACHE:
        return _SESSION_ANSWERS_CACHE[session_id]

    stmt = select(Answer).where(Answer.session_id == session_id)
    res = await db.execute(stmt)
    answers = res.scalars().all()
    answers_map = {ans.question_id: ans.raw_answer for ans in answers}
    _SESSION_ANSWERS_CACHE[session_id] = answers_map
    return answers_map


async def get_next_question_for_session(db: AsyncSession, session: AssessmentSession) -> Optional[Dict[str, Any]]:
    """
    Determine next question to present based on session phase:
    - CORE_IN_PROGRESS: 24 mandatory base items -> 0-6 adaptive items
    - DEEP_IN_PROGRESS: Trait items -> State/Context items -> VFC pairs
    """
    answers_map = await get_session_answers_map(db, session.id)

    if session.phase in ("CORE_IN_PROGRESS", "CONSENT_PENDING"):
        # 1. Base 24 CORE items
        for item in CORE_BASE_ITEMS:
            q_id = item["question_id"]
            if q_id not in answers_map:
                return {
                    "question_id": q_id,
                    "phase": "CORE",
                    "total_progress": len(answers_map),
                    "target_total": 24
                }

        # 2. Adaptive pool check (0..6)
        stmt = select(Answer).where(
            Answer.session_id == session.id,
            Answer.phase_answered == "CORE_ADAPTIVE"
        )
        res = await db.execute(stmt)
        adaptive_answers = res.scalars().all()
        adaptive_history = [ans.question_id for ans in adaptive_answers]

        next_adaptive = select_next_adaptive_question(answers_map, adaptive_history)
        if next_adaptive:
            return {
                "question_id": next_adaptive,
                "phase": "CORE_ADAPTIVE",
                "total_progress": len(answers_map),
                "adaptive_index": len(adaptive_history) + 1,
                "target_total": 30
            }

        # CORE complete! Update session status to CORE_READY
        session.phase = "CORE_READY"
        session.core_completed_at = datetime.utcnow()
        await db.commit()
        return None

    if session.phase == "DEEP_IN_PROGRESS":
        # 1. Master trait questions (excluding already answered in CORE)
        for q_id in DEEP_TRAIT_ORDER:
            if q_id not in answers_map:
                return {
                    "question_id": q_id,
                    "phase": "DEEP",
                    "total_progress": len(answers_map),
                    "target_total": 175
                }

        # 2. State & Context items
        for q_id in DEEP_STATE_CONTEXT_ORDER:
            if q_id not in answers_map:
                return {
                    "question_id": q_id,
                    "phase": "STATE" if q_id in ("Q149", "Q150", "Q151", "Q152", "Q153", "Q154") else "CONTEXT",
                    "total_progress": len(answers_map),
                    "target_total": 175
                }

        # 3. VFC pairs (VFC01..VFC15)
        session.phase = "VFC_IN_PROGRESS"
        await db.commit()

    if session.phase == "VFC_IN_PROGRESS":
        for vfc_id in VFC_ORDER:
            if vfc_id not in answers_map:
                # Find VFC details
                vfc_data = next((v for v in VFC_PAIRS if v["vfc_id"] == vfc_id), None)
                return {
                    "question_id": vfc_id,
                    "phase": "VFC",
                    "vfc_data": vfc_data,
                    "total_progress": len(answers_map),
                    "target_total": 175
                }

        # Assessment completed!
        session.phase = "FULL_ASSESSMENT_COMPLETED"
        session.deep_completed_at = datetime.utcnow()
        await db.commit()
        return None

    return None
