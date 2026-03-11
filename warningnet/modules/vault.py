from __future__ import annotations

import time
import uuid
from pathlib import Path

from warningnet.services.database import APP_DIR, Database
from warningnet.services.security import decrypt_bytes, encrypt_bytes

VAULT_DIR = APP_DIR / "vault"
DATA_DIR = VAULT_DIR / "data"


class VaultService:
    def __init__(self, db: Database) -> None:
        self.db = db
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def add_file(self, source_file: Path, password: str) -> str:
        blob_id = str(uuid.uuid4())
        target = DATA_DIR / f"{blob_id}.bin"
        encrypted = encrypt_bytes(source_file.read_bytes(), password)
        target.write_bytes(encrypted)

        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO vault_items(id, original_name, stored_path, created_at) VALUES(?, ?, ?, ?)",
                (blob_id, source_file.name, str(target), time.time()),
            )
        self.db.log_activity("vault", f"added file {source_file}")
        return blob_id

    def list_items(self) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM vault_items ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def extract(self, item_id: str, output_file: Path, password: str) -> None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM vault_items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise ValueError("Vault öğesi bulunamadı")

        payload = Path(row["stored_path"]).read_bytes()
        decrypted = decrypt_bytes(payload, password)
        output_file.write_bytes(decrypted)
        self.db.log_activity("vault", f"extracted item {item_id}")
