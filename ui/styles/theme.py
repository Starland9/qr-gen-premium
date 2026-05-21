"""Theme management for QR Gen Premium."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

DARK_QSS = """
/* === Base === */
QMainWindow, QDialog {
    background-color: #0F1117;
}
QWidget {
    background-color: #0F1117;
    color: #F0F0F5;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
    selection-background-color: #6C63FF;
    selection-color: #F0F0F5;
}
QWidget#centralWidget {
    background-color: #0F1117;
}

/* === Panels / Cards === */
QFrame#card {
    background-color: #1A1D27;
    border: 1px solid #2A2D3E;
    border-radius: 6px;
    padding: 8px;
}
QFrame {
    border: none;
}
QGroupBox {
    background-color: #1A1D27;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    margin-top: 10px;
    padding: 8px 10px;
    font-weight: 600;
    color: #8B8FA8;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    left: 8px;
    top: -6px;
    color: #8B8FA8;
}

/* === Buttons === */
QPushButton {
    background-color: #1A1D27;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
    min-height: 24px;
    outline: none;
}
QPushButton:hover {
    background-color: #22263A;
    border-color: #6C63FF;
    color: #F0F0F5;
}
QPushButton:pressed {
    background-color: #2A2E45;
    border-color: #6C63FF;
}
QPushButton:disabled {
    background-color: #14161F;
    color: #3C3F52;
    border-color: #1E2030;
}
QPushButton#accentButton {
    background-color: #6C63FF;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 600;
    min-height: 28px;
}
QPushButton#accentButton:hover {
    background-color: #7C74FF;
}
QPushButton#accentButton:pressed {
    background-color: #5A52E0;
}
QPushButton#accentButton:disabled {
    background-color: #3A375A;
    color: #7070A0;
}
QPushButton#pillButton {
    background-color: transparent;
    color: #8B8FA8;
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 500;
    min-height: 24px;
}
QPushButton#pillButton:hover {
    background-color: #22263A;
    color: #F0F0F5;
    border-color: #2A2D3E;
}
QPushButton#pillButton[selected="true"] {
    background-color: #6C63FF;
    color: #FFFFFF;
    border-color: #6C63FF;
}
QPushButton#segmentButton {
    background-color: #1A1D27;
    color: #8B8FA8;
    border: 1px solid #2A2D3E;
    border-radius: 0px;
    padding: 4px 10px;
    font-size: 11px;
    min-height: 24px;
}
QPushButton#segmentButton:first-child {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
}
QPushButton#segmentButton:last-child {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QPushButton#segmentButton[selected="true"] {
    background-color: #6C63FF;
    color: #FFFFFF;
    border-color: #6C63FF;
}
QPushButton#segmentButton:hover:!pressed {
    background-color: #22263A;
    color: #F0F0F5;
}
QPushButton#iconButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px;
    min-width: 24px;
    min-height: 24px;
    max-width: 24px;
    max-height: 24px;
}
QPushButton#iconButton:hover {
    background-color: #22263A;
}

/* === Inputs === */
QLineEdit {
    background-color: #1A1D27;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 24px;
    selection-background-color: #6C63FF;
}
QLineEdit:focus {
    border-color: #6C63FF;
    background-color: #1E2230;
}
QLineEdit:disabled {
    background-color: #14161F;
    color: #3C3F52;
    border-color: #1E2030;
}
QLineEdit[error="true"] {
    border-color: #FF5B5B;
}
QTextEdit {
    background-color: #1A1D27;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: #6C63FF;
}
QTextEdit:focus {
    border-color: #6C63FF;
    background-color: #1E2230;
}

/* === ComboBox === */
QComboBox {
    background-color: #1A1D27;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    min-height: 24px;
    min-width: 90px;
}
QComboBox:hover {
    border-color: #6C63FF;
}
QComboBox:focus {
    border-color: #6C63FF;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 20px;
    border-left: 1px solid #2A2D3E;
    border-radius: 0 4px 4px 0;
    background: transparent;
}
QComboBox::down-arrow {
    width: 8px;
    height: 8px;
    image: none;
    border-left: 2px solid #8B8FA8;
    border-bottom: 2px solid #8B8FA8;
    transform: rotate(-45deg);
    margin-right: 4px;
}
QComboBox QAbstractItemView {
    background-color: #1A1D27;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    selection-background-color: #6C63FF;
    selection-color: #FFFFFF;
    outline: none;
    padding: 2px;
}
QComboBox QAbstractItemView::item {
    padding: 4px 10px;
    border-radius: 4px;
    min-height: 22px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #22263A;
}

/* === SpinBox === */
QSpinBox, QDoubleSpinBox {
    background-color: #1A1D27;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    min-height: 24px;
    min-width: 60px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #6C63FF;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #22263A;
    border: none;
    width: 16px;
    border-radius: 2px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #6C63FF;
}

/* === Slider === */
QSlider::groove:horizontal {
    height: 3px;
    background-color: #2A2D3E;
    border-radius: 1px;
}
QSlider::handle:horizontal {
    background-color: #6C63FF;
    border: none;
    width: 12px;
    height: 12px;
    border-radius: 6px;
    margin: -4px 0;
}
QSlider::handle:horizontal:hover {
    background-color: #7C74FF;
    width: 14px;
    height: 14px;
    border-radius: 7px;
    margin: -5px 0;
}
QSlider::sub-page:horizontal {
    background-color: #6C63FF;
    border-radius: 1px;
}

/* === CheckBox === */
QCheckBox {
    color: #F0F0F5;
    font-size: 12px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #2A2D3E;
    background-color: #1A1D27;
}
QCheckBox::indicator:hover {
    border-color: #6C63FF;
}
QCheckBox::indicator:checked {
    background-color: #6C63FF;
    border-color: #6C63FF;
    image: none;
}
QCheckBox::indicator:checked:hover {
    background-color: #7C74FF;
}

/* === Labels === */
QLabel {
    color: #F0F0F5;
    background: transparent;
    font-size: 12px;
}
QLabel#secondary {
    color: #8B8FA8;
    font-size: 11px;
}
QLabel#badge {
    background-color: #6C63FF;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}
QLabel#errorLabel {
    color: #FF5B5B;
    font-size: 10px;
}
QLabel#successLabel {
    color: #4CAF82;
    font-size: 10px;
}
QLabel#heading {
    font-size: 15px;
    font-weight: 700;
    color: #F0F0F5;
}
QLabel#subheading {
    font-size: 13px;
    font-weight: 600;
    color: #F0F0F5;
}

/* === ScrollArea === */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: #0F1117;
    width: 6px;
    border-radius: 3px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #2A2D3E;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #6C63FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #0F1117;
    height: 6px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background-color: #2A2D3E;
    border-radius: 3px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #6C63FF;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #2A2D3E;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #1A1D27;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: transparent;
    color: #8B8FA8;
    border: none;
    padding: 6px 16px;
    font-size: 12px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #6C63FF;
    border-bottom: 2px solid #6C63FF;
}
QTabBar::tab:hover:!selected {
    color: #F0F0F5;
}

/* === StatusBar === */
QStatusBar {
    background-color: #0A0C13;
    color: #8B8FA8;
    font-size: 10px;
    border-top: 1px solid #1E2030;
}
QStatusBar::item {
    border: none;
}

/* === ToolTip === */
QToolTip {
    background-color: #22263A;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
}

/* === Mode Toggle Bar === */
QWidget#modeToggleBar {
    background-color: #0A0C13;
    border-bottom: 1px solid #1E2030;
}
QPushButton#modeButton {
    background-color: transparent;
    color: #8B8FA8;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
    min-height: 24px;
}
QPushButton#modeButton:hover {
    background-color: #22263A;
    color: #F0F0F5;
}
QPushButton#modeButton[active="true"] {
    background-color: #6C63FF;
    color: #FFFFFF;
    border-color: #6C63FF;
}
QPushButton#modeButton[active="true"]:hover {
    background-color: #7C74FF;
}

/* === Secondary Button === */
QPushButton#secondaryButton {
    background-color: transparent;
    color: #8B8FA8;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    min-height: 24px;
}
QPushButton#secondaryButton:hover {
    background-color: #22263A;
    color: #F0F0F5;
    border-color: #6C63FF;
}

/* === Drop Zone === */
QFrame#dropZone {
    background-color: #141620;
    border: 2px dashed #2A2D3E;
    border-radius: 6px;
}
QFrame#dropZone:hover {
    border-color: #6C63FF;
    background-color: #1A1D2E;
}
QFrame#dropZone[dragActive="true"] {
    border-color: #6C63FF;
    background-color: #1E2040;
}

/* === Scan Panel Labels === */
QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #F0F0F5;
}
QLabel#subtitle {
    font-size: 11px;
    color: #8B8FA8;
}
QLabel#decodedText {
    background-color: #0F1117;
    color: #F0F0F5;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
    padding: 4px 6px;
    font-size: 11px;
    font-family: "Consolas", "Fira Mono", monospace;
}
"""


class ThemeManager:
    """Manages application-wide theming."""

    @staticmethod
    def apply_dark(app: QApplication) -> None:
        """Apply the dark premium theme to the application."""
        app.setStyleSheet(DARK_QSS)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0F1117"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#F0F0F5"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#1A1D27"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#22263A"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#22263A"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#F0F0F5"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#F0F0F5"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#1A1D27"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F0F0F5"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#6C63FF"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#6C63FF"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#3C3F52")
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#3C3F52")
        )
        app.setPalette(palette)
