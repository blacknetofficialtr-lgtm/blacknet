from __future__ import annotations

from urllib.parse import urlparse

SUSPICIOUS_TLDS = {"zip", "mov", "cam", "xyz", "top", "gq"}
SUSPICIOUS_KEYWORDS = {"login", "verify", "bank", "wallet", "free", "bonus", "urgent"}


def analyze_url(url: str) -> dict:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    score = 0
    findings: list[str] = []

    if parsed.scheme not in {"https", "http"}:
        score += 30
        findings.append("Geçersiz veya güvenilmeyen protokol")

    if "@" in url or ".." in host:
        score += 25
        findings.append("Maskeleme belirtisi bulundu")

    if host:
        tld = host.split(".")[-1]
        if tld in SUSPICIOUS_TLDS:
            score += 20
            findings.append(f"Şüpheli TLD: .{tld}")

    text = f"{host} {path}"
    matched = [k for k in SUSPICIOUS_KEYWORDS if k in text]
    if matched:
        score += min(25, len(matched) * 7)
        findings.append(f"Şüpheli anahtar kelimeler: {', '.join(matched)}")

    if len(host) > 45:
        score += 10
        findings.append("Aşırı uzun alan adı")

    score = min(score, 100)
    risk = "Düşük" if score < 30 else "Orta" if score < 60 else "Yüksek"
    return {"url": url, "score": score, "risk": risk, "findings": findings}
