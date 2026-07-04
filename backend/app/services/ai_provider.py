"""Couche d'abstraction multi-fournisseur IA — Groq, OpenRouter, DeepSeek, Ollama,
ou tout endpoint compatible OpenAI. Tous exposent une API `chat.completions`,
ce qui permet un seul client dans le code quel que soit le fournisseur choisi.

Le fournisseur actif vient de `settings.AI_PROVIDER`. Utilisé uniquement quand
`settings.DEMO_MODE` est faux (voir `services/copilot_ai.py`) — sinon Copilot
répond via les règles déterministes de `demo_data.copilot_ask`.
"""
import logging
import threading

from ..core.config import settings

logger = logging.getLogger("aegis.ai_provider")

_PROVIDERS = {
    "groq": "Groq (cloud)",
    "openrouter": "OpenRouter (open-source)",
    "deepseek": "DeepSeek (open-weight)",
    "ollama": "Ollama (local / open-source)",
    "openai_compatible": "Endpoint compatible OpenAI",
}

_lock = threading.Lock()
_client_cache: dict = {}


def _settings_for(provider: str):
    if provider == "ollama":
        return f"{settings.OLLAMA_HOST.rstrip('/')}/v1", "ollama", settings.OLLAMA_MODEL, None
    if provider == "openai_compatible":
        return settings.OPENAI_COMPAT_BASE_URL, (settings.OPENAI_COMPAT_API_KEY or "none"), settings.OPENAI_COMPAT_MODEL, None
    if provider == "openrouter":
        return ("https://openrouter.ai/api/v1", settings.OPENROUTER_API_KEY, settings.OPENROUTER_MODEL,
                {"HTTP-Referer": "https://aegis-soc.local", "X-Title": "Aegis SOC Platform"})
    if provider == "deepseek":
        return "https://api.deepseek.com", settings.DEEPSEEK_API_KEY, settings.DEEPSEEK_MODEL, None
    return "https://api.groq.com/openai/v1", settings.GROQ_API_KEY, settings.GROQ_MODEL, None


def is_configured(provider: str) -> bool:
    base_url, api_key, model, _ = _settings_for(provider)
    if not model:
        return False
    if provider == "ollama":
        return True
    if provider == "openai_compatible":
        return bool(base_url)
    return bool(api_key)


def active_provider_info() -> dict:
    provider = (settings.AI_PROVIDER or "groq").lower()
    if provider not in _PROVIDERS:
        provider = "groq"
    _, _, model, _ = _settings_for(provider)
    return {"provider": provider, "label": _PROVIDERS[provider], "model": model, "configured": is_configured(provider)}


def get_client():
    """Retourne (client, model) pour le fournisseur actif — (None, None) si non configuré."""
    provider = (settings.AI_PROVIDER or "groq").lower()
    if provider not in _PROVIDERS:
        provider = "groq"
    with _lock:
        if provider not in _client_cache:
            base_url, api_key, model, headers = _settings_for(provider)
            if not is_configured(provider):
                _client_cache[provider] = (None, None)
            else:
                try:
                    from openai import OpenAI
                    kwargs = {"api_key": api_key or "none", "base_url": base_url}
                    if headers:
                        kwargs["default_headers"] = headers
                    _client_cache[provider] = (OpenAI(**kwargs), model)
                except Exception as e:
                    logger.error("[ai_provider] init impossible (%s): %s", provider, e)
                    _client_cache[provider] = (None, None)
        return _client_cache[provider]
