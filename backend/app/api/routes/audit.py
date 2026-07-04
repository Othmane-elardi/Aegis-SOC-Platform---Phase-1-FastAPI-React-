"""Audit Center — journal des actions utilisateurs et système (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import require_roles

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/overview")
def overview(_: User = Depends(require_roles("auditor", "soc_manager"))):
    return demo_data.audit_overview()
