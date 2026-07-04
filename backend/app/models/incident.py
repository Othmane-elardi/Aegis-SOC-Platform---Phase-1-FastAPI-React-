"""Modèle Incident — cycle de vie réel et persistant (contrairement aux autres
modules qui restent en données de démo générées à la volée). Un incident peut
provenir d'une génération de démo initiale, d'une alerte Wazuh réelle ingérée,
ou d'une création manuelle par un analyste (voir `source`)."""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

VALID_STATUSES = ("new", "investigating", "contained", "resolved")
VALID_SOURCES = ("demo", "wazuh", "manual")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    alert_id: Mapped[str] = mapped_column(String(160), default="", index=True)
    title: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(16), default="medium")
    status: Mapped[str] = mapped_column(String(24), default="new")
    verdict: Mapped[str] = mapped_column(String(24), default="")
    asset: Mapped[str] = mapped_column(String(120), default="")
    source_ip: Mapped[str] = mapped_column(String(64), default="")
    mitre_tactic: Mapped[str] = mapped_column(String(120), default="")
    mitre_id: Mapped[str] = mapped_column(String(16), default="")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    assignee: Mapped[str] = mapped_column(String(255), default="")
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    ai_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    threat_intel: Mapped[dict] = mapped_column(JSON, default=dict)
    active_response: Mapped[dict] = mapped_column(JSON, default=dict)
    timeline: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[list] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(16), default="demo")
    sla_breached: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
