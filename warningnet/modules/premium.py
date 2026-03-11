from __future__ import annotations

from warningnet.services.database import Database

PREMIUM_CODE = "WARNINGNET-50TL"


class PremiumService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def is_active(self) -> bool:
        return self.db.get_setting("premium_active", "0") == "1"

    def activate(self, code: str) -> bool:
        if code.strip().upper() == PREMIUM_CODE:
            self.db.set_setting("premium_active", "1")
            self.db.log_activity("premium", "premium activated")
            return True
        return False
