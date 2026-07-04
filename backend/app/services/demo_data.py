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


# ── Threat Intelligence ──────────────────────────────────────────────────
THREAT_ACTORS = [
    {"name": "APT29 (Cozy Bear)", "origin": "Russie", "motivation": "Espionnage", "sophistication": "Élevée"},
    {"name": "Lazarus Group", "origin": "Corée du Nord", "motivation": "Financier / Espionnage", "sophistication": "Élevée"},
    {"name": "FIN7", "origin": "Non attribué", "motivation": "Financier", "sophistication": "Élevée"},
    {"name": "APT41", "origin": "Chine", "motivation": "Espionnage / Financier", "sophistication": "Élevée"},
    {"name": "Sandworm", "origin": "Russie", "motivation": "Sabotage", "sophistication": "Élevée"},
    {"name": "Scattered Spider", "origin": "Non attribué", "motivation": "Financier", "sophistication": "Moyenne"},
]
TARGET_SECTORS = ["Finance", "Énergie", "Santé", "Administration", "Retail", "Industrie"]
CAMPAIGN_NAMES = [
    "Operation SilentLedger", "Operation FrostGate", "Operation RedTelescope",
    "Operation DarkHarbor", "Operation GhostInvoice", "Operation IronCurrent",
]


def threat_actors() -> list[dict]:
    rng = _rng("actors")
    out = []
    for a in THREAT_ACTORS:
        out.append({
            **a,
            "campaigns_active": rng.randint(1, 4),
            "iocs_linked": rng.randint(20, 400),
            "targeted_sectors": rng.sample(TARGET_SECTORS, k=rng.randint(1, 3)),
            "last_seen": (_now() - timedelta(days=rng.randint(0, 45))).isoformat(),
        })
    return out


def threat_campaigns(limit: int = 6) -> list[dict]:
    rng = _rng("campaigns")
    out = []
    for i in range(limit):
        actor = rng.choice(THREAT_ACTORS)
        tid, tactic = rng.choice(MITRE_TACTICS)
        out.append({
            "id": f"CAMP-{2024 + (i % 3)}-{100 + i}",
            "name": CAMPAIGN_NAMES[i % len(CAMPAIGN_NAMES)],
            "actor": actor["name"],
            "target_sector": rng.choice(TARGET_SECTORS),
            "primary_tactic": tactic,
            "iocs_count": rng.randint(8, 120),
            "status": rng.choice(["active", "active", "monitored", "dormant"]),
            "started_at": (_now() - timedelta(days=rng.randint(5, 180))).isoformat(),
        })
    return out


def threat_intel_summary() -> dict:
    rng = _rng("ti-sum")
    feed = threat_intel_feed(40)
    malicious = sum(1 for f in feed if f["verdict"] == "malicious")
    return {
        "total_indicators": rng.randint(3200, 5400),
        "malicious_pct": round(100 * malicious / len(feed), 1),
        "new_today": rng.randint(30, 140),
        "active_campaigns": sum(1 for c in threat_campaigns() if c["status"] == "active"),
        "actors_tracked": len(THREAT_ACTORS),
        "feeds_connected": rng.randint(6, 11),
    }


def threat_intel_overview() -> dict:
    return {
        "summary": threat_intel_summary(),
        "actors": threat_actors(),
        "campaigns": threat_campaigns(),
        "feed": threat_intel_feed(20),
    }


# ── MITRE ATT&CK Center ───────────────────────────────────────────────────
MITRE_TECHNIQUES = [
    ("T1566", "Phishing", "TA0001", "Initial Access"),
    ("T1190", "Exploit Public-Facing Application", "TA0001", "Initial Access"),
    ("T1078", "Valid Accounts", "TA0001", "Initial Access"),
    ("T1059", "Command and Scripting Interpreter", "TA0002", "Execution"),
    ("T1204", "User Execution", "TA0002", "Execution"),
    ("T1053", "Scheduled Task/Job", "TA0002", "Execution"),
    ("T1543", "Create or Modify System Process", "TA0003", "Persistence"),
    ("T1136", "Create Account", "TA0003", "Persistence"),
    ("T1547", "Boot or Logon Autostart Execution", "TA0003", "Persistence"),
    ("T1068", "Exploitation for Privilege Escalation", "TA0004", "Privilege Escalation"),
    ("T1055", "Process Injection", "TA0004", "Privilege Escalation"),
    ("T1548", "Abuse Elevation Control Mechanism", "TA0004", "Privilege Escalation"),
    ("T1110", "Brute Force", "TA0006", "Credential Access"),
    ("T1003", "OS Credential Dumping", "TA0006", "Credential Access"),
    ("T1558", "Steal or Forge Kerberos Tickets", "TA0006", "Credential Access"),
    ("T1082", "System Information Discovery", "TA0007", "Discovery"),
    ("T1046", "Network Service Discovery", "TA0007", "Discovery"),
    ("T1087", "Account Discovery", "TA0007", "Discovery"),
    ("T1041", "Exfiltration Over C2 Channel", "TA0010", "Exfiltration"),
    ("T1567", "Exfiltration Over Web Service", "TA0010", "Exfiltration"),
    ("T1071", "Application Layer Protocol", "TA0011", "Command and Control"),
    ("T1105", "Ingress Tool Transfer", "TA0011", "Command and Control"),
    ("T1573", "Encrypted Channel", "TA0011", "Command and Control"),
    ("T1486", "Data Encrypted for Impact", "TA0040", "Impact"),
    ("T1490", "Inhibit System Recovery", "TA0040", "Impact"),
]


def mitre_techniques() -> list[dict]:
    rng = _rng("mitre-tech")
    out = []
    for tech_id, name, tactic_id, tactic in MITRE_TECHNIQUES:
        detections = rng.randint(0, 45)
        coverage = "covered" if detections > 10 else "partial" if detections > 0 else "none"
        out.append({
            "id": tech_id, "name": name, "tactic_id": tactic_id, "tactic": tactic,
            "detections": detections, "coverage": coverage,
            "incidents_mapped": rng.randint(0, 12),
        })
    return out


def mitre_overview() -> dict:
    techniques = mitre_techniques()
    covered = sum(1 for t in techniques if t["coverage"] == "covered")
    partial = sum(1 for t in techniques if t["coverage"] == "partial")
    none_ = sum(1 for t in techniques if t["coverage"] == "none")
    return {
        "tactics": mitre_coverage(),
        "techniques": techniques,
        "summary": {
            "total_techniques": len(techniques),
            "covered": covered, "partial": partial, "not_covered": none_,
            "coverage_pct": round(100 * (covered + partial * 0.5) / len(techniques), 1),
        },
    }


# ── Asset Management ──────────────────────────────────────────────────────
ASSET_TYPES = ["workstation", "server", "network", "cloud", "container"]
ASSET_OS = ["Windows Server 2022", "Windows 11", "Ubuntu 22.04", "RHEL 9", "macOS Sonoma", "ESXi 8"]
ASSET_OWNERS = ["IT Infra", "DevOps", "Finance", "RH", "Sécurité", "Réseau"]


def assets_inventory(limit: int = 60) -> list[dict]:
    rng = _rng("assets")
    out = []
    for i in range(limit):
        atype = rng.choice(ASSET_TYPES)
        criticality = rng.choices(["critical", "high", "medium", "low"], weights=[1, 3, 5, 4])[0]
        vulns = rng.randint(0, 24)
        risk = {"critical": 80, "high": 60, "medium": 35, "low": 15}[criticality] + vulns + rng.randint(-10, 10)
        online = rng.random() < 0.9
        out.append({
            "id": f"AST-{3000 + i}",
            "hostname": rng.choice(ASSETS) + (f"-{i}" if rng.random() < 0.3 else ""),
            "type": atype,
            "ip": f"10.{rng.randint(0,20)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
            "os": rng.choice(ASSET_OS),
            "owner": rng.choice(ASSET_OWNERS),
            "criticality": criticality,
            "risk_score": max(1, min(100, risk)),
            "vulnerabilities": vulns,
            "status": "online" if online else "offline",
            "last_seen": (_now() - timedelta(minutes=rng.randint(0, 60) if online else rng.randint(60, 20000))).isoformat(),
        })
    out.sort(key=lambda x: x["risk_score"], reverse=True)
    return out


def assets_summary(items: list[dict] | None = None) -> dict:
    items = items or assets_inventory()
    by_type: dict[str, int] = {}
    for a in items:
        by_type[a["type"]] = by_type.get(a["type"], 0) + 1
    return {
        "total": len(items),
        "critical": sum(1 for a in items if a["criticality"] == "critical"),
        "at_risk": sum(1 for a in items if a["risk_score"] >= 70),
        "offline": sum(1 for a in items if a["status"] == "offline"),
        "by_type": by_type,
    }


def assets_overview() -> dict:
    items = assets_inventory()
    return {"summary": assets_summary(items), "items": items}


# ── Vulnerability Management ─────────────────────────────────────────────
VULN_TITLES = [
    "Exécution de code à distance via désérialisation non sécurisée",
    "Contournement d'authentification sur interface d'administration",
    "Élévation de privilèges via pilote noyau vulnérable",
    "Injection de commandes dans le service web exposé",
    "Divulgation d'informations sensibles via API mal configurée",
    "Débordement de tampon dans la bibliothèque de traitement d'images",
    "Falsification de requête côté serveur (SSRF)",
    "Vulnérabilité XXE dans le parseur XML",
    "Contournement de la validation de certificat TLS",
    "Path traversal permettant la lecture de fichiers arbitraires",
]
VULN_STATUSES = ["open", "patching", "patched", "accepted_risk"]


def vulnerabilities(limit: int = 50) -> list[dict]:
    rng = _rng("vulns")
    out = []
    for i in range(limit):
        cvss = round(rng.uniform(3.0, 9.9), 1)
        severity = "critical" if cvss >= 9 else "high" if cvss >= 7 else "medium" if cvss >= 4 else "low"
        status = rng.choices(VULN_STATUSES, weights=[3, 2, 4, 1])[0]
        published = _now() - timedelta(days=rng.randint(2, 700))
        out.append({
            "id": f"CVE-{published.year}-{rng.randint(10000, 49999)}",
            "title": rng.choice(VULN_TITLES),
            "cvss": cvss,
            "severity": severity,
            "asset": rng.choice(ASSETS),
            "status": status,
            "exploit_available": rng.random() < 0.22,
            "published_at": published.isoformat(),
            "days_open": (rng.randint(1, 90) if status in ("open", "patching") else 0),
        })
    out.sort(key=lambda x: x["cvss"], reverse=True)
    return out


def vulnerabilities_summary(items: list[dict] | None = None) -> dict:
    items = items or vulnerabilities()
    rng = _rng("vulns-sum")
    open_items = [v for v in items if v["status"] in ("open", "patching")]
    return {
        "total": len(items),
        "open": len(open_items),
        "critical_open": sum(1 for v in open_items if v["severity"] == "critical"),
        "exploit_available": sum(1 for v in open_items if v["exploit_available"]),
        "patch_compliance_pct": rng.randint(72, 93),
        "avg_days_to_patch": rng.randint(6, 22),
    }


def vulnerabilities_overview() -> dict:
    items = vulnerabilities()
    return {"summary": vulnerabilities_summary(items), "items": items}


# ── Compliance Center ─────────────────────────────────────────────────────
COMPLIANCE_FRAMEWORKS = ["ISO 27001", "NIST CSF", "PCI DSS", "RGPD", "SOC 2"]
CONTROL_CATEGORIES = ["Gestion des accès", "Chiffrement", "Journalisation", "Continuité d'activité",
                       "Gestion des vulnérabilités", "Sensibilisation", "Réponse à incident"]


def compliance_frameworks() -> list[dict]:
    rng = _rng("compliance-fw")
    out = []
    for fw in COMPLIANCE_FRAMEWORKS:
        total = rng.randint(60, 140)
        passed = int(total * rng.uniform(0.75, 0.97))
        failed = total - passed
        out.append({
            "name": fw,
            "score": round(100 * passed / total, 1),
            "controls_total": total,
            "controls_passed": passed,
            "controls_failed": failed,
            "last_audit": (_now() - timedelta(days=rng.randint(10, 200))).isoformat(),
            "next_audit": (_now() + timedelta(days=rng.randint(30, 180))).isoformat(),
        })
    return out


def compliance_controls(limit: int = 30) -> list[dict]:
    rng = _rng("compliance-ctrl")
    out = []
    for i in range(limit):
        status = rng.choices(["compliant", "partial", "non_compliant"], weights=[6, 2, 1])[0]
        out.append({
            "id": f"CTL-{500 + i}",
            "framework": rng.choice(COMPLIANCE_FRAMEWORKS),
            "category": rng.choice(CONTROL_CATEGORIES),
            "name": f"{rng.choice(CONTROL_CATEGORIES)} — contrôle {i + 1}",
            "status": status,
            "evidence_count": rng.randint(0, 8),
            "owner": rng.choice(ASSET_OWNERS),
        })
    return out


def compliance_overview() -> dict:
    frameworks = compliance_frameworks()
    return {
        "frameworks": frameworks,
        "controls": compliance_controls(),
        "summary": {
            "overall_score": round(sum(f["score"] for f in frameworks) / len(frameworks), 1),
            "frameworks_tracked": len(frameworks),
            "controls_failed": sum(f["controls_failed"] for f in frameworks),
        },
    }
