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


def _ioc_value(kind: str, rng: random.Random, i: int) -> str:
    return {
        "ip": f"{rng.randint(11,223)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
        "domain": rng.choice(["evil-cdn.ru", "login-secure.tk", "update-flash.cn", "pay-invoice.xyz", "cloud-sync.top"]),
        "hash": hashlib.sha256(f"ioc-{i}".encode()).hexdigest(),
        "url": "http://malicious.example/payload",
    }[kind]


# ── IOC Management ────────────────────────────────────────────────────────
def ioc_management(limit: int = 60) -> list[dict]:
    rng = _rng("ioc-mgmt")
    kinds = ["ip", "domain", "hash", "url"]
    sources = ["MISP", "VirusTotal", "Recorded Future", "Interne (SOC)", "OTX AlienVault"]
    out = []
    for i in range(limit):
        kind = rng.choice(kinds)
        added = _now() - timedelta(days=rng.randint(0, 60))
        ttl_days = rng.choice([30, 60, 90, 180])
        expires = added + timedelta(days=ttl_days)
        out.append({
            "id": f"IOC-{6000 + i}",
            "type": kind,
            "value": _ioc_value(kind, rng, i),
            "verdict": rng.choice(["malicious", "suspicious", "clean"]),
            "confidence": rng.randint(40, 99),
            "source": rng.choice(sources),
            "tags": rng.sample(["ransomware", "phishing", "c2", "botnet", "apt", "scanner"], k=rng.randint(1, 2)),
            "matches": rng.randint(0, 240),
            "status": "expired" if expires < _now() else rng.choices(["active", "whitelisted"], weights=[9, 1])[0],
            "added_at": added.isoformat(),
            "expires_at": expires.isoformat(),
        })
    out.sort(key=lambda x: x["matches"], reverse=True)
    return out


def ioc_summary(items: list[dict] | None = None) -> dict:
    items = items or ioc_management()
    rng = _rng("ioc-sum")
    active = [i for i in items if i["status"] == "active"]
    return {
        "total": len(items),
        "active": len(active),
        "expiring_soon": sum(1 for i in active if datetime.fromisoformat(i["expires_at"]) - _now() < timedelta(days=7)),
        "matches_today": rng.randint(80, 400),
        "false_positive_rate": round(rng.uniform(2.0, 8.0), 1),
    }


def ioc_overview() -> dict:
    items = ioc_management()
    return {"summary": ioc_summary(items), "items": items}


# ── UEBA (User & Entity Behavior Analytics) ──────────────────────────────
UEBA_DEPARTMENTS = ["Finance", "RH", "IT", "Ventes", "Direction", "R&D"]
ANOMALY_TYPES = [
    "Voyage impossible (connexions géo-incohérentes)", "Téléchargement de masse inhabituel",
    "Accès hors horaires habituels", "Pic d'utilisation de privilèges", "Accès à des ressources jamais utilisées",
    "Volume d'e-mails sortants anormal", "Connexion depuis un nouvel appareil non enrôlé",
]


def ueba_entities(limit: int = 40) -> list[dict]:
    rng = _rng("ueba-ent")
    first_names = ["Amine", "Léa", "Sami", "Karim", "Nora", "Yassine", "Chloé", "Omar", "Inès", "Hugo"]
    last_names = ["Martin", "Dubois", "Nguyen", "Moreau", "Bennani", "Alaoui", "Girard", "Lefevre"]
    out = []
    for i in range(limit):
        risk = rng.randint(5, 98)
        out.append({
            "id": f"ENT-{7000 + i}",
            "name": f"{rng.choice(first_names)} {rng.choice(last_names)}",
            "department": rng.choice(UEBA_DEPARTMENTS),
            "risk_score": risk,
            "anomalies_7d": rng.randint(0, 12),
            "baseline_deviation_pct": rng.randint(-20, 180),
            "last_anomaly": (_now() - timedelta(hours=rng.randint(1, 400))).isoformat(),
        })
    out.sort(key=lambda x: x["risk_score"], reverse=True)
    return out


def ueba_anomalies(limit: int = 25) -> list[dict]:
    rng = _rng("ueba-anom")
    entities = ueba_entities()
    out = []
    for i in range(limit):
        entity = rng.choice(entities)
        severity = rng.choices(["critical", "high", "medium", "low"], weights=[1, 3, 5, 3])[0]
        out.append({
            "id": f"ANOM-{8000 + i}",
            "entity": entity["name"],
            "department": entity["department"],
            "type": rng.choice(ANOMALY_TYPES),
            "severity": severity,
            "detected_at": (_now() - timedelta(hours=rng.randint(0, 72))).isoformat(),
        })
    out.sort(key=lambda x: x["detected_at"], reverse=True)
    return out


def ueba_summary(entities: list[dict] | None = None) -> dict:
    entities = entities or ueba_entities()
    rng = _rng("ueba-sum")
    return {
        "entities_monitored": len(entities),
        "high_risk": sum(1 for e in entities if e["risk_score"] >= 70),
        "anomalies_today": rng.randint(6, 34),
        "avg_risk_score": round(sum(e["risk_score"] for e in entities) / len(entities), 1),
    }


def ueba_overview() -> dict:
    entities = ueba_entities()
    return {"summary": ueba_summary(entities), "entities": entities, "anomalies": ueba_anomalies()}


# ── Risk Management ───────────────────────────────────────────────────────
RISK_CATEGORIES = ["Technique", "Opérationnel", "Conformité", "Tiers / Fournisseur", "Stratégique"]
RISK_TITLES = [
    "Dépendance à un fournisseur cloud unique", "Absence de MFA sur comptes à privilèges legacy",
    "Segmentation réseau insuffisante en environnement OT", "Obsolescence de composants tiers non patchés",
    "Sensibilisation insuffisante au phishing", "Plan de continuité d'activité non testé",
    "Accès tiers non revus périodiquement", "Chiffrement absent sur sauvegardes hors site",
    "Shadow IT sur applications SaaS non validées", "Délai de détection élevé sur environnement cloud",
]
RISK_STATUSES = ["open", "mitigating", "accepted_risk", "closed"]


def risk_register(limit: int = 24) -> list[dict]:
    rng = _rng("risk-reg")
    out = []
    for i in range(limit):
        likelihood = rng.randint(1, 5)
        impact = rng.randint(1, 5)
        score = likelihood * impact
        out.append({
            "id": f"RISK-{900 + i}",
            "title": rng.choice(RISK_TITLES),
            "category": rng.choice(RISK_CATEGORIES),
            "likelihood": likelihood,
            "impact": impact,
            "score": score,
            "level": "critical" if score >= 20 else "high" if score >= 12 else "medium" if score >= 6 else "low",
            "owner": rng.choice(ANALYSTS)["name"],
            "status": rng.choices(RISK_STATUSES, weights=[3, 3, 2, 2])[0],
            "updated_at": (_now() - timedelta(days=rng.randint(0, 90))).isoformat(),
        })
    out.sort(key=lambda x: x["score"], reverse=True)
    return out


def risk_summary(items: list[dict] | None = None) -> dict:
    items = items or risk_register()
    by_category: dict[str, int] = {}
    for r in items:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
    return {
        "total": len(items),
        "critical_high": sum(1 for r in items if r["level"] in ("critical", "high")),
        "open": sum(1 for r in items if r["status"] == "open"),
        "avg_score": round(sum(r["score"] for r in items) / len(items), 1),
        "by_category": by_category,
    }


def risk_overview() -> dict:
    items = risk_register()
    return {"summary": risk_summary(items), "items": items}


# ── Case Management ───────────────────────────────────────────────────────
CASE_TITLES = [
    "Investigation compromission compte à privilèges", "Suspicion d'exfiltration de données client",
    "Analyse forensique poste de travail direction", "Campagne de phishing ciblée — RH",
    "Revue post-incident ransomware", "Enquête sur activité réseau anormale (OT)",
    "Suspicion de fraude interne — accès financiers", "Investigation malware sur serveur exposé",
]
CASE_STATUSES = ["open", "in_review", "closed"]
CASE_PRIORITIES = ["critical", "high", "medium", "low"]


def cases(limit: int = 30) -> list[dict]:
    rng = _rng("cases")
    out = []
    for i in range(limit):
        created = _now() - timedelta(days=rng.randint(0, 45))
        status = rng.choices(CASE_STATUSES, weights=[3, 2, 4])[0]
        priority = rng.choice(CASE_PRIORITIES)
        sla_days = {"critical": 2, "high": 5, "medium": 10, "low": 20}[priority]
        due = created + timedelta(days=sla_days)
        out.append({
            "id": f"CASE-{created.strftime('%Y%m')}-{400 + i}",
            "title": rng.choice(CASE_TITLES),
            "priority": priority,
            "status": status,
            "analyst": rng.choice(ANALYSTS)["name"],
            "related_incidents": rng.randint(0, 5),
            "created_at": created.isoformat(),
            "due_at": due.isoformat(),
            "overdue": status != "closed" and due < _now(),
        })
    out.sort(key=lambda x: x["created_at"], reverse=True)
    return out


def cases_summary(items: list[dict] | None = None) -> dict:
    items = items or cases()
    return {
        "total": len(items),
        "open": sum(1 for c in items if c["status"] == "open"),
        "overdue": sum(1 for c in items if c["overdue"]),
        "closed": sum(1 for c in items if c["status"] == "closed"),
    }


def cases_overview() -> dict:
    items = cases()
    return {"summary": cases_summary(items), "items": items}


# ── SIEM ───────────────────────────────────────────────────────────────
SIEM_SOURCES = ["Windows Event Log", "Firewall (Edge)", "Linux Auditd", "Cloud (AWS CloudTrail)", "IDS/IPS", "Proxy Web", "EDR"]
SIEM_EVENT_TYPES = [
    ("Authentication", "Échec d'authentification répété"), ("Network", "Trafic sortant vers IP suspecte"),
    ("Process", "Création de processus inhabituelle"), ("File", "Modification de fichier système critique"),
    ("Policy", "Violation de politique de pare-feu"), ("DNS", "Résolution DNS vers domaine à risque"),
]


def siem_events(limit: int = 60) -> list[dict]:
    rng = _rng("siem-events")
    out = []
    for i in range(limit):
        category, msg = rng.choice(SIEM_EVENT_TYPES)
        out.append({
            "id": f"EVT-{900000 + i}",
            "timestamp": (_now() - timedelta(seconds=rng.randint(0, 3600 * 6))).isoformat(),
            "source": rng.choice(SIEM_SOURCES),
            "category": category,
            "message": msg,
            "host": rng.choice(ASSETS),
            "severity": rng.choices(SEVERITIES, weights=[1, 3, 6, 8])[0],
        })
    out.sort(key=lambda x: x["timestamp"], reverse=True)
    return out


def siem_summary() -> dict:
    rng = _rng("siem-sum")
    return {
        "events_per_sec": rng.randint(850, 2400),
        "events_today": rng.randint(48_000_000, 72_000_000),
        "sources_connected": len(SIEM_SOURCES),
        "storage_used_tb": round(rng.uniform(4.2, 9.8), 1),
        "retention_days": 180,
    }


def siem_sources_breakdown() -> list[dict]:
    rng = _rng("siem-src")
    return [{"source": s, "events": rng.randint(500, 9000)} for s in SIEM_SOURCES]


def siem_overview() -> dict:
    return {
        "summary": siem_summary(),
        "sources": siem_sources_breakdown(),
        "events": siem_events(),
    }


# ── SOAR Playbooks ────────────────────────────────────────────────────────
PLAYBOOK_DEFS = [
    ("Confinement — poste compromis", "Malware détecté (EDR)", "Confinement"),
    ("Blocage IOC automatique", "Nouvel IOC malveillant reçu", "Threat Intel"),
    ("Réinitialisation identifiants", "Brute-force réussi détecté", "Identity"),
    ("Enrichissement d'alerte", "Nouvelle alerte SIEM créée", "Enrichissement"),
    ("Isolation réseau VLAN", "Mouvement latéral suspecté", "Confinement"),
    ("Notification équipe conformité", "Violation de politique DLP", "Conformité"),
    ("Blocage expéditeur phishing", "Campagne de phishing signalée", "Email Security"),
    ("Escalade incident critique", "Incident sévérité critique créé", "Escalade"),
]


def soar_playbooks() -> list[dict]:
    rng = _rng("soar")
    out = []
    for i, (name, trigger, category) in enumerate(PLAYBOOK_DEFS):
        executions = rng.randint(20, 400)
        out.append({
            "id": f"PB-{100 + i}",
            "name": name,
            "trigger": trigger,
            "category": category,
            "status": rng.choices(["active", "draft", "disabled"], weights=[7, 2, 1])[0],
            "executions_30d": executions,
            "success_rate": round(rng.uniform(82, 99.5), 1),
            "avg_duration_sec": rng.randint(8, 240),
            "last_run": (_now() - timedelta(hours=rng.randint(0, 48))).isoformat(),
        })
    return out


def soar_summary(items: list[dict] | None = None) -> dict:
    items = items or soar_playbooks()
    rng = _rng("soar-sum")
    return {
        "total": len(items),
        "active": sum(1 for p in items if p["status"] == "active"),
        "executions_today": rng.randint(60, 260),
        "time_saved_hours": rng.randint(120, 480),
    }


def soar_overview() -> dict:
    items = soar_playbooks()
    return {"summary": soar_summary(items), "playbooks": items}


# ── Detection Engineering ─────────────────────────────────────────────────
DETECTION_RULE_NAMES = [
    "Connexion admin domaine hors horaires", "Exécution PowerShell encodée",
    "Kerberoasting — requêtes TGS anormales", "Création de tâche planifiée suspecte",
    "Transfert de fichier volumineux vers externe", "Désactivation des journaux d'audit",
    "Nouveau compte ajouté aux administrateurs", "Connexion RDP depuis IP externe",
    "Exécution depuis répertoire temporaire", "Modification de clé de registre Run",
    "Balayage de ports interne", "Requête DNS vers domaine récemment enregistré",
]


def detection_rules() -> list[dict]:
    rng = _rng("detection")
    out = []
    for i, name in enumerate(DETECTION_RULE_NAMES):
        tid, tactic = rng.choice(MITRE_TACTICS)
        out.append({
            "id": f"RULE-{200 + i}",
            "name": name,
            "mitre_tactic": tactic,
            "mitre_id": tid,
            "severity": rng.choice(SEVERITIES),
            "status": rng.choices(["enabled", "tuning", "disabled"], weights=[7, 2, 1])[0],
            "false_positive_rate": round(rng.uniform(0.5, 18.0), 1),
            "hits_7d": rng.randint(0, 140),
            "author": rng.choice(ANALYSTS)["name"],
            "updated_at": (_now() - timedelta(days=rng.randint(1, 120))).isoformat(),
        })
    return out


def detection_summary(items: list[dict] | None = None) -> dict:
    items = items or detection_rules()
    return {
        "total": len(items),
        "enabled": sum(1 for r in items if r["status"] == "enabled"),
        "avg_fp_rate": round(sum(r["false_positive_rate"] for r in items) / len(items), 1),
        "hits_7d": sum(r["hits_7d"] for r in items),
    }


def detection_overview() -> dict:
    items = detection_rules()
    return {"summary": detection_summary(items), "rules": items}


# ── Threat Hunting ─────────────────────────────────────────────────────────
HUNT_HYPOTHESES = [
    "Persistance via tâches planifiées non signées sur serveurs critiques",
    "Exfiltration lente via DNS tunneling sur le segment finance",
    "Comptes de service utilisés en dehors de leur périmètre habituel",
    "Mouvement latéral via WMI non détecté par les règles actuelles",
    "Utilisation d'outils LOLBins pour contourner l'EDR",
    "Communications C2 déguisées en trafic HTTPS légitime",
]
HUNT_STATUSES = ["planned", "in_progress", "completed"]


def threat_hunts() -> list[dict]:
    rng = _rng("hunts")
    out = []
    for i, hyp in enumerate(HUNT_HYPOTHESES):
        started = _now() - timedelta(days=rng.randint(2, 60))
        status = rng.choice(HUNT_STATUSES)
        tid, tactic = rng.choice(MITRE_TACTICS)
        out.append({
            "id": f"HUNT-{50 + i}",
            "hypothesis": hyp,
            "status": status,
            "analyst": rng.choice(ANALYSTS)["name"],
            "mitre_tactic": tactic,
            "findings": rng.randint(0, 6) if status != "planned" else 0,
            "started_at": started.isoformat(),
        })
    return out


def hunting_summary(items: list[dict] | None = None) -> dict:
    items = items or threat_hunts()
    rng = _rng("hunt-sum")
    return {
        "total": len(items),
        "active": sum(1 for h in items if h["status"] == "in_progress"),
        "findings_total": sum(h["findings"] for h in items),
        "coverage_pct": rng.randint(58, 82),
    }


def hunting_overview() -> dict:
    items = threat_hunts()
    return {"summary": hunting_summary(items), "hunts": items}


# ── Analyst Workspace ──────────────────────────────────────────────────────
def analyst_workspace(analyst_name: str) -> dict:
    rng = _rng(f"workspace-{analyst_name}")
    my_incidents = incidents(15)[:6]
    for inc in my_incidents:
        inc["assignee"] = analyst_name
    my_cases = cases(10)[:4]
    for c in my_cases:
        c["analyst"] = analyst_name
    return {
        "analyst": analyst_name,
        "kpis": {
            "open_assigned": rng.randint(3, 9),
            "resolved_today": rng.randint(2, 8),
            "avg_response_min": round(rng.uniform(4, 18), 1),
            "sla_at_risk": rng.randint(0, 3),
        },
        "incidents": my_incidents,
        "cases": my_cases,
        "shift": {
            "team_on_duty": rng.choice(["Équipe A", "Équipe B", "Équipe C"]),
            "handover_at": (_now() + timedelta(hours=rng.randint(1, 8))).isoformat(),
        },
    }


# ── Audit Center ───────────────────────────────────────────────────────────
AUDIT_ACTIONS = [
    "Connexion réussie", "Échec de connexion", "Modification de rôle utilisateur",
    "Changement de statut d'incident", "Export de rapport", "Modification de règle de détection",
    "Consultation de dossier confidentiel", "Désactivation d'un compte", "Création d'une clé API",
    "Modification de politique de conformité",
]
AUDIT_ACTORS = ["admin@aegis.local", "ciso@aegis.local", "manager@aegis.local", "analyst@aegis.local", "auditor@aegis.local"]


def audit_log(limit: int = 60) -> list[dict]:
    rng = _rng("audit")
    out = []
    for i in range(limit):
        action = rng.choice(AUDIT_ACTIONS)
        failed = "Échec" in action
        out.append({
            "id": f"AUD-{10000 + i}",
            "timestamp": (_now() - timedelta(minutes=rng.randint(0, 60 * 24 * 14))).isoformat(),
            "actor": rng.choice(AUDIT_ACTORS),
            "action": action,
            "target": rng.choice(["INC-2026-2031", "Règle RULE-204", "Utilisateur k.moreau", "Rapport SOC Mensuel", "Politique ISO 27001"]),
            "ip_address": f"{rng.randint(11,223)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
            "result": "failed" if failed and rng.random() < 0.7 else "success",
        })
    out.sort(key=lambda x: x["timestamp"], reverse=True)
    return out


def audit_summary(items: list[dict] | None = None) -> dict:
    items = items or audit_log()
    return {
        "events_today": sum(1 for a in items if datetime.fromisoformat(a["timestamp"]) > _now() - timedelta(days=1)),
        "failed_logins_24h": sum(1 for a in items if a["action"] == "Échec de connexion" and datetime.fromisoformat(a["timestamp"]) > _now() - timedelta(days=1)),
        "admin_actions_7d": sum(1 for a in items if a["actor"] == "admin@aegis.local" and datetime.fromisoformat(a["timestamp"]) > _now() - timedelta(days=7)),
        "exports_7d": sum(1 for a in items if a["action"] == "Export de rapport" and datetime.fromisoformat(a["timestamp"]) > _now() - timedelta(days=7)),
    }


def audit_overview() -> dict:
    items = audit_log()
    return {"summary": audit_summary(items), "items": items}


# ── Administration ─────────────────────────────────────────────────────────
def admin_system_settings() -> dict:
    rng = _rng("admin-sys")
    return {
        "mfa_enforced": True,
        "sso_enabled": rng.choice([True, False]),
        "session_timeout_min": rng.choice([30, 45, 60]),
        "password_policy": "Min. 12 caractères, rotation 90 jours, MFA obligatoire",
        "api_keys_active": rng.randint(3, 12),
        "data_retention_days": 365,
    }


def admin_license() -> dict:
    rng = _rng("admin-lic")
    seats_total = 50
    return {
        "plan": "Enterprise",
        "seats_used": rng.randint(18, seats_total),
        "seats_total": seats_total,
        "renews_at": (_now() + timedelta(days=rng.randint(30, 300))).isoformat(),
    }


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
