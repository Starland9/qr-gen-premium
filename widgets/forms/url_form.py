"""URL QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit

from domain.validators import URLValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class URLForm(BaseForm):
    """Form for URL QR codes."""

    def _setup_ui(self) -> None:
        self._url = QLineEdit()
        self._url.setPlaceholderText("https://example.com")
        self._url.textChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("URL"), self._url)

    def get_data(self) -> dict[str, str]:
        return {"url": self._url.text()}

    def validate(self) -> ValidationResult:
        return URLValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        return self._url.text()
