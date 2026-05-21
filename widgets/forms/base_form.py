"""Abstract base class for QR code data input forms."""

from __future__ import annotations

from abc import abstractmethod

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget

from domain.validators import ValidationResult


class BaseForm(QWidget):
    """Abstract base form for QR data input."""

    data_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QFormLayout(self)
        self._layout.setSpacing(10)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self._setup_ui()

    @abstractmethod
    def _setup_ui(self) -> None:
        """Set up the form's UI elements."""

    @abstractmethod
    def get_data(self) -> dict[str, str]:
        """Return the current form data as a dictionary."""

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the current form data."""

    def get_qr_data(self) -> str:
        """Return raw data string for QR encoding (override per type)."""
        data = self.get_data()
        return next(iter(data.values()), "") if data else ""

    def _create_field(self, label: str, placeholder: str = "") -> tuple[QLabel, QLineEdit]:
        """Helper to create a labeled input field."""
        lbl = QLabel(label)
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.textChanged.connect(self.data_changed)
        return lbl, field

    def _add_row(self, label: str, widget: QWidget, placeholder: str = "") -> QLineEdit | None:
        """Add a row to the form layout. Returns QLineEdit if created."""
        if isinstance(widget, QLineEdit):
            widget.setPlaceholderText(placeholder)
            widget.textChanged.connect(self.data_changed)
        lbl = QLabel(label)
        self._layout.addRow(lbl, widget)
        return widget if isinstance(widget, QLineEdit) else None
