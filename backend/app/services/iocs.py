"""Extraction d'indicateurs de compromission (IoC) depuis une alerte Wazuh brute."""
import re


def is_private_ip(ip: str) -> bool:
    try:
        parts = list(map(int, ip.split(".")))
        if parts[0] == 10:
            return True
        if parts[0] == 172 and 16 <= parts[1] <= 31:
            return True
        if parts[0] == 192 and parts[1] == 168:
            return True
        if parts[0] in (127,):
            return True
        if parts[0] == 169 and parts[1] == 254:
            return True
    except Exception:
        pass
    return False


def extract_iocs(alert: dict) -> list[dict]:
    iocs = []
    data = alert.get("data", {}) or {}
    for field in ("srcip", "src_ip", "sourceip"):
        ip = data.get(field) or alert.get(field)
        if ip and re.match(r"^\d{1,3}(\.\d{1,3}){3}$", str(ip)) and not is_private_ip(str(ip)):
            iocs.append({"type": "ip", "value": str(ip)})
    for field in ("dstip", "dst_ip"):
        ip = data.get(field)
        if ip and re.match(r"^\d{1,3}(\.\d{1,3}){3}$", str(ip)) and not is_private_ip(str(ip)):
            iocs.append({"type": "ip", "value": str(ip)})
    for field in ("md5", "sha256", "hash"):
        h = data.get(field) or alert.get(field)
        if h and re.match(r"^[a-fA-F0-9]{32,64}$", str(h)):
            iocs.append({"type": "sha256" if len(str(h)) == 64 else "md5", "value": str(h)})
    full_log = alert.get("full_log", "")
    if full_log:
        for u in re.findall(r"https?://[^\s\"'<>]+", str(full_log))[:2]:
            iocs.append({"type": "url", "value": u})
        for d in re.findall(r"\b(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b", str(full_log))[:2]:
            if d not in ("localhost", "local"):
                iocs.append({"type": "domain", "value": d})
    seen, unique = set(), []
    for ioc in iocs:
        if ioc["value"] not in seen:
            seen.add(ioc["value"])
            unique.append(ioc)
    return unique
