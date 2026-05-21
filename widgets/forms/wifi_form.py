"""WiFi QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit

from domain.validators import WiFiValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class WiFiForm(BaseForm):
    """Form for WiFi network QR codes."""

    def _setup_ui(self) -> None:
        self._ssid = QLineEdit()
        self._ssid.setPlaceholderText("Network name")
        self._ssid.textChanged.connect(self.data_changed)
        self._security = QComboBox()
        self._security.addItems(["WPA", "WEP", "nopass"])
        self._security.currentTextChanged.connect(self.data_changed)
        self._password = QLineEdit()
        self._password.setPlaceholderText("Network password")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.textChanged.connect(self.data_changed)
        self._hidden = QCheckBox("Hidden network")
        self._hidden.stateChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("SSID"), self._ssid)
        self._layout.addRow(QLabel("Security"), self._security)
        self._layout.addRow(QLabel("Password"), self._password)
        self._layout.addRow(QLabel(""), self._hidden)

    def get_data(self) -> dict[str, str]:
        return {
            "ssid": self._ssid.text(),
            "security": self._security.currentText(),
            "password": self._password.text(),
            "hidden": "true" if self._hidden.isChecked() else "false",
        }

    def validate(self) -> ValidationResult:
        return WiFiValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        d = self.get_data()
        return (
            f"WIFI:T:{d['security']};S:{d['ssid']};"
            f"P:{d['password']};H:{d['hidden']};;"
        )
