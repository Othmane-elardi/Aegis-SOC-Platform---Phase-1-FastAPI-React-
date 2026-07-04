"""Detection Engineering — règles de détection, faux positifs, cycle de vie (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/detection", tags=["detection"])


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.detection_overview()
