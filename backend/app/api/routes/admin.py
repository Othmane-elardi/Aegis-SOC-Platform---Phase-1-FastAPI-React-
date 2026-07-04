"""Administration — comptes de la plateforme (données réelles, filtrées par tenant) et
paramètres système (démo). L'isolation multi-tenant est appliquée ici : un admin ne voit
et ne gère jamais que les comptes de son propre tenant, jamais ceux des autres organisations."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.tenant import Tenant
from ...models.user import User
from ...schemas.user import UserOut
from ...services import demo_data
from ..deps import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def overview(user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == user.tenant_id).first()
    users = db.query(User).filter(User.tenant_id == user.tenant_id).order_by(User.created_at).all()
    return {
        "tenant": {
            "slug": user.tenant_id,
            "name": tenant.name if tenant else user.tenant_id,
            "plan": tenant.plan if tenant else "n/a",
        },
        "users": [UserOut.model_validate(u).model_dump(mode="json") for u in users],
        "system": demo_data.admin_system_settings(),
        "license": demo_data.admin_license(
            plan=tenant.plan if tenant else "n/a",
            seats_total=tenant.seats if tenant else len(users),
            seats_used=len(users),
        ),
    }
