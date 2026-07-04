"""Intégration Wazuh réelle (API REST + Active Response) et Elasticsearch (alertes/stats).

Actif uniquement si `settings.DEMO_MODE` est faux — sinon toutes les fonctions
sont des no-op côté réseau (aucune connexion tentée), les modules appelants
retombant sur `services/demo_data.py`.
"""
import logging
from datetime import datetime, timezone

import requests
import urllib3

from ..core.config import settings

urllib3.disable_warnings()
logger = logging.getLogger("aegis.wazuh")

ACTION_LABELS = {
    "firewall-drop": "Blocage IP", "restart-wazuh-agent": "Redémarrage agent",
    "disable-account": "Désactivation compte", "kill-process": "Arrêt processus",
    "network-isolation": "Isolation réseau",
}

_es_client = None


def _get_es():
    """Client Elasticsearch paresseux — importé/instancié seulement si utilisé,
    pour ne jamais tenter de connexion en mode démo."""
    global _es_client
    if _es_client is None:
        from elasticsearch import Elasticsearch
        _es_client = Elasticsearch(
            settings.ES_HOST,
            basic_auth=(settings.ES_USER, settings.ES_PASS) if settings.ES_USER else None,
            verify_certs=False, ssl_show_warn=False,
            request_timeout=5, max_retries=1, retry_on_timeout=False,
        )
    return _es_client


def get_wazuh_token() -> str | None:
    try:
        r = requests.get(
            f"{settings.WAZUH_HOST}:55000/security/user/authenticate",
            auth=(settings.WAZUH_USER, settings.WAZUH_PASS), verify=False, timeout=5,
        )
        if r.status_code == 200:
            return r.json()["data"]["token"]
    except Exception as e:
        logger.error("[wazuh auth] %s", e)
    return None


def get_agent_id(token: str, agent_name: str) -> str | None:
    try:
        r = requests.get(
            f"{settings.WAZUH_HOST}:55000/agents", params={"name": agent_name},
            headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=5,
        )
        agents = r.json().get("data", {}).get("affected_items", [])
        return agents[0]["id"] if agents else None
    except Exception as e:
        logger.error("[wazuh get_agent_id] %s", e)
        return None


def wazuh_status() -> dict:
    if settings.DEMO_MODE:
        return {"connected": False, "demo_mode": True, "wazuh_host": settings.WAZUH_HOST}
    token = get_wazuh_token()
    return {"connected": bool(token), "demo_mode": False, "wazuh_host": settings.WAZUH_HOST}


def list_agents() -> tuple[list[dict] | None, str | None]:
    token = get_wazuh_token()
    if not token:
        return None, "Token Wazuh indisponible"
    try:
        r = requests.get(
            f"{settings.WAZUH_HOST}:55000/agents",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 500, "select": "id,name,status,ip"}, verify=False, timeout=10,
        )
        if r.status_code == 200:
            items = r.json().get("data", {}).get("affected_items", [])
            return [{"id": a["id"], "name": a["name"], "status": a.get("status", "unknown"),
                     "ip": a.get("ip", "")} for a in items], None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def get_alerts(minutes: int = 1440, size: int = 50) -> list[dict]:
    try:
        r = _get_es().search(index="wazuh-alerts-*", body={
            "query": {"bool": {"filter": [{"range": {"@timestamp": {"gte": f"now-{minutes}m", "lte": "now"}}}]}},
            "sort": [{"@timestamp": {"order": "desc"}}], "size": size,
            "_source": ["@timestamp", "agent.name", "agent.ip", "rule.description", "rule.level",
                        "rule.mitre.id", "rule.mitre.tactic", "rule.id", "data.srcip", "full_log", "location"],
        })
        return [h["_source"] for h in r["hits"]["hits"]]
    except Exception as e:
        logger.error("[wazuh get_alerts] %s", e)
        return []


def get_stats(minutes: int = 1440) -> dict:
    empty = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0,
             "top_tactics": [], "top_agents": [], "top_source_ips": [], "top_mitre_techniques": []}
    try:
        r = _get_es().search(index="wazuh-alerts-*", body={
            "size": 0, "query": {"range": {"@timestamp": {"gte": f"now-{minutes}m"}}},
            "aggs": {
                "critical": {"filter": {"range": {"rule.level": {"gte": 15}}}},
                "high": {"filter": {"range": {"rule.level": {"gte": 12, "lt": 15}}}},
                "medium": {"filter": {"range": {"rule.level": {"gte": 7, "lt": 12}}}},
                "low": {"filter": {"range": {"rule.level": {"lt": 7}}}},
                "top_tactics": {"terms": {"field": "rule.mitre.tactic", "size": 6}},
                "top_agents": {"terms": {"field": "agent.name", "size": 5}},
                "top_source_ips": {"terms": {"field": "data.srcip", "size": 5}},
                "top_mitre_techniques": {"terms": {"field": "rule.mitre.id", "size": 8}},
            },
        })
        aggs = r["aggregations"]
        return {
            "total": r["hits"]["total"]["value"], "critical": aggs["critical"]["doc_count"],
            "high": aggs["high"]["doc_count"], "medium": aggs["medium"]["doc_count"], "low": aggs["low"]["doc_count"],
            "top_tactics": [(b["key"], b["doc_count"]) for b in aggs["top_tactics"]["buckets"]],
            "top_agents": [(b["key"], b["doc_count"]) for b in aggs["top_agents"]["buckets"]],
            "top_source_ips": [(b["key"], b["doc_count"]) for b in aggs["top_source_ips"]["buckets"] if b["key"]],
            "top_mitre_techniques": [(b["key"], b["doc_count"]) for b in aggs["top_mitre_techniques"]["buckets"] if b["key"]],
        }
    except Exception as e:
        logger.error("[wazuh get_stats] %s", e)
        return empty


def get_storage_used_gb() -> float:
    try:
        stats = _get_es().indices.stats(index="wazuh-alerts-*")
        total_bytes = stats.get("_all", {}).get("total", {}).get("store", {}).get("size_in_bytes", 0)
        return round(total_bytes / (1024 ** 3), 2)
    except Exception as e:
        logger.error("[wazuh get_storage_used_gb] %s", e)
        return 0.0


def trigger_active_response(agent_name: str, src_ip: str, action: str = "firewall-drop", extra: dict | None = None) -> dict:
    """Déclenche une action Active Response réelle sur un agent Wazuh. Ne fait
    rien en mode démo (voir routes appelantes, qui gèrent le cas démo elles-mêmes)."""
    extra = extra or {}
    action_label = ACTION_LABELS.get(action, action)
    token = get_wazuh_token()
    if not token:
        return {"success": False, "error": "Token Wazuh indisponible", "action": action, "action_label": action_label}

    agent_id = get_agent_id(token, agent_name)
    if not agent_id:
        return {"success": False, "error": f"Agent '{agent_name}' introuvable", "action": action, "action_label": action_label}

    def _body(cmd, args):
        return {"command": cmd, "arguments": args, "alert": {"data": {"srcip": src_ip or ""}, "rule": {"level": 10}}}

    if action == "firewall-drop":
        body = _body("firewall-drop", ["-", "null", "180", src_ip] if src_ip else [])
    elif action == "restart-wazuh-agent":
        body = _body("restart-wazuh-agent", [])
    elif action == "disable-account":
        username = extra.get("username", "")
        if not username:
            return {"success": False, "error": "username requis", "action": action, "action_label": action_label}
        body = _body("disable-account", [username])
    elif action == "kill-process":
        target = extra.get("pid") or extra.get("process_name", "")
        if not target:
            return {"success": False, "error": "pid ou process_name requis", "action": action, "action_label": action_label}
        body = _body("kill-process", [str(target)])
    elif action == "network-isolation":
        body = _body("network-isolation", [settings.WAZUH_HOST.replace("https://", "").split(":")[0]])
    else:
        return {"success": False, "error": f"Action inconnue: {action}", "action": action, "action_label": action_label}

    try:
        r = requests.put(
            f"{settings.WAZUH_HOST}:55000/active-response", params={"agents_list": agent_id},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=body, verify=False, timeout=10,
        )
        ts = datetime.now(timezone.utc).isoformat()
        if r.status_code == 200:
            logger.info("[AR] %s -> agent %s (%s) | IP=%s", action_label, agent_name, agent_id, src_ip)
            return {"success": True, "agent_id": agent_id, "action": action, "action_label": action_label,
                    "ip": src_ip, "timestamp": ts}
        return {"success": False, "error": r.text[:200], "action": action, "action_label": action_label, "timestamp": ts}
    except Exception as e:
        logger.error("[AR error] %s", e)
        return {"success": False, "error": str(e), "action": action, "action_label": action_label}
