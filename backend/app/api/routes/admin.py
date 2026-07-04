"""Administration — comptes de la plateforme (données réelles) et paramètres système (démo)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.user import User
from ...schemas.user import UserOut
from ...services import demo_data
from ..deps import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def overview(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at).all()
    return {
        "users": [UserOut.model_validate(u).model_dump(mode="json") for u in users],
        "system": demo_data.admin_system_settings(),
        "license": demo_data.admin_license(),
    }
