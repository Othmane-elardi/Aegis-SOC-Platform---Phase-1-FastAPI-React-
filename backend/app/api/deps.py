"""Dépendances FastAPI : utilisateur courant (JWT) + garde de rôle (RBAC)."""
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.security import decode_access_token
from ..db.base import get_db
from ..models.user import User

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise")
    payload = decode_access_token(creds.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Jeton invalide ou expiré")
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Compte introuvable ou désactivé")
    return user


def require_roles(*roles: str) -> Callable:
    """Garde RBAC : l'admin passe toujours ; sinon le rôle doit être autorisé."""
    def guard(user: User = Depends(get_current_user)) -> User:
        if user.role != "admin" and user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé — rôle insuffisant")
        return user
    return guard
