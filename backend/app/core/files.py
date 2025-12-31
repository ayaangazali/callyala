"""File utilities with atomic writes and locking."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

import portalocker

from .logging import logger


def atomic_write_json(path: Path, data: Any, indent: int = 2) -> None:
    """Atomically write JSON to file with locking."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file first
    fd, tmp_path = tempfile.mkstemp(
        suffix=".tmp",
        prefix=path.stem + "_",
        dir=path.parent,
    )
    
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        # Atomic rename
        os.replace(tmp_path, path)
        logger.debug(f"Atomic write to {path}")
    except Exception:
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def read_json(path: Path, default: Any = None) -> Any:
    """Read JSON file with optional default."""
    path = Path(path)
    if not path.exists():
        return default
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(path: Path, record: dict) -> None:
    """Append a single JSON record to JSONL file with locking."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with portalocker.Lock(path, "a", timeout=10) as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        f.flush()


def read_jsonl(path: Path) -> list[dict]:
    """Read all records from JSONL file."""
    path = Path(path)
    if not path.exists():
        return []
    
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON line in {path}")
    return records


class LockedFile:
    """Context manager for locked file operations."""

    def __init__(self, path: Path, mode: str = "r+", timeout: int = 10):
        self.path = Path(path)
        self.mode = mode
        self.timeout = timeout
        self._lock: Optional[portalocker.Lock] = None

    def __enter__(self):
        # Ensure file exists for read modes
        if "r" in self.mode and not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("{}" if self.path.suffix == ".json" else "")
        
        self._lock = portalocker.Lock(self.path, self.mode, timeout=self.timeout)
        return self._lock.__enter__()

    def __exit__(self, *args):
        if self._lock:
            return self._lock.__exit__(*args)
