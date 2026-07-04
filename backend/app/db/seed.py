"""Création des tables + amorçage des comptes, tenants et incidents de démonstration au démarrage."""
import logging
from datetime import datetime

from ..core.config import settings
from ..core.security import hash_password
from ..models.incident import Incident
from ..models.tenant import Tenant
from ..models.user import User
from ..services import demo_data
from .base import Base, SessionLocal, engine

logger = logging.getLogger("aegis.seed")

DEMO_USERS = [
    ("ciso@aegis.local", "ciso1234", "Directrice Sécurité (CISO)", "ciso"),
    ("manager@aegis.local", "manager1234", "Responsable SOC", "soc_manager"),
    ("analyst@aegis.local", "analyst1234", "Analyste N2", "analyst"),
    ("auditor@aegis.local", "auditor1234", "Auditeur Conformité", "auditor"),
]

# Tenants additionnels pour démontrer l'isolation multi-tenant (chaque admin ne
# voit que les comptes de son propre tenant — cf. api/routes/admin.py).
DEMO_TENANTS = [
    ("globex", "Globex Financial Group", "enterprise", 25),
    ("northwind", "Northwind Energy", "professional", 10),
]
DEMO_TENANT_USERS = [
    ("globex", "admin@globex.demo", "admin1234", "Administratrice Plateforme", "admin"),
    ("globex", "ciso@globex.demo", "ciso1234", "CISO Globex", "ciso"),
    ("northwind", "admin@northwind.demo", "admin1234", "Administrateur Plateforme", "admin"),
]


def _seed_incidents_for_tenant(db, tenant_id: str, count: int) -> None:
    """Amorce des incidents *persistants* et actionnables (contrairement aux autres
    modules qui restent générés à la volée) — voir models/incident.py."""
    for inc in demo_data.incidents(count):
        db.add(Incident(
            id=f"{tenant_id.upper()}-{inc['id']}", tenant_id=tenant_id,
            title=inc["title"], description=inc["title"], severity=inc["severity"], status=inc["status"],
            asset=inc["asset"], source_ip=inc["source_ip"], mitre_tactic=inc["mitre_tactic"],
            risk_score=inc["risk_score"], assignee=inc["assignee"] or "", source="demo",
            sla_breached=inc["sla_breached"],
            timeline=[{"timestamp": inc["created_at"], "event": "Incident créé par corrélation SIEM (démo)", "actor": "system"}],
            created_at=datetime.fromisoformat(inc["created_at"]),
        ))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Tenant).count() == 0:
            db.add(Tenant(slug="default", name="Aegis Corp", plan="enterprise", seats=50))
            if settings.DEMO_MODE:
                for slug, name, plan, seats in DEMO_TENANTS:
                    db.add(Tenant(slug=slug, name=name, plan=plan, seats=seats))
            db.commit()

        if db.query(User).count() == 0:
            db.add(User(
                email=settings.FIRST_ADMIN_EMAIL.lower(), full_name="Administrateur Plateforme",
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD), role="admin", tenant_id="default",
            ))
            if settings.DEMO_MODE:
                for email, pwd, name, role in DEMO_USERS:
                    db.add(User(email=email, full_name=name, hashed_password=hash_password(pwd), role=role, tenant_id="default"))
                for tenant_id, email, pwd, name, role in DEMO_TENANT_USERS:
                    db.add(User(email=email, full_name=name, hashed_password=hash_password(pwd), role=role, tenant_id=tenant_id))
            db.commit()
            logger.warning("[seed] Comptes amorcés — admin=%s (changez les mots de passe en production).",
                           settings.FIRST_ADMIN_EMAIL)

        if db.query(Incident).count() == 0 and settings.DEMO_MODE:
            _seed_incidents_for_tenant(db, "default", 40)
            _seed_incidents_for_tenant(db, "globex", 15)
            _seed_incidents_for_tenant(db, "northwind", 8)
            db.commit()
            logger.info("[seed] Incidents de démo amorcés (persistants, actionnables).")
    finally:
        db.close()
