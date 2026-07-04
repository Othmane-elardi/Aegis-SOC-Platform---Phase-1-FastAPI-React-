"""SOAR Playbooks — automatisation de la réponse à incident.

`/overview` reste en données de démo (playbooks illustratifs). Les endpoints
`/status`, `/agents` et `/trigger` sont réels : ils parlent à Wazuh quand
`DEMO_MODE=false`, et simulent un succès sans appel réseau en mode démo."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.config import settings
from ...models.user import User
from ...services import demo_data, wazuh_client
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/soar", tags=["soar"])


class TriggerRequest(BaseModel):
    agent_name: str
    src_ip: str = ""
    action: str = "firewall-drop"
    extra: dict = {}


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.soar_overview()


@router.get("/status")
def status(_: User = Depends(get_current_user)):
    return wazuh_client.wazuh_status()


@router.get("/agents")
def agents(_: User = Depends(require_roles("admin", "soc_manager", "analyst"))):
    if settings.DEMO_MODE:
        return {"agents": demo_data.assets_inventory(20)}
    items, error = wazuh_client.list_agents()
    if items is None:
        raise HTTPException(503, error or "Wazuh indisponible")
    return {"agents": items}


@router.post("/trigger")
def trigger(body: TriggerRequest, user: User = Depends(require_roles("admin", "soc_manager", "analyst"))):
    if settings.DEMO_MODE:
        return {
            "success": True, "demo": True, "agent_id": "000", "action": body.action,
            "action_label": wazuh_client.ACTION_LABELS.get(body.action, body.action),
            "ip": body.src_ip, "triggered_by": user.full_name or user.email,
        }
    result = wazuh_client.trigger_active_response(body.agent_name, body.src_ip, body.action, body.extra)
    return {**result, "triggered_by": user.full_name or user.email}
