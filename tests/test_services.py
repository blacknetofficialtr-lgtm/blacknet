from pathlib import Path

from warningnet.modules.network_analyzer import analyze_url
from warningnet.modules.premium import PremiumService
from warningnet.services.database import Database
from warningnet.services.security import decrypt_bytes, encrypt_bytes


def test_encrypt_roundtrip():
    data = b"secret-warningnet-data"
    payload = encrypt_bytes(data, "StrongPassword123!")
    restored = decrypt_bytes(payload, "StrongPassword123!")
    assert restored == data


def test_network_analyzer_score():
    result = analyze_url("http://free-bonus-login.xyz/verify")
    assert result["score"] >= 30
    assert result["risk"] in {"Orta", "Yüksek"}


def test_premium_activation(tmp_path: Path):
    db = Database(tmp_path / "test.db")
    premium = PremiumService(db)
    assert premium.activate("WARNINGNET-50TL") is True
    assert premium.is_active() is True
