"""Custom exceptions for QR Gen Premium."""


class QRGenError(Exception):
    """Base exception for all QR Gen errors."""


class ValidationError(QRGenError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class GenerationError(QRGenError):
    """Raised when QR code generation fails."""


class ExportError(QRGenError):
    """Raised when export fails."""


class HistoryError(QRGenError):
    """Raised when history operations fail."""


class DecodeError(QRGenError):
    """Raised when QR code decoding from an image fails."""


class ImageShareError(QRGenError):
    """Raised when image sharing (LAN server or online upload) fails."""
