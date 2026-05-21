"""Phone QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit

from domain.validators import PhoneValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class PhoneForm(BaseForm):
    """Form for phone number QR codes."""

    def _setup_ui(self) -> None:
        self._phone = QLineEdit()
        self._phone.setPlaceholderText("+1 555 123 4567")
        self._phone.textChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("Phone"), self._phone)

    def get_data(self) -> dict[str, str]:
        return {"phone": self._phone.text()}

    def validate(self) -> ValidationResult:
        return PhoneValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        return f"tel:{self._phone.text()}"
