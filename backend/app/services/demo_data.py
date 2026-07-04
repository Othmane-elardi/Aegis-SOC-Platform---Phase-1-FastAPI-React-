"""Données de démonstration enterprise — dashboards vivants sans SIEM branché.

Alimente les tableaux de bord CISO / SOC Manager / Analyste avec des métriques
réalistes et cohérentes. Déterministe sur la minute (stable pour une démo),
évolue ensuite pour un effet « temps réel ».
"""
import hashlib
import random
from datetime import datetime, timedelta, timezone

SEVERITIES = ["critical", "high", "medium", "low"]

ASSETS = [
    "WIN-DC01", "SRV-WEB01", "SRV-DB01", "SRV-EXCHANGE", "WKS-FINANCE-07",
    "WKS-HR-03", "LNX-APP01", "FW-EDGE01", "K8S-NODE-02", "SRV-VPN01",
]
ANALYSTS = [
    {"name": "Amine Martin", "handle": "a.martin"},
    {"name": "Léa Dubois", "handle": "l.dubois"},
    {"name": "Sami Nguyen", "handle": "s.nguyen"},
    {"name": "Karim Moreau", "handle": "k.moreau"},
]
MITRE_TACTICS = [
    ("TA0001", "Initial Access"), ("TA0002", "Execution"), ("TA0003", "Persistence"),
    ("TA0004", "Privilege Escalation"), ("TA0006", "Credential Access"),
    ("TA0007", "Discovery"), ("TA0010", "Exfiltration"), ("TA0011", "Command and Control"),
    ("TA0040", "Impact"),
]
INCIDENT_TITLES = [
    ("Brute-force réussi sur compte privilégié", "critical", "Credential Access"),
    ("Ransomware — chiffrement de fichiers détecté", "critical", "Impact"),
    ("Exfiltration de données vers hôte externe", "high", "Exfiltration"),
    ("PowerShell encodé suspect exécuté", "high", "Execution"),
    ("Balayage de ports interne (mouvement latéral)", "medium", "Discovery"),
    ("Connexion depuis géolocalisation impossible", "high", "Initial Access"),
    ("Compte ajouté aux administrateurs du domaine", "high", "Persistence"),
    ("Communication vers infrastructure C2 connue", "critical", "Command and Control"),
    ("Injection SQL sur application exposée", "medium", "Initial Access"),
    ("Kerberoasting détecté sur le contrôleur", "high", "Credential Access"),
    ("Antivirus : malware mis en quarantaine", "medium", "Execution"),
    ("Élévation de privilèges via sudo", "high", "Privilege Escalation"),
]
STATUSES = ["new", "investigating", "contained", "resolved"]


def _rng(salt: str = "") -> random.Random:
    seed = int(datetime.now(timezone.utc).timestamp() // 60)
    return random.Random(f"{seed}-{salt}")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def incidents(limit: int = 40) -> list[dict]:
    rng = _rng("inc")
    out = []
    for i in range(limit):
        title, sev, tactic = rng.choice(INCIDENT_TITLES)
        created = _now() - timedelta(hours=rng.randint(0, 21 * 24), minutes=rng.randint(0, 59))
        status = rng.choice(STATUSES)
        assignee = rng.choice(ANALYSTS) if status != "new" or rng.random() < 0.5 else None
        risk = {"critical": 90, "high": 72, "medium": 48, "low": 22}[sev] + rng.randint(-8, 8)
        out.append({
            "id": f"INC-{created.strftime('%Y%m')}-{2000 + i}",
            "title": title, "severity": sev, "status": status,
            "asset": rng.choice(ASSETS), "source_ip": f"{rng.randint(11,223)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
            "mitre_tactic": tactic, "risk_score": max(1, min(100, risk)),
            "assignee": assignee["name"] if assignee else None,
            "assignee_handle": assignee["handle"] if assignee else None,
            "created_at": created.isoformat(),
            "sla_breached": status not in ("resolved", "contained") and rng.random() < 0.18,
        })
    out.sort(key=lambda x: x["created_at"], reverse=True)
    return out


def alert_trend(days: int = 14) -> list[dict]:
    rng = _rng("trend")
    series = []
    base = 180
    for d in range(days, -1, -1):
        day = (_now() - timedelta(days=d)).date()
        spike = 2.1 if d in (1, 2) else 1.0  # incident en cours ces 2 derniers jours
        total = int(base * spike * rng.uniform(0.8, 1.25))
        series.append({
            "date": day.isoformat(),
            "total": total,
            "critical": int(total * rng.uniform(0.02, 0.05)),
            "high": int(total * rng.uniform(0.10, 0.18)),
            "resolved": int(total * rng.uniform(0.55, 0.8)),
        })
    return series


def severity_breakdown() -> dict:
    rng = _rng("sev")
    return {
        "critical": rng.randint(6, 14), "high": rng.randint(40, 70),
        "medium": rng.randint(110, 160), "low": rng.randint(30, 60),
    }


def mitre_coverage() -> list[dict]:
    rng = _rng("mitre")
    return [{"id": tid, "tactic": name, "count": rng.randint(3, 60)} for tid, name in MITRE_TACTICS]


def analyst_workload() -> list[dict]:
    rng = _rng("wl")
    return [{
        "name": a["name"], "handle": a["handle"],
        "open": rng.randint(1, 6), "in_progress": rng.randint(0, 5),
        "resolved_today": rng.randint(2, 12),
    } for a in ANALYSTS]


def executive_kpis() -> dict:
    rng = _rng("exec")
    sev = severity_breakdown()
    return {
        "risk_score": rng.randint(58, 74),
        "risk_trend": rng.choice([-6, -4, -3, 2, 5]),
        "open_incidents": rng.randint(18, 34),
        "critical_incidents": sev["critical"],
        "mttr_hours": round(rng.uniform(3.5, 7.5), 1),
        "mttd_minutes": round(rng.uniform(8, 26), 1),
        "sla_compliance": rng.randint(88, 98),
        "assets_monitored": 1284,
        "assets_at_risk": rng.randint(12, 28),
        "coverage_pct": rng.randint(82, 94),
        "incidents_cost_eur": rng.randint(120, 340) * 1000,
        "compliance": {"ISO 27001": rng.randint(86, 96), "NIST CSF": rng.randint(78, 90),
                       "PCI DSS": rng.randint(80, 94), "RGPD": rng.randint(88, 98)},
    }


def soc_overview() -> dict:
    sev = severity_breakdown()
    return {
        "kpis": executive_kpis(),
        "severity_breakdown": sev,
        "alert_trend": alert_trend(),
        "mitre_coverage": mitre_coverage(),
        "analyst_workload": analyst_workload(),
        "recent_incidents": incidents(8),
        "generated_at": _now().isoformat(),
    }


def threat_intel_feed(limit: int = 12) -> list[dict]:
    rng = _rng("ti")
    kinds = ["ip", "domain", "hash", "url"]
    verdicts = ["malicious", "suspicious", "clean"]
    out = []
    for i in range(limit):
        kind = rng.choice(kinds)
        value = {"ip": f"{rng.randint(11,223)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
                 "domain": rng.choice(["evil-cdn.ru", "login-secure.tk", "update-flash.cn", "pay-invoice.xyz"]),
                 "hash": hashlib.sha256(f"{i}".encode()).hexdigest(),
                 "url": "http://malicious.example/payload"}[kind]
        out.append({"type": kind, "value": value, "verdict": rng.choice(verdicts),
                    "sources": rng.randint(1, 6), "first_seen": (_now() - timedelta(days=rng.randint(0, 30))).isoformat()})
    return out
