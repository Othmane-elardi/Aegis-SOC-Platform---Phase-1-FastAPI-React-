"""Modèle Tenant — organisation cliente dans l'environnement multi-tenant SaaS.

Isolation par tenant appliquée au niveau applicatif (filtrage des requêtes par
`tenant_id`, cf. `api/deps.py::get_current_user` et `api/routes/admin.py`) plutôt
que par schéma DB séparé — approche standard pour un SaaS multi-tenant "pooled".
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

PLANS = ("starter", "professional", "enterprise")


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(String(32), default="professional")
    seats: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
