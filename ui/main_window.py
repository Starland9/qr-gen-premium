"""Main application window."""

from __future__ import annotations

import base64

from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.config import APP_NAME, APP_VERSION, DEFAULT_BOX_SIZE, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from domain.models import ExportConfig, ExportFormat, HistoryEntry, QRConfig, QRType
from services.export_service import ExportService
from services.history_service import HistoryService
from services.qr_generator import QRGeneratorService
from ui.utils import pil_to_qimage
from widgets.customization_panel import CustomizationPanel
from widgets.export_panel import ExportPanel
from widgets.forms.email_form import EmailForm
from widgets.forms.geo_form import GeoForm
from widgets.forms.phone_form import PhoneForm
from widgets.forms.sms_form import SMSForm
from widgets.forms.text_form import TextForm
from widgets.forms.url_form import URLForm
from widgets.forms.vcard_form import VCardForm
from widgets.forms.wifi_form import WiFiForm
from widgets.notification_widget import NotificationWidget
from widgets.qr_preview_widget import QRPreviewWidget
from widgets.type_selector_widget import TypeSelectorWidget

_FORM_MAP = {
    QRType.TEXT: TextForm,
    QRType.URL: URLForm,
    QRType.EMAIL: EmailForm,
    QRType.PHONE: PhoneForm,
    QRType.SMS: SMSForm,
    QRType.VCARD: VCardForm,
    QRType.WIFI: WiFiForm,
    QRType.GEO: GeoForm,
}


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self) -> None:
        super().__init__()
        self._generator = QRGeneratorService()
        self._exporter = ExportService()
        self._history = HistoryService()
        self._current_type = QRType.TEXT
        self._forms: dict[QRType, object] = {}
        self._setup_window()
        self._build_ui()
        self._connect_signals()

    def _setup_window(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1100, 700)
        self.statusBar().showMessage(f"  {APP_NAME}  v{APP_VERSION}")

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # --- Left panel ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(16, 16, 12, 16)
        left_layout.setSpacing(12)

        # Title
        title = QLabel(APP_NAME)
        title.setObjectName("heading")
        left_layout.addWidget(title)

        # Type selector
        self._type_selector = TypeSelectorWidget()
        left_layout.addWidget(self._type_selector)

        # Form stack
        self._form_stack = QStackedWidget()
        for qr_type, FormClass in _FORM_MAP.items():
            form = FormClass()
            form.data_changed.connect(self._on_form_changed)
            self._forms[qr_type] = form
            self._form_stack.addWidget(form)

        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(self._form_stack)
        form_scroll.setFrameShape(form_scroll.frameShape().NoFrame)
        left_layout.addWidget(form_scroll, stretch=1)

        # Customization panel
        self._customization = CustomizationPanel()
        left_layout.addWidget(self._customization)

        splitter.addWidget(left_widget)
        splitter.setStretchFactor(0, 3)

        # --- Right panel ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 16, 16, 16)
        right_layout.setSpacing(12)

        self._preview = QRPreviewWidget()
        right_layout.addWidget(self._preview, stretch=1)

        self._export_panel = ExportPanel()
        self._export_panel.set_export_enabled(False)
        right_layout.addWidget(self._export_panel)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([620, 480])

        root_layout.addWidget(splitter)

        # Notification overlay
        self._notification = NotificationWidget(central)

    def _connect_signals(self) -> None:
        self._type_selector.type_changed.connect(self._on_type_changed)
        self._customization.customization_changed.connect(self._on_form_changed)
        self._export_panel.export_requested.connect(self._on_export)

    def _on_type_changed(self, qr_type: QRType) -> None:
        self._current_type = qr_type
        form = self._forms.get(qr_type)
        if form is not None:
            self._form_stack.setCurrentWidget(form)
        self._preview.update_badge(qr_type)
        self._on_form_changed()

    def _on_form_changed(self) -> None:
        self._on_generate()

    def _on_generate(self) -> None:
        form = self._forms.get(self._current_type)
        if form is None:
            return
        result = form.validate()  # type: ignore[union-attr]
        if not result.is_valid:
            self._preview.clear_preview()
            self._export_panel.set_export_enabled(False)
            return
        data = form.get_qr_data()  # type: ignore[union-attr]
        if not data.strip():
            self._preview.clear_preview()
            self._export_panel.set_export_enabled(False)
            return
        config = QRConfig(
            qr_type=self._current_type,
            data=data,
            size=self._customization.get_size(),
            box_size=DEFAULT_BOX_SIZE,
            border=self._customization.get_border(),
            fill_color=self._customization.get_fill_color(),
            back_color=self._customization.get_back_color(),
            error_correction=self._customization.get_error_correction(),
            logo_path=self._customization.get_logo_path(),
        )
        try:
            if config.logo_path:
                pil_image = self._generator.generate_with_logo(config)
            else:
                pil_image = self._generator.generate(config)
            qimage = pil_to_qimage(pil_image)
            self._preview.update_preview(qimage)
            self._export_panel.set_export_enabled(True)
            self._last_config = config
            self._last_pil_image = pil_image
            self._last_qimage = qimage
        except Exception as exc:
            self._preview.clear_preview()
            self._export_panel.set_export_enabled(False)
            self.statusBar().showMessage(f"  Generation error: {exc}")

    def _on_export(self, export_config: ExportConfig) -> None:
        if not hasattr(self, "_last_pil_image") or not hasattr(self, "_last_config"):
            self._show_notification("Generate a QR code first.", "error")
            return
        try:
            if export_config.format == ExportFormat.SVG:
                path = self._exporter.export_svg(self._last_config, export_config)
            else:
                path = self._exporter.export(self._last_pil_image, export_config)
            self._show_notification(f"Saved to {path.name}", "success")
            self._save_history()
        except Exception as exc:
            self._show_notification(f"Export failed: {exc}", "error")

    def _save_history(self) -> None:
        if not hasattr(self, "_last_config") or not hasattr(self, "_last_qimage"):
            return
        buf = QBuffer()
        buf.open(QIODevice.OpenMode.WriteOnly)
        self._last_qimage.save(buf, "PNG")
        thumb_b64 = base64.b64encode(buf.data().data()).decode()
        entry = HistoryEntry(
            qr_type=self._current_type,
            data_preview=self._last_config.data[:60],
            thumbnail_b64=thumb_b64,
        )
        self._history.add_entry(entry)

    def _show_notification(self, message: str, level: str = "success") -> None:
        self._notification.show_message(message, level)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if hasattr(self, "_notification"):
            parent_w = self.centralWidget().width() if self.centralWidget() else self.width()
            x = parent_w - self._notification.width() - 16
            self._notification.move(x, self._notification.y())
