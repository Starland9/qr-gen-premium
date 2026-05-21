"""Email QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit

from domain.validators import EmailValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class EmailForm(BaseForm):
    """Form for email QR codes."""

    def _setup_ui(self) -> None:
        self._email = QLineEdit()
        self._email.setPlaceholderText("user@example.com")
        self._email.textChanged.connect(self.data_changed)
        self._subject = QLineEdit()
        self._subject.setPlaceholderText("Optional subject")
        self._subject.textChanged.connect(self.data_changed)
        self._body = QLineEdit()
        self._body.setPlaceholderText("Optional body")
        self._body.textChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("Email"), self._email)
        self._layout.addRow(QLabel("Subject"), self._subject)
        self._layout.addRow(QLabel("Body"), self._body)

    def get_data(self) -> dict[str, str]:
        return {
            "email": self._email.text(),
            "subject": self._subject.text(),
            "body": self._body.text(),
        }

    def validate(self) -> ValidationResult:
        return EmailValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        email = self._email.text()
        subject = self._subject.text()
        body = self._body.text()
        params: list[str] = []
        if subject:
            params.append(f"subject={subject}")
        if body:
            params.append(f"body={body}")
        suffix = "?" + "&".join(params) if params else ""
        return f"mailto:{email}{suffix}"
