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
    # DEMO_MODE=true (défaut) : SIEM/SOAR/Copilot alimentés par des données
    # synthétiques, aucun appel réseau vers Wazuh/ELK/IA/VirusTotal. Passer à
    # false pour une intégration réelle — voir les variables ci-dessous,
    # toutes à définir dans backend/.env (jamais commité, voir .gitignore).
    DEMO_MODE: bool = True

    # ── Elasticsearch / Wazuh (intégration SIEM réelle) ───────
    ES_HOST: str = "https://localhost:9200"
    ES_USER: str = ""
    ES_PASS: str = ""
    WAZUH_HOST: str = "https://localhost"
    WAZUH_USER: str = ""
    WAZUH_PASS: str = ""
    # Niveau de sévérité Wazuh (0-15) à partir duquel une réponse active
    # automatique (blocage IP, etc.) peut être déclenchée par le pipeline IA.
    AR_MIN_LEVEL: int = 10

    # ── IA — fournisseur actif (voir services/ai_provider.py) ─
    # "groq" | "openrouter" | "deepseek" | "ollama" | "openai_compatible"
    AI_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OPENAI_COMPAT_BASE_URL: str = ""
    OPENAI_COMPAT_API_KEY: str = ""
    OPENAI_COMPAT_MODEL: str = ""

    # ── Threat Intel : VirusTotal ──────────────────────────────
    VT_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
