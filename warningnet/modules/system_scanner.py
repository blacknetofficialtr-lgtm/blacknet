from __future__ import annotations

import shutil
from pathlib import Path


def disk_summary(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "used_percent": round((usage.used / usage.total) * 100, 2) if usage.total else 0,
    }


def largest_files(path: Path, limit: int = 20) -> list[dict]:
    files: list[dict] = []
    for p in path.rglob("*"):
        if p.is_file():
            try:
                size = p.stat().st_size
            except OSError:
                continue
            files.append({"path": str(p), "size": size})
    return sorted(files, key=lambda x: x["size"], reverse=True)[:limit]
