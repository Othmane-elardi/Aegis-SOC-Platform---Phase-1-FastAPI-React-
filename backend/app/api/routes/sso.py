"""Identity & SSO — fournisseurs d'identité fédérée (SAML/OIDC) (données de démo)."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import require_roles

router = APIRouter(prefix="/sso", tags=["sso"])


@router.get("/overview")
def overview(_: User = Depends(require_roles("admin"))):
    return demo_data.sso_overview()
