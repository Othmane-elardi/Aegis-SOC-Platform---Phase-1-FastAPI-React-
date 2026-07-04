"""Authentification : login (JWT) + profil courant."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.security import create_access_token, verify_password
from ...db.base import get_db
from ...models.user import User
from ...schemas.auth import LoginRequest, Token
from ...schemas.user import UserOut
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.strip().lower()).first()
    if not user or not user.is_active or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    token = create_access_token(subject=user.email, role=user.role,
                                extra={"name": user.full_name, "tenant": user.tenant_id})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
