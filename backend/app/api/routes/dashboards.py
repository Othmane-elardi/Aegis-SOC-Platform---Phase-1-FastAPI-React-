"""Dashboards CISO / SOC / Analyste + flux threat intel."""
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services import demo_data
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/soc")
def soc_dashboard(_: User = Depends(get_current_user)):
    """Vue SOC complète (KPIs, tendance, sévérité, MITRE, charge, incidents récents)."""
    return demo_data.soc_overview()


@router.get("/executive")
def executive_dashboard(_: User = Depends(require_roles("ciso", "soc_manager"))):
    """Vue exécutive CISO — risque, conformité, coût, tendances (accès restreint)."""
    return {
        "kpis": demo_data.executive_kpis(),
        "alert_trend": demo_data.alert_trend(),
        "severity_breakdown": demo_data.severity_breakdown(),
    }


@router.get("/threat-intel")
def threat_intel(_: User = Depends(get_current_user)):
    return {"indicators": demo_data.threat_intel_feed()}
