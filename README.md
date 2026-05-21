# QR Gen Premium

> **A production-ready, premium-quality QR code generator desktop application built with Python and PySide6.**

---

## ✨ Features

- **8 QR Code Types** — Text, URL, Email, Phone, SMS, vCard, WiFi, Geo coordinates
- **Live Preview** — Real-time QR generation as you type
- **Custom Styling** — Choose fill/background colors, error correction level, border size
- **Logo Overlay** — Embed any PNG/JPG/SVG logo into the QR center
- **Export Formats** — PNG, SVG, and JPEG export
- **Clipboard Support** — One-click copy to system clipboard
- **Generation History** — Last 20 QR codes saved locally
- **Premium Dark Theme** — Polished dark UI with purple accent, smooth animations
- **Cross-Platform** — Runs on Windows, macOS, and Linux

---

## 📋 Requirements

- Python 3.11+
- PySide6 >= 6.6.0
- qrcode[pil] >= 7.4.2
- Pillow >= 10.0.0

---

## 🚀 Installation

### From source

```bash
git clone https://github.com/your-org/qr-gen-premium.git
cd qr-gen-premium
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Development setup

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
ruff check .
```

---

## 🖥 Usage

1. **Select QR Type** — Click a type pill at the top of the left panel (Text, URL, Email, etc.)
2. **Fill the form** — Enter the relevant data in the form fields
3. **Customize** — Adjust size, colors, error correction, and optionally add a logo
4. **Preview** — The QR code updates live in the right panel
5. **Export** — Choose format (PNG/SVG/JPG), filename, output folder and click **Export**

---

## 🏗 Architecture

```
app/           Entry point
core/          Configuration and custom exceptions
domain/        Data models and input validators
services/      QR generation, export, and history business logic
ui/            Main window and theme management
widgets/       Reusable UI components and type-specific input forms
assets/        Icons and static assets
tests/         Pytest test suite
scripts/       Build helpers (PyInstaller)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run `ruff check .` and `pytest tests/ -v`
5. Open a pull request

---

## 📄 License

MIT License.
