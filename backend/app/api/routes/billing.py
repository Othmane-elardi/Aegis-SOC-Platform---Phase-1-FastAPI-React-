"""Billing & Subscription — plan, usage et factures du tenant courant (démo + données réelles de tenant)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.tenant import Tenant
from ...models.user import User
from ...services import demo_data
from ..deps import require_roles

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/overview")
def overview(user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.slug == user.tenant_id).first()
    seats_used = db.query(User).filter(User.tenant_id == user.tenant_id).count()
    plan = tenant.plan if tenant else "professional"
    seats_total = tenant.seats if tenant else seats_used
    return {
        "billing": demo_data.billing_overview(plan=plan, seats_total=seats_total, seats_used=seats_used),
        "invoices": demo_data.billing_invoices(),
    }
