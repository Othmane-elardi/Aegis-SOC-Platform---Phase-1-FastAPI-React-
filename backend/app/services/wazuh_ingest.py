"""Pipeline d'ingestion réelle : Wazuh/Elasticsearch → analyse IA → VirusTotal
→ réponse active → incident persistant. Ne démarre que si `DEMO_MODE=false` et
Wazuh configuré (voir `start_background_ingestion`, appelé au démarrage de l'app).

Un cluster Wazuh connecté correspond au tenant "default" — un déploiement mono-
tenant par instance de collecte, cohérent avec l'architecture multi-tenant
"pooled" du reste de la plateforme (voir models/tenant.py)."""
import logging
import threading
import time
from datetime import datetime, timezone

from ..core.config import settings
from ..db.base import SessionLocal
from ..models.incident import Incident
from . import ai_analysis, virustotal, wazuh_client

logger = logging.getLogger("aegis.wazuh_ingest")

INGEST_TENANT = "default"
POLL_INTERVAL_SECONDS = 30
_seen_alert_ids: set[str] = set()


def _alert_id(alert: dict) -> str:
    rule = alert.get("rule", {}) or {}
    return f"{rule.get('id', '')}-{alert.get('@timestamp', '')}"


def _ingest_one(db, alert: dict) -> None:
    alert_id = _alert_id(alert)
    if alert_id in _seen_alert_ids:
        return
    if db.query(Incident).filter(Incident.alert_id == alert_id, Incident.tenant_id == INGEST_TENANT).first():
        _seen_alert_ids.add(alert_id)
        return

    rule = alert.get("rule", {}) or {}
    level = int(rule.get("level", 0) or 0)
    agent_name = (alert.get("agent", {}) or {}).get("name", "unknown")
    src_ip = (alert.get("data", {}) or {}).get("srcip", "")

    analysis = ai_analysis.analyze_alert(alert)
    vt_results = virustotal.enrich_alert_with_vt(alert)

    ar_result: dict = {}
    if level >= settings.AR_MIN_LEVEL and src_ip and not analysis.get("is_false_positive", False):
        ar_action = analysis.get("active_response", "alert_only")
        if ar_action == "block_ip":
            ar_result = wazuh_client.trigger_active_response(agent_name, src_ip, "firewall-drop")
        elif ar_action == "restart_agent":
            ar_result = wazuh_client.trigger_active_response(agent_name, src_ip, "restart-wazuh-agent")

    now = datetime.now(timezone.utc)
    risk = int(analysis.get("risk_score") or level * 6)
    severity = str(analysis.get("risk_level", "medium")).lower()
    if severity not in ("critical", "high", "medium", "low"):
        severity = "medium"

    events = [{"timestamp": now.isoformat(), "event": "Incident créé automatiquement depuis une alerte Wazuh", "actor": "system"}]
    if ar_result.get("success"):
        events.append({"timestamp": now.isoformat(),
                        "event": f"Réponse active déclenchée : {ar_result.get('action_label', ar_result.get('action'))}",
                        "actor": "system"})

    inc = Incident(
        id=f"INC-{now.strftime('%Y%m%d%H%M%S')}-{abs(hash(alert_id)) % 100000:05d}",
        tenant_id=INGEST_TENANT, alert_id=alert_id,
        title=rule.get("description", "Alerte Wazuh") or "Alerte Wazuh", description=rule.get("description", "") or "",
        severity=severity, status="new", asset=agent_name, source_ip=src_ip or "",
        mitre_tactic=(rule.get("mitre", {}) or {}).get("tactic", "") or "",
        mitre_id=(rule.get("mitre", {}) or {}).get("id", "") or "",
        risk_score=max(1, min(100, risk)), source="wazuh",
        ai_analysis=analysis, threat_intel=vt_results, active_response=ar_result, timeline=events,
    )
    db.add(inc)
    db.commit()
    _seen_alert_ids.add(alert_id)
    logger.info("[ingest] Nouvel incident %s — %s — niveau %s", inc.id, agent_name, level)


def _poll_loop() -> None:
    logger.info("[ingest] Pipeline d'ingestion Wazuh démarré (intervalle %ss)", POLL_INTERVAL_SECONDS)
    while True:
        try:
            alerts = wazuh_client.get_alerts(minutes=5, size=30)
            db = SessionLocal()
            try:
                for alert in alerts:
                    _ingest_one(db, alert)
            finally:
                db.close()
        except Exception as e:
            logger.error("[ingest] %s", e)
        time.sleep(POLL_INTERVAL_SECONDS)


def start_background_ingestion() -> None:
    if settings.DEMO_MODE:
        return
    if not (settings.WAZUH_HOST and settings.WAZUH_USER and settings.WAZUH_PASS):
        logger.warning("[ingest] DEMO_MODE=false mais WAZUH_HOST/USER/PASS incomplets — ingestion désactivée.")
        return
    threading.Thread(target=_poll_loop, daemon=True).start()
