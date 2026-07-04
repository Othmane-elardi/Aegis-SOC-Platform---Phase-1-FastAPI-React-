"""Analyse IA d'une alerte Wazuh brute — score de risque, type d'attaque,
recommandations, décision de réponse active. Utilisé par le pipeline
d'ingestion réelle (voir `wazuh_ingest.py`)."""
import json
import logging
import re

from . import ai_provider

logger = logging.getLogger("aegis.ai_analysis")

_FALLBACK_RECS = ["Configurer un fournisseur IA (GROQ_API_KEY, etc.) pour une analyse détaillée."]


def _extract_json_obj(raw: str) -> dict:
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    match = re.search(r"\{.*\}", raw.strip(), re.DOTALL)
    return json.loads(match.group()) if match else {}


def analyze_alert(alert: dict) -> dict:
    rule = alert.get("rule", {}) or {}
    level = int(rule.get("level", 0) or 0)
    agent_name = (alert.get("agent", {}) or {}).get("name", "unknown")
    src_ip = (alert.get("data", {}) or {}).get("srcip", "")

    client, model = ai_provider.get_client()
    if client is None:
        return {
            "risk_score": min(100, level * 7),
            "risk_level": "High" if level >= 12 else "Medium" if level >= 7 else "Low",
            "attack_type": "Non déterminé (IA non configurée)",
            "explanation": "Analyse basée uniquement sur le niveau de sévérité Wazuh.",
            "recommendations": _FALLBACK_RECS, "active_response": "alert_only", "is_false_positive": False,
        }
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"""Analyse cette alerte SOC/Wazuh. Réponds UNIQUEMENT avec un JSON valide, en français.
Règle: {rule.get('description', 'N/A')}
Niveau: {level}/15
Agent: {agent_name}
IP source: {src_ip}
MITRE: {rule.get('mitre', {}).get('tactic', 'N/A')}
JSON attendu:
{{
  "risk_score": <0-100>,
  "risk_level": "<Critical|High|Medium|Low>",
  "attack_type": "<type d'attaque>",
  "explanation": "<analyse courte>",
  "recommendations": ["<rec1>", "<rec2>"],
  "active_response": "<block_ip|restart_agent|alert_only>",
  "is_false_positive": <true|false>
}}"""}],
            temperature=0.1, max_tokens=400,
        )
        parsed = _extract_json_obj(resp.choices[0].message.content.strip())
        return parsed or {
            "risk_score": 50, "risk_level": "Medium", "attack_type": "Inconnu",
            "explanation": "Réponse IA vide ou non parsable.", "recommendations": ["Vérifier manuellement"],
            "active_response": "alert_only", "is_false_positive": False,
        }
    except Exception as e:
        logger.error("[ai_analysis] %s", e)
        return {"risk_score": 50, "risk_level": "Medium", "attack_type": "Inconnu", "explanation": str(e),
                "recommendations": ["Vérifier manuellement"], "active_response": "alert_only", "is_false_positive": False}
