"""Enrichissement d'indicateurs de compromission via l'API VirusTotal (v3).

Actif uniquement si `VT_API_KEY` est renseigné et `DEMO_MODE` est faux — sinon
les appelants retombent sur les données de démo (voir `demo_data.py`)."""
import base64 as b64
import logging
from datetime import datetime, timezone

import requests

from ..core.config import settings

logger = logging.getLogger("aegis.virustotal")

VT_BASE = "https://www.virustotal.com/api/v3"
_cache: dict = {}


def vt_enabled() -> bool:
    return bool(settings.VT_API_KEY)


def vt_lookup(ioc_type: str, ioc_value: str) -> dict:
    if not vt_enabled():
        return {"error": "VT_API_KEY non configuré", "enabled": False}

    cache_key = f"{ioc_type}:{ioc_value}"
    if cache_key in _cache:
        return _cache[cache_key]

    headers = {"x-apikey": settings.VT_API_KEY, "Accept": "application/json"}
    try:
        if ioc_type == "ip":
            url = f"{VT_BASE}/ip_addresses/{ioc_value}"
        elif ioc_type in ("md5", "sha256"):
            url = f"{VT_BASE}/files/{ioc_value}"
        elif ioc_type == "domain":
            url = f"{VT_BASE}/domains/{ioc_value}"
        elif ioc_type == "url":
            url_id = b64.urlsafe_b64encode(ioc_value.encode()).decode().strip("=")
            url = f"{VT_BASE}/urls/{url_id}"
        else:
            return {"error": f"Type IoC inconnu: {ioc_type}"}

        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 404:
            result = {"found": False, "ioc_type": ioc_type, "ioc_value": ioc_value, "message": "IoC inconnu de VirusTotal"}
        elif r.status_code == 401:
            result = {"error": "Clé API VirusTotal invalide"}
        elif r.status_code == 429:
            result = {"error": "Quota API VirusTotal dépassé"}
        elif r.status_code == 200:
            attrs = r.json().get("data", {}).get("attributes", {})
            stats = attrs.get("last_analysis_stats", {})
            mal, sus = stats.get("malicious", 0), stats.get("suspicious", 0)
            verdict = "MALICIOUS" if mal >= 5 else "SUSPICIOUS" if (mal >= 1 or sus >= 3) else "CLEAN"
            result = {
                "found": True, "ioc_type": ioc_type, "ioc_value": ioc_value,
                "malicious": mal, "suspicious": sus, "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0), "total_engines": sum(stats.values()),
                "reputation": attrs.get("reputation", 0), "tags": attrs.get("tags", []),
                "verdict": verdict,
                "link": f"https://www.virustotal.com/gui/{'ip-address' if ioc_type == 'ip' else ioc_type + 's'}/{ioc_value}",
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            result = {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        result = {"error": str(e)}

    _cache[cache_key] = result
    return result


def enrich_alert_with_vt(alert: dict) -> dict:
    from .iocs import extract_iocs
    if not vt_enabled():
        return {}
    results = {}
    for ioc in extract_iocs(alert)[:4]:
        results[f"{ioc['type']}_{ioc['value']}"] = vt_lookup(ioc["type"], ioc["value"])
    return results
