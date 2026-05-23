import secrets
import shutil
import tempfile
import os
from datetime import datetime


class ConfidentialityManager:
    def __init__(self):
        self.session_id = secrets.token_hex(16)
        self.workspace = tempfile.mkdtemp(prefix=f"proofdoc_{self.session_id[:8]}_")
        self.audit_log = []

    def log_action(self, action: str, filename: str, confidence: float = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session": self.session_id[:8],
            "action": action,
            "file": filename,
            "confidence": confidence,
        }
        self.audit_log.append(entry)
        return entry

    def secure_path(self, filename: str) -> str:
        return os.path.join(self.workspace, os.path.basename(filename))

    def cleanup(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def get_audit_report(self) -> list:
        return self.audit_log
