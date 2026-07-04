"""AI Copilot — insights générés automatiquement et assistant question/réponse (démo)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/copilot", tags=["copilot"])


class AskRequest(BaseModel):
    question: str


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.copilot_overview()


@router.post("/ask")
def ask(body: AskRequest, _: User = Depends(get_current_user)):
    return demo_data.copilot_ask(body.question)
