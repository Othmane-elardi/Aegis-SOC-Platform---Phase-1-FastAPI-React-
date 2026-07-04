"""Incident Management — liste filtrable + détail (données de démo)."""
from fastapi import APIRouter, Depends, HTTPException, Query

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("")
def list_incidents(
    _: User = Depends(get_current_user),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(40, le=200),
):
    items = demo_data.incidents(limit=limit)
    if severity:
        items = [i for i in items if i["severity"] == severity]
    if status:
        items = [i for i in items if i["status"] == status]
    counts: dict[str, int] = {}
    for i in demo_data.incidents(limit=limit):
        counts[i["status"]] = counts.get(i["status"], 0) + 1
    return {"items": items, "total": len(items), "status_counts": counts}


@router.get("/{incident_id}")
def get_incident(incident_id: str, _: User = Depends(get_current_user)):
    inc = next((i for i in demo_data.incidents(limit=60) if i["id"] == incident_id), None)
    if not inc:
        raise HTTPException(404, "Incident introuvable")
    inc = dict(inc)
    inc["timeline"] = [
        {"ts": inc["created_at"], "event": "Incident créé par corrélation SIEM", "actor": "system"},
        {"ts": inc["created_at"], "event": f"Sévérité évaluée : {inc['severity'].upper()}", "actor": "engine"},
    ]
    inc["recommendations"] = [
        "Isoler l'actif concerné du réseau",
        "Réinitialiser les identifiants potentiellement compromis",
        "Collecter les artefacts forensiques (mémoire, journaux)",
    ]
    return inc
