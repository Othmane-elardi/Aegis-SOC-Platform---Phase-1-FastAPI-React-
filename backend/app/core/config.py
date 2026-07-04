"""Configuration centralisée (12-factor : tout vient de l'environnement).

SQLite par défaut → l'API démarre sans aucune dépendance externe. En production,
définir DATABASE_URL vers Postgres (ex. postgresql+psycopg://user:pass@host/db).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Application ───────────────────────────────────────────
    PROJECT_NAME: str = "Aegis SOC Platform"
    API_V1: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = True

    # ── Sécurité ──────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE-ME-generate-a-long-random-value"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 8 * 60
    ALGORITHM: str = "HS256"

    # ── Base de données ───────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./aegis.db"

    # ── CORS (origines du frontend React) ─────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ── Compte admin amorcé au premier démarrage ──────────────
    FIRST_ADMIN_EMAIL: str = "admin@aegis.local"
    FIRST_ADMIN_PASSWORD: str = "admin1234"

    # ── Mode démo (données synthétiques réalistes) ────────────
    DEMO_MODE: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
