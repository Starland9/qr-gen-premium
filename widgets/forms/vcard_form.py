"""vCard QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit

from domain.validators import VCardValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class VCardForm(BaseForm):
    """Form for vCard QR codes."""

    def _setup_ui(self) -> None:
        self._first = QLineEdit()
        self._first.setPlaceholderText("John")
        self._first.textChanged.connect(self.data_changed)
        self._last = QLineEdit()
        self._last.setPlaceholderText("Doe")
        self._last.textChanged.connect(self.data_changed)
        self._org = QLineEdit()
        self._org.setPlaceholderText("Acme Corp")
        self._org.textChanged.connect(self.data_changed)
        self._phone = QLineEdit()
        self._phone.setPlaceholderText("+1 555 000 0000")
        self._phone.textChanged.connect(self.data_changed)
        self._email = QLineEdit()
        self._email.setPlaceholderText("john@example.com")
        self._email.textChanged.connect(self.data_changed)
        self._website = QLineEdit()
        self._website.setPlaceholderText("https://example.com")
        self._website.textChanged.connect(self.data_changed)
        self._address = QLineEdit()
        self._address.setPlaceholderText("123 Main St, City, State")
        self._address.textChanged.connect(self.data_changed)
        for label, widget in [
            ("First Name", self._first),
            ("Last Name", self._last),
            ("Organization", self._org),
            ("Phone", self._phone),
            ("Email", self._email),
            ("Website", self._website),
            ("Address", self._address),
        ]:
            self._layout.addRow(QLabel(label), widget)

    def get_data(self) -> dict[str, str]:
        return {
            "first_name": self._first.text(),
            "last_name": self._last.text(),
            "org": self._org.text(),
            "phone": self._phone.text(),
            "email": self._email.text(),
            "website": self._website.text(),
            "address": self._address.text(),
        }

    def validate(self) -> ValidationResult:
        return VCardValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        d = self.get_data()
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{d['last_name']};{d['first_name']}",
            f"FN:{d['first_name']} {d['last_name']}".strip(),
        ]
        if d["org"]:
            lines.append(f"ORG:{d['org']}")
        if d["phone"]:
            lines.append(f"TEL:{d['phone']}")
        if d["email"]:
            lines.append(f"EMAIL:{d['email']}")
        if d["website"]:
            lines.append(f"URL:{d['website']}")
        if d["address"]:
            lines.append(f"ADR:;;{d['address']};;;;")
        lines.append("END:VCARD")
        return "\n".join(lines)
