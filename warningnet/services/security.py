from __future__ import annotations

import hashlib
import hmac
import os

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    HAS_CRYPTOGRAPHY = True
except Exception:  # pragma: no cover
    HAS_CRYPTOGRAPHY = False


def _derive_key_std(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390000, dklen=32)


def _xor_stream(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt_bytes(data: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)

    if HAS_CRYPTOGRAPHY:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
        key = kdf.derive(password.encode("utf-8"))
        ciphertext = AESGCM(key).encrypt(nonce, data, None)
        return b"AES1" + salt + nonce + ciphertext

    key = _derive_key_std(password, salt)
    ciphertext = _xor_stream(data, key)
    mac = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return b"XOR1" + salt + nonce + mac + ciphertext


def decrypt_bytes(payload: bytes, password: str) -> bytes:
    mode = payload[:4]
    salt = payload[4:20]
    nonce = payload[20:32]

    if mode == b"AES1":
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("AES çözme için cryptography paketi gerekli")
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
        key = kdf.derive(password.encode("utf-8"))
        return AESGCM(key).decrypt(nonce, payload[32:], None)

    if mode == b"XOR1":
        key = _derive_key_std(password, salt)
        mac = payload[32:64]
        ciphertext = payload[64:]
        calc = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, calc):
            raise ValueError("Parola hatalı veya veri bozulmuş")
        return _xor_stream(ciphertext, key)

    raise ValueError("Bilinmeyen şifreleme formatı")
