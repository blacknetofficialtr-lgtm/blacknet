from __future__ import annotations

import os
from pathlib import Path

from warningnet.services.database import Database


class FileSearchService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def index_directory(self, root: Path) -> int:
        count = 0
        with self.db.connect() as conn:
            for base, _, files in os.walk(root):
                for filename in files:
                    path = Path(base) / filename
                    try:
                        stat = path.stat()
                    except OSError:
                        continue
                    conn.execute(
                        """
                        INSERT INTO indexed_files(path, name, extension, size, modified_at)
                        VALUES(?, ?, ?, ?, ?)
                        ON CONFLICT(path) DO UPDATE SET
                            name=excluded.name,
                            extension=excluded.extension,
                            size=excluded.size,
                            modified_at=excluded.modified_at
                        """,
                        (str(path), path.name, path.suffix.lower(), stat.st_size, stat.st_mtime),
                    )
                    count += 1
        self.db.log_activity("file_search", f"indexed {count} files under {root}")
        return count

    def search(self, query: str, extension: str = "") -> list[dict]:
        like_query = f"%{query}%"
        extension = extension.lower().strip()
        with self.db.connect() as conn:
            if extension:
                rows = conn.execute(
                    "SELECT * FROM indexed_files WHERE name LIKE ? AND extension = ? ORDER BY modified_at DESC LIMIT 500",
                    (like_query, extension if extension.startswith(".") else f".{extension}"),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM indexed_files WHERE name LIKE ? ORDER BY modified_at DESC LIMIT 500",
                    (like_query,),
                ).fetchall()
        return [dict(row) for row in rows]
