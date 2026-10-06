"""Private, atomic response recordings shared by model providers."""

import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from sns_recommend.core.config import settings


def recording_path(kind, encoded):
    return Path(settings().recordings_dir) / (
        hashlib.sha256(encoded.encode()).hexdigest() + f"-{kind}.json"
    )


def write_recording(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        # NamedTemporaryFile creates a file readable only by its owner (0600).
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
            temporary = Path(f.name)
            json.dump(data, f, ensure_ascii=False, allow_nan=False)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
