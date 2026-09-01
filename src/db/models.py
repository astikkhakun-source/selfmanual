import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, Float, BigInteger, DateTime, ForeignKey, Text, JSON, Boolean, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(10), default="ru")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sessions: Mapped[list["AssessmentSession"]] = relationship("AssessmentSession", back_populates="user", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")
    entitlements: Mapped[list["AccessEntitlement"]] = relationship("AccessEntitlement", back_populates="user")


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consent_version: Mapped[str] = mapped_column(String(20), default="1.0")
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    versions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    phase: Mapped[str] = mapped_column(String(30), default="CORE_IN_PROGRESS")  # CORE_IN_PROGRESS, DEEP_UNLOCKED, DEEP_IN_PROGRESS, VFC_IN_PROGRESS, COMPLETED
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")  # ACTIVE, COMPLETED, ABANDONED
    current_position: Mapped[int] = mapped_column(Integer, default=0)
    core_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deep_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    answers: Mapped[list["Answer"]] = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    core_analysis: Mapped[Optional["CoreAnalysis"]] = relationship("CoreAnalysis", back_populates="session", uselist=False)
    analysis_runs: Mapped[list["AnalysisRun"]] = relationship("AnalysisRun", back_populates="session")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_answer: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..7 for trait/state/context or win option for VFC
    selected_value: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # For VFC value name
    phase_answered: Mapped[str] = mapped_column(String(20), nullable=False)  # CORE, CORE_ADAPTIVE, DEEP, STATE, CONTEXT, VFC
    response_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    display_position: Mapped[int] = mapped_column(Integer, default=0)
    client_event_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("session_id", "client_event_id", name="uq_session_client_event"),
        UniqueConstraint("session_id", "question_id", name="uq_session_question"),
    )

    session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="answers")


class CoreAnalysis(Base):
    __tablename__ = "core_analysis"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    core_engine_version: Mapped[str] = mapped_column(String(20), default="1.0")
    signals_json: Mapped[dict] = mapped_column(JSON, default=dict)
    conflicts_json: Mapped[dict] = mapped_column(JSON, default=dict)
    resources_json: Mapped[dict] = mapped_column(JSON, default=dict)
    adaptive_history_json: Mapped[list] = mapped_column(JSON, default=list)
    top_conflict_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    top_resource_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    report_mode: Mapped[str] = mapped_column(String(30), default="CONFLICT")  # CONFLICT, CONFIGURATION_ONLY
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="core_analysis")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False)
    engine_versions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    immutable_profile_snapshot_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED")  # PENDING, COMPLETED, FAILED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="analysis_runs")
    scale_scores: Mapped[list["ScaleScore"]] = relationship("ScaleScore", back_populates="analysis_run", cascade="all, delete-orphan")
    findings: Mapped[list["Finding"]] = relationship("Finding", back_populates="analysis_run", cascade="all, delete-orphan")
    system_cycles: Mapped[list["SystemCycle"]] = relationship("SystemCycle", back_populates="analysis_run", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="analysis_run")
    pdf_exports: Mapped[list["PDFExport"]] = relationship("PDFExport", back_populates="analysis_run")


class ScaleScore(Base):
    __tablename__ = "scale_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    scale_id: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_mean: Mapped[float] = mapped_column(Float, nullable=False)
    normalized: Mapped[float] = mapped_column(Float, nullable=False)  # 0..100
    rank: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..46
    delta: Mapped[float] = mapped_column(Float, nullable=False)  # normalized - median
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    flags_json: Mapped[list] = mapped_column(JSON, default=list)

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="scale_scores")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    finding_id: Mapped[str] = mapped_column(String(50), nullable=False)  # P01..P37 or C01..C12
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # PATTERN, CONFLICT, RESOURCE
    cluster: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")  # ACTIVE, SUPPRESSED, DOWNGRADED
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    priority: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_json: Mapped[list] = mapped_column(JSON, default=list)
    counter_evidence_json: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="findings")


class SystemCycle(Base):
    __tablename__ = "system_cycles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    cycle_id: Mapped[str] = mapped_column(String(50), nullable=False)
    systemicity_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="system_cycles")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(20), nullable=False)  # CORE_FREE, FULL
    prompt_version: Mapped[str] = mapped_column(String(20), default="1.3")
    schema_version: Mapped[str] = mapped_column(String(20), default="1.3")
    model_version: Mapped[str] = mapped_column(String(50), default="gpt-4o")
    report_json: Mapped[dict] = mapped_column(JSON, default=dict)
    generation_status: Mapped[str] = mapped_column(String(20), default="SUCCESS")  # PENDING, SUCCESS, FAILED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis_run: Mapped[Optional["AnalysisRun"]] = relationship("AnalysisRun", back_populates="reports")


class PDFExport(Base):
    __tablename__ = "pdf_exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, READY, FAILED, SENT
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis_run: Mapped["AnalysisRun"] = relationship("AnalysisRun", back_populates="pdf_exports")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, PAID, FAILED, REFUNDED
    prodamus_order_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="payments")


class AccessEntitlement(Base):
    __tablename__ = "access_entitlements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False)
    entitlement_type: Mapped[str] = mapped_column(String(30), default="FULL_REPORT")
    source: Mapped[str] = mapped_column(String(30), default="payment")  # payment, promo, admin
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, REVOKED
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="entitlements")
