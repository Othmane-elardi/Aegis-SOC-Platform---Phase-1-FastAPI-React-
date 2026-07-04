"""Création des tables + amorçage des comptes de démonstration au démarrage."""
import logging

from ..core.config import settings
from ..core.security import hash_password
from ..models.user import User
from .base import Base, SessionLocal, engine

logger = logging.getLogger("aegis.seed")

DEMO_USERS = [
    ("ciso@aegis.local", "ciso1234", "Directrice Sécurité (CISO)", "ciso"),
    ("manager@aegis.local", "manager1234", "Responsable SOC", "soc_manager"),
    ("analyst@aegis.local", "analyst1234", "Analyste N2", "analyst"),
    ("auditor@aegis.local", "auditor1234", "Auditeur Conformité", "auditor"),
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(
                email=settings.FIRST_ADMIN_EMAIL.lower(), full_name="Administrateur Plateforme",
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD), role="admin",
            ))
            if settings.DEMO_MODE:
                for email, pwd, name, role in DEMO_USERS:
                    db.add(User(email=email, full_name=name, hashed_password=hash_password(pwd), role=role))
            db.commit()
            logger.warning("[seed] Comptes amorcés — admin=%s (changez les mots de passe en production).",
                           settings.FIRST_ADMIN_EMAIL)
    finally:
        db.close()
