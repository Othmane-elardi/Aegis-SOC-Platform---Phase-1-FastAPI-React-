"""Vulnerability Management — CVE, exposition, cycle de remédiation (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.vulnerabilities_overview()
