"""Plain text QR form."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTextEdit

from domain.validators import TextValidator, ValidationResult
from widgets.forms.base_form import BaseForm


class TextForm(BaseForm):
    """Form for plain text QR codes."""

    def _setup_ui(self) -> None:
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("Enter any text...")
        self._text_edit.setMaximumHeight(120)
        self._text_edit.textChanged.connect(self.data_changed)
        self._layout.addRow(QLabel("Text"), self._text_edit)

    def get_data(self) -> dict[str, str]:
        return {"text": self._text_edit.toPlainText()}

    def validate(self) -> ValidationResult:
        return TextValidator().validate(self.get_data())

    def get_qr_data(self) -> str:
        return self._text_edit.toPlainText()

    def set_text(self, text: str) -> None:
        """Programmatically set the text content."""
        self._text_edit.setPlainText(text)
