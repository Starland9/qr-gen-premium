"""Geo coordinate QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit

from domain.validators import GeoValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class GeoForm(BaseForm):
    """Form for geographic location QR codes."""

    def _setup_ui(self) -> None:
        self._lat = QLineEdit()
        self._lat.setPlaceholderText("37.7749")
        self._lat.textChanged.connect(self.data_changed)
        self._lon = QLineEdit()
        self._lon.setPlaceholderText("-122.4194")
        self._lon.textChanged.connect(self.data_changed)
        self._label_field = QLineEdit()
        self._label_field.setPlaceholderText("Optional label")
        self._label_field.textChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("Latitude"), self._lat)
        self._layout.addRow(QLabel("Longitude"), self._lon)
        self._layout.addRow(QLabel("Label"), self._label_field)

    def get_data(self) -> dict[str, str]:
        return {
            "latitude": self._lat.text(),
            "longitude": self._lon.text(),
            "label": self._label_field.text(),
        }

    def validate(self) -> ValidationResult:
        return GeoValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        lat = self._lat.text()
        lon = self._lon.text()
        label = self._label_field.text()
        base = f"geo:{lat},{lon}"
        if label:
            base += f"?q={lat},{lon}({label})"
        return base
