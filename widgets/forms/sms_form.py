"""SMS QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit, QTextEdit

from domain.validators import SMSValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class SMSForm(BaseForm):
    """Form for SMS QR codes."""

    def _setup_ui(self) -> None:
        self._phone = QLineEdit()
        self._phone.setPlaceholderText("+1 555 123 4567")
        self._phone.textChanged.connect(self.data_changed)
        self._message = QTextEdit()
        self._message.setPlaceholderText("Your message text")
        self._message.setMaximumHeight(100)
        self._message.textChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("Phone"), self._phone)
        self._layout.addRow(QLabel("Message"), self._message)

    def get_data(self) -> dict[str, str]:
        return {
            "phone": self._phone.text(),
            "message": self._message.toPlainText(),
        }

    def validate(self) -> ValidationResult:
        return SMSValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        phone = self._phone.text()
        message = self._message.toPlainText()
        return f"SMSTO:{phone}:{message}"
