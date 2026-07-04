"""Analyst Workspace — file personnelle de l'analyste connecté (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/analyst", tags=["analyst"])


@router.get("/workspace")
def workspace(user: User = Depends(get_current_user)):
    return demo_data.analyst_workspace(user.full_name or user.email)
