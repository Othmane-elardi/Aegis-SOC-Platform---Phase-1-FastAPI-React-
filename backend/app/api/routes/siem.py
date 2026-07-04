"""SIEM — flux d'événements ingérés et statistiques.

Sert des données de démo par défaut. Quand `DEMO_MODE=false`, interroge
réellement Elasticsearch/Wazuh (voir `services/wazuh_client.py`) et restitue
la même forme de réponse pour que le frontend n'ait rien à changer."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ...core.config import settings
from ...models.user import User
from ...services import demo_data, wazuh_client
from ..deps import get_current_user

router = APIRouter(prefix="/siem", tags=["siem"])

_LEVEL_TO_SEVERITY = lambda level: "critical" if level >= 15 else "high" if level >= 12 else "medium" if level >= 7 else "low"  # noqa: E731


def _real_overview() -> dict:
    stats = wazuh_client.get_stats(minutes=1440)
    alerts = wazuh_client.get_alerts(minutes=1440, size=60)
    agents, _ = wazuh_client.list_agents()
    connected = wazuh_client.wazuh_status()["connected"]

    events = []
    for i, a in enumerate(alerts):
        rule = a.get("rule", {}) or {}
        events.append({
            "id": f"EVT-REAL-{i}", "timestamp": a.get("@timestamp", datetime.now(timezone.utc).isoformat()),
            "source": (a.get("location") or "Wazuh"), "category": rule.get("mitre", {}).get("tactic", "") or "Wazuh",
            "message": rule.get("description", "N/A"), "host": (a.get("agent", {}) or {}).get("name", "unknown"),
            "severity": _LEVEL_TO_SEVERITY(int(rule.get("level", 0) or 0)),
        })

    return {
        "summary": {
            "events_per_sec": round(stats["total"] / (1440 * 60), 2) if stats["total"] else 0,
            "events_today": stats["total"],
            "sources_connected": len(agents) if agents else len(stats["top_agents"]),
            "storage_used_tb": round(wazuh_client.get_storage_used_gb() / 1024, 3),
            "retention_days": 90,
            "mode": "wazuh", "connected": connected,
        },
        "sources": [{"source": name, "events": count} for name, count in stats["top_agents"]] or
                   [{"source": "Wazuh", "events": stats["total"]}],
        "events": events,
    }


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    if settings.DEMO_MODE:
        return demo_data.siem_overview()
    return _real_overview()
