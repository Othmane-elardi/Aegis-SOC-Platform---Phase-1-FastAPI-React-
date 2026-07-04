"""IOC Management — cycle de vie des indicateurs de compromission.

`/overview` reste en données de démo. `/lookup` interroge réellement
VirusTotal quand `VT_API_KEY` est configuré (indépendant de `DEMO_MODE` —
l'enrichissement threat intel a du sens même sans Wazuh connecté)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...models.user import User
from ...services import demo_data, virustotal
from ..deps import get_current_user

router = APIRouter(prefix="/iocs", tags=["iocs"])


class LookupRequest(BaseModel):
    ioc_type: str
    ioc_value: str


@router.get("/overview")
def overview(_: User = Depends(get_current_user)):
    return demo_data.ioc_overview()


@router.post("/lookup")
def lookup(body: LookupRequest, _: User = Depends(get_current_user)):
    if not virustotal.vt_enabled():
        return demo_data.vt_lookup(body.ioc_type, body.ioc_value)
    return virustotal.vt_lookup(body.ioc_type, body.ioc_value)
