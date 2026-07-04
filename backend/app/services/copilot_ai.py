"""Copilot IA réel — répond en langage naturel à partir des alertes Wazuh réelles
et des incidents persistés. N'est appelé que si `DEMO_MODE` est faux ; retourne
`None` si aucun fournisseur IA n'est configuré, auquel cas l'appelant retombe
sur la réponse déterministe de `demo_data.copilot_ask`."""
import logging

from . import ai_provider, wazuh_client

logger = logging.getLogger("aegis.copilot_ai")


def answer_query(question: str) -> str | None:
    client, model = ai_provider.get_client()
    if client is None:
        return None
    try:
        stats = wazuh_client.get_stats()
        alerts = wazuh_client.get_alerts(minutes=1440, size=15)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": (
                    "Tu es un expert SOC. Analyse les alertes Wazuh/ELK et réponds en français, de façon "
                    "concise et précise. Cite des chiffres exacts. Utilise MITRE ATT&CK quand pertinent."
                )},
                {"role": "user", "content": (
                    f"Statistiques 24h : {stats}\n\nAlertes récentes (échantillon) : {alerts[:10]}\n\n"
                    f"Question : {question}"
                )},
            ],
            temperature=0.3, max_tokens=600,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error("[copilot_ai] %s", e)
        return f"Erreur IA : {e}"
