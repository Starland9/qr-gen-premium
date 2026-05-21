"""Domain models for QR Gen Premium."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QRType(Enum):
    """Supported QR code content types."""

    TEXT = "Text"
    URL = "URL"
    EMAIL = "Email"
    PHONE = "Phone"
    SMS = "SMS"
    VCARD = "vCard"
    WIFI = "WiFi"
    GEO = "Geo"


class ErrorCorrectionLevel(Enum):
    """QR code error correction levels."""

    L = "L (~7%)"
    M = "M (~15%)"
    Q = "Q (~25%)"
    H = "H (~30%)"


class ExportFormat(Enum):
    """Supported export formats."""

    PNG = "PNG"
    SVG = "SVG"
    JPG = "JPG"


@dataclass
class QRConfig:
    """Configuration for QR code generation."""

    qr_type: QRType = QRType.TEXT
    data: str = ""
    size: int = 300
    box_size: int = 10
    border: int = 4
    fill_color: str = "#000000"
    back_color: str = "#FFFFFF"
    error_correction: ErrorCorrectionLevel = ErrorCorrectionLevel.M
    logo_path: str | None = None


@dataclass
class ExportConfig:
    """Configuration for exporting QR codes."""

    format: ExportFormat = ExportFormat.PNG
    output_dir: str = "."
    filename: str = "qrcode"
    scale: float = 1.0


@dataclass
class HistoryEntry:
    """A single history entry for a generated QR code."""

    qr_type: QRType
    data_preview: str
    created_at: datetime = field(default_factory=datetime.now)
    thumbnail_b64: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            "id": self.id,
            "qr_type": self.qr_type.name,
            "data_preview": self.data_preview,
            "created_at": self.created_at.isoformat(),
            "thumbnail_b64": self.thumbnail_b64,
        }

    @classmethod
    def from_dict(cls, data: dict) -> HistoryEntry:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            qr_type=QRType[data["qr_type"]],
            data_preview=data["data_preview"],
            created_at=datetime.fromisoformat(data["created_at"]),
            thumbnail_b64=data.get("thumbnail_b64", ""),
        )
