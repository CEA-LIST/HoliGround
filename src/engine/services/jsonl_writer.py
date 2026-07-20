from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class JsonlWriter:
    """Simple JSONL writer that appends one record per line."""

    def __init__(self, path: Path, mode: str = 'w') -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._handle = path.open(mode, encoding='utf-8')

    def write(self, record: Dict[str, Any]) -> None:
        json_line = json.dumps(record, ensure_ascii=False)
        self._handle.write(json_line + '\n')
        self._handle.flush()

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.close()

    def __del__(self) -> None:  # pragma: no cover
        self.close()

