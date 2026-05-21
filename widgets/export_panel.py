"""Export panel widget."""

from __future__ import annotations

import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from domain.models import ExportConfig, ExportFormat


class ExportPanel(QWidget):
    """Panel for configuring and triggering QR code export."""

    export_requested = Signal(object)  # emits ExportConfig

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected_format = ExportFormat.PNG
        self._format_buttons: dict[ExportFormat, QPushButton] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Format selector
        fmt_group = QGroupBox("Export Format")
        fmt_layout = QHBoxLayout(fmt_group)
        for fmt in ExportFormat:
            btn = QPushButton(fmt.value)
            btn.setObjectName("segmentButton")
            btn.clicked.connect(lambda checked, f=fmt: self._select_format(f))
            self._format_buttons[fmt] = btn
            fmt_layout.addWidget(btn)
        fmt_layout.addStretch()
        layout.addWidget(fmt_group)
        self._select_format(ExportFormat.PNG)

        # Filename
        file_group = QGroupBox("File Settings")
        file_layout = QVBoxLayout(file_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Filename:"))
        self._filename_input = QLineEdit("qrcode")
        name_row.addWidget(self._filename_input)
        file_layout.addLayout(name_row)

        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Folder:"))
        self._dir_input = QLineEdit(os.path.expanduser("~/Desktop"))
        dir_row.addWidget(self._dir_input)
        browse_btn = QPushButton("…")
        browse_btn.setFixedWidth(32)
        browse_btn.clicked.connect(self._browse_folder)
        dir_row.addWidget(browse_btn)
        file_layout.addLayout(dir_row)

        open_btn = QPushButton("📂  Open Folder")
        open_btn.clicked.connect(self._open_folder)
        file_layout.addWidget(open_btn)

        layout.addWidget(file_group)

        # Export button
        self._export_btn = QPushButton("⬇  Export QR Code")
        self._export_btn.setObjectName("accentButton")
        self._export_btn.clicked.connect(self._on_export)
        layout.addWidget(self._export_btn)
        layout.addStretch()

    def _select_format(self, fmt: ExportFormat) -> None:
        self._selected_format = fmt
        for f, btn in self._format_buttons.items():
            btn.setProperty("selected", f == fmt)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _browse_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self._dir_input.setText(path)

    def _open_folder(self) -> None:
        import subprocess
        import sys
        folder = self._dir_input.text()
        if os.path.isdir(folder):
            if sys.platform == "win32":
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])

    def _on_export(self) -> None:
        config = ExportConfig(
            format=self._selected_format,
            output_dir=self._dir_input.text() or os.path.expanduser("~/Desktop"),
            filename=self._filename_input.text() or "qrcode",
        )
        self.export_requested.emit(config)

    def set_export_enabled(self, enabled: bool) -> None:
        """Enable or disable the export button."""
        self._export_btn.setEnabled(enabled)
