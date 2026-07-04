"""Incident Management — cycle de vie réel et persistant (contrairement aux
autres modules qui restent en données de démo générées à la volée).

Un incident peut être créé manuellement, provenir du jeu de démo initial, ou
(si `DEMO_MODE=false` et Wazuh configuré) être ingéré automatiquement depuis
une alerte Wazuh réelle — voir `services/wazuh_ingest.py`."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.incident import VALID_STATUSES, Incident
from ...models.user import User
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _serialize(inc: Incident) -> dict:
    return {
        "id": inc.id, "alert_id": inc.alert_id, "title": inc.title, "description": inc.description,
        "severity": inc.severity, "status": inc.status, "verdict": inc.verdict,
        "asset": inc.asset, "source_ip": inc.source_ip, "mitre_tactic": inc.mitre_tactic, "mitre_id": inc.mitre_id,
        "risk_score": inc.risk_score, "assignee": inc.assignee or None, "priority": inc.priority,
        "tags": inc.tags or [], "ai_analysis": inc.ai_analysis or {}, "threat_intel": inc.threat_intel or {},
        "active_response": inc.active_response or {}, "timeline": inc.timeline or [], "notes": inc.notes or [],
        "source": inc.source, "sla_breached": inc.sla_breached,
        "created_at": inc.created_at.isoformat(), "updated_at": inc.updated_at.isoformat(),
    }


class IncidentCreate(BaseModel):
    title: str
    description: str = ""
    severity: str = "medium"
    asset: str = ""
    source_ip: str = ""
    mitre_tactic: str = ""
    priority: str = "normal"
    tags: list[str] = []


class IncidentUpdate(BaseModel):
    status: str | None = None
    assignee: str | None = None
    verdict: str | None = None
    priority: str | None = None
    tags: list[str] | None = None
    note: str | None = None


@router.get("")
def list_incidents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    assignee: str | None = Query(None, description="'me' pour filtrer sur l'utilisateur connecté"),
    limit: int = Query(60, le=500),
):
    q = db.query(Incident).filter(Incident.tenant_id == user.tenant_id)
    if severity:
        q = q.filter(Incident.severity == severity)
    if status:
        q = q.filter(Incident.status == status)
    if assignee:
        target = user.full_name if assignee == "me" else assignee
        q = q.filter(Incident.assignee == target)
    items = q.order_by(Incident.created_at.desc()).limit(limit).all()

    all_for_counts = db.query(Incident).filter(Incident.tenant_id == user.tenant_id).all()
    counts: dict[str, int] = {}
    for i in all_for_counts:
        counts[i.status] = counts.get(i.status, 0) + 1

    return {"items": [_serialize(i) for i in items], "total": len(all_for_counts), "status_counts": counts}


@router.get("/{incident_id}")
def get_incident(incident_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.tenant_id == user.tenant_id).first()
    if not inc:
        raise HTTPException(404, "Incident introuvable")
    return _serialize(inc)


@router.post("", status_code=201)
def create_incident(body: IncidentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    inc = Incident(
        id=f"INC-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}", tenant_id=user.tenant_id,
        title=body.title, description=body.description, severity=body.severity, asset=body.asset,
        source_ip=body.source_ip, mitre_tactic=body.mitre_tactic, priority=body.priority, tags=body.tags,
        source="manual", status="new",
        timeline=[{"timestamp": now.isoformat(), "event": "Incident créé manuellement", "actor": user.full_name or user.email}],
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)
    return _serialize(inc)


@router.patch("/{incident_id}")
def update_incident(incident_id: str, body: IncidentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.tenant_id == user.tenant_id).first()
    if not inc:
        raise HTTPException(404, "Incident introuvable")

    actor = user.full_name or user.email
    now = datetime.now(timezone.utc)
    timeline = list(inc.timeline or [])

    if body.status is not None:
        if body.status not in VALID_STATUSES:
            raise HTTPException(422, f"Statut invalide — valeurs autorisées : {', '.join(VALID_STATUSES)}")
        if body.status != inc.status:
            timeline.append({"timestamp": now.isoformat(), "event": f"Statut changé → {body.status}", "actor": actor})
        inc.status = body.status
    if body.assignee is not None and body.assignee != inc.assignee:
        timeline.append({"timestamp": now.isoformat(), "event": f"Assigné à {body.assignee}" if body.assignee else "Désassigné", "actor": actor})
        inc.assignee = body.assignee
    if body.verdict is not None:
        inc.verdict = body.verdict
        timeline.append({"timestamp": now.isoformat(), "event": f"Verdict : {body.verdict}", "actor": actor})
    if body.priority is not None:
        inc.priority = body.priority
    if body.tags is not None:
        inc.tags = body.tags
    if body.note:
        notes = list(inc.notes or [])
        notes.append({"ts": now.isoformat(), "text": body.note.strip(), "author": actor})
        inc.notes = notes
        timeline.append({"timestamp": now.isoformat(), "event": f"Note ajoutée par {actor} : {body.note.strip()[:80]}", "actor": actor})

    inc.timeline = timeline
    db.commit()
    db.refresh(inc)
    return _serialize(inc)


@router.delete("/{incident_id}")
def delete_incident(incident_id: str, user: User = Depends(require_roles("admin", "soc_manager")), db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.tenant_id == user.tenant_id).first()
    if not inc:
        raise HTTPException(404, "Incident introuvable")
    db.delete(inc)
    db.commit()
    return {"deleted": incident_id}
