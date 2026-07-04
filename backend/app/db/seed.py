"""Création des tables + amorçage des comptes et tenants de démonstration au démarrage."""
import logging

from ..core.config import settings
from ..core.security import hash_password
from ..models.tenant import Tenant
from ..models.user import User
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
    finally:
        db.close()
