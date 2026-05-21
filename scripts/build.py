#!/usr/bin/env python3
"""PyInstaller build helper for QR Gen Premium."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENTRY = ROOT / "app" / "main.py"
DIST = ROOT / "dist"
ICON_SVG = ROOT / "assets" / "icons" / "app_icon.svg"

APP_NAME = "QR Gen Premium"


def get_icon_flag() -> list[str]:
    """Return the appropriate --icon flag for the current platform."""
    system = platform.system()
    if system == "Windows":
        ico = ROOT / "assets" / "icons" / "app_icon.ico"
        if ico.exists():
            return ["--icon", str(ico)]
    elif system == "Darwin":
        icns = ROOT / "assets" / "icons" / "app_icon.icns"
        if icns.exists():
            return ["--icon", str(icns)]
    return []


def build() -> int:
    """Run PyInstaller with platform-appropriate settings."""
    system = platform.system()
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(ENTRY),
        "--name", APP_NAME.replace(" ", "-"),
        "--onefile",
        "--windowed",
        "--distpath", str(DIST),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT),
        "--add-data", f"{ROOT / 'assets'}{os.pathsep}assets",
        "--noconfirm",
    ]
    cmd.extend(get_icon_flag())
    if system == "Darwin":
        cmd += ["--target-architecture", "universal2"]
    print(f"Building for {system}...")
    print("Command:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
