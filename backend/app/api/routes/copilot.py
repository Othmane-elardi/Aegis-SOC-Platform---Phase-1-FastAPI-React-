"""AI Copilot — insights automatiques et assistant question/réponse.

Répond via un vrai fournisseur IA (Groq/OpenRouter/DeepSeek/Ollama) sur des
alertes Wazuh réelles quand `DEMO_MODE=false` et qu'un fournisseur est
configuré ; sinon retombe sur la réponse déterministe basée sur les données
de démo, pour que le module reste utilisable sans aucune intégration."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...core.config import settings
from ...models.user import User
from ...services import copilot_ai, demo_data
from ..deps import get_current_user

router = APIRouter(prefix="/copilot", tags=["copilot"])


class AskRequest(BaseModel):
    question: str


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.copilot_overview()


@router.post("/ask")
def ask(body: AskRequest, _: User = Depends(get_current_user)):
    if not settings.DEMO_MODE:
        real_answer = copilot_ai.answer_query(body.question)
        if real_answer is not None:
            return {"question": body.question, "answer": real_answer,
                    "answered_at": datetime.now(timezone.utc).isoformat(), "engine": "ai"}
    return {**demo_data.copilot_ask(body.question), "engine": "demo"}
