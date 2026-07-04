"""Threat Intelligence — acteurs, campagnes, flux d'indicateurs (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/threat-intel", tags=["threat-intel"])


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.threat_intel_overview()
