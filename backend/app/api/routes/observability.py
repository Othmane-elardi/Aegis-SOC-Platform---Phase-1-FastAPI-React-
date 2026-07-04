"""Observability — santé de la plateforme, latence, disponibilité (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.observability_overview()
