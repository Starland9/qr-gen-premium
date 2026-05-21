"""Customization panel for QR code appearance settings."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.config import DEFAULT_BACK_COLOR, DEFAULT_BORDER, DEFAULT_BOX_SIZE, DEFAULT_FILL_COLOR, DEFAULT_QR_SIZE
from domain.models import ErrorCorrectionLevel


class CustomizationPanel(QWidget):
    """Panel for customizing QR code appearance."""

    customization_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fill_color = DEFAULT_FILL_COLOR
        self._back_color = DEFAULT_BACK_COLOR
        self._logo_path: str | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.frameShape().NoFrame)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        # Size
        size_group = QGroupBox("Size")
        size_layout = QVBoxLayout(size_group)
        size_row = QHBoxLayout()
        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(100, 1000)
        self._size_slider.setValue(DEFAULT_QR_SIZE)
        self._size_slider.valueChanged.connect(self._emit_changed)
        self._size_label = QLabel(f"{DEFAULT_QR_SIZE}px")
        self._size_label.setObjectName("secondary")
        self._size_label.setFixedWidth(50)
        self._size_slider.valueChanged.connect(
            lambda v: self._size_label.setText(f"{v}px")
        )
        size_row.addWidget(self._size_slider)
        size_row.addWidget(self._size_label)
        size_layout.addLayout(size_row)
        layout.addWidget(size_group)

        # Margin
        margin_group = QGroupBox("Border / Margin")
        margin_layout = QHBoxLayout(margin_group)
        margin_layout.addWidget(QLabel("Border cells:"))
        self._border_spin = QSpinBox()
        self._border_spin.setRange(0, 20)
        self._border_spin.setValue(DEFAULT_BORDER)
        self._border_spin.valueChanged.connect(self._emit_changed)
        margin_layout.addWidget(self._border_spin)
        margin_layout.addStretch()
        layout.addWidget(margin_group)

        # Colors
        color_group = QGroupBox("Colors")
        color_layout = QHBoxLayout(color_group)
        self._fill_btn = QPushButton("● Foreground")
        self._fill_btn.setToolTip("QR code dot color")
        self._fill_btn.clicked.connect(self._pick_fill_color)
        self._back_btn = QPushButton("○ Background")
        self._back_btn.setToolTip("QR code background color")
        self._back_btn.clicked.connect(self._pick_back_color)
        self._update_color_btn(self._fill_btn, self._fill_color)
        self._update_color_btn(self._back_btn, self._back_color)
        color_layout.addWidget(self._fill_btn)
        color_layout.addWidget(self._back_btn)
        layout.addWidget(color_group)

        # Error correction
        ec_group = QGroupBox("Error Correction")
        ec_layout = QHBoxLayout(ec_group)
        self._ec_combo = QComboBox()
        for ec in ErrorCorrectionLevel:
            self._ec_combo.addItem(ec.value, ec)
        self._ec_combo.setCurrentIndex(1)  # M
        self._ec_combo.currentIndexChanged.connect(self._emit_changed)
        ec_layout.addWidget(self._ec_combo)
        ec_layout.addStretch()
        layout.addWidget(ec_group)

        # Logo
        logo_group = QGroupBox("Logo Overlay")
        logo_layout = QVBoxLayout(logo_group)
        logo_row = QHBoxLayout()
        self._logo_btn = QPushButton("Browse…")
        self._logo_btn.clicked.connect(self._pick_logo)
        self._logo_clear_btn = QPushButton("Clear")
        self._logo_clear_btn.clicked.connect(self._clear_logo)
        self._logo_label = QLabel("No logo selected")
        self._logo_label.setObjectName("secondary")
        logo_row.addWidget(self._logo_btn)
        logo_row.addWidget(self._logo_clear_btn)
        logo_layout.addLayout(logo_row)
        logo_layout.addWidget(self._logo_label)
        layout.addWidget(logo_group)

        # Reset
        reset_btn = QPushButton("↺  Reset Defaults")
        reset_btn.clicked.connect(self._reset)
        layout.addWidget(reset_btn)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _emit_changed(self) -> None:
        self.customization_changed.emit()

    def _pick_fill_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._fill_color), self, "Foreground Color")
        if color.isValid():
            self._fill_color = color.name()
            self._update_color_btn(self._fill_btn, self._fill_color)
            self._emit_changed()

    def _pick_back_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._back_color), self, "Background Color")
        if color.isValid():
            self._back_color = color.name()
            self._update_color_btn(self._back_btn, self._back_color)
            self._emit_changed()

    def _update_color_btn(self, btn: QPushButton, color: str) -> None:
        btn.setStyleSheet(
            f"background-color: {color}; "
            f"color: {'#000000' if QColor(color).lightness() > 128 else '#FFFFFF'};"
            "border-radius: 8px; padding: 6px 14px;"
        )

    def _pick_logo(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg *.jpeg *.svg)"
        )
        if path:
            self._logo_path = path
            import os
            self._logo_label.setText(os.path.basename(path))
            self._emit_changed()

    def _clear_logo(self) -> None:
        self._logo_path = None
        self._logo_label.setText("No logo selected")
        self._emit_changed()

    def _reset(self) -> None:
        self._size_slider.setValue(DEFAULT_QR_SIZE)
        self._border_spin.setValue(DEFAULT_BORDER)
        self._fill_color = DEFAULT_FILL_COLOR
        self._back_color = DEFAULT_BACK_COLOR
        self._update_color_btn(self._fill_btn, self._fill_color)
        self._update_color_btn(self._back_btn, self._back_color)
        self._ec_combo.setCurrentIndex(1)
        self._clear_logo()
        self._emit_changed()

    def get_size(self) -> int:
        return self._size_slider.value()

    def get_border(self) -> int:
        return self._border_spin.value()

    def get_fill_color(self) -> str:
        return self._fill_color

    def get_back_color(self) -> str:
        return self._back_color

    def get_error_correction(self) -> ErrorCorrectionLevel:
        return self._ec_combo.currentData()

    def get_logo_path(self) -> str | None:
        return self._logo_path
