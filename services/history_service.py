"""History service for persisting QR code generation history."""

from __future__ import annotations

import json
from pathlib import Path

from core.config import HISTORY_FILE, HISTORY_MAX_ENTRIES
from core.exceptions import HistoryError
from domain.models import HistoryEntry


class HistoryService:
    """Service for managing QR code generation history."""

    def __init__(self) -> None:
        self._path = Path(HISTORY_FILE).expanduser()
        self._entries: list[HistoryEntry] = []
        self._load()

    def add_entry(self, entry: HistoryEntry) -> None:
        """Add a new history entry, pruning old ones if needed."""
        self._entries.insert(0, entry)
        if len(self._entries) > HISTORY_MAX_ENTRIES:
            self._entries = self._entries[:HISTORY_MAX_ENTRIES]
        self._save()

    def get_entries(self) -> list[HistoryEntry]:
        """Return all history entries, most recent first."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear all history entries."""
        self._entries = []
        self._save()

    def _save(self) -> None:
        """Persist history to JSON file."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            data = [e.to_dict() for e in self._entries]
            self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as exc:
            raise HistoryError(f"Failed to save history: {exc}") from exc

    def _load(self) -> None:
        """Load history from JSON file."""
        try:
            if self._path.exists():
                raw = self._path.read_text(encoding="utf-8")
                data = json.loads(raw)
                self._entries = [HistoryEntry.from_dict(d) for d in data]
        except Exception:
            self._entries = []
