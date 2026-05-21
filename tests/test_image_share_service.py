"""Tests for image share service and image validator."""

from __future__ import annotations

import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from core.exceptions import ImageShareError
from domain.validators import ImageValidator
from services.image_share_service import ImageUploaderService, LocalImageServerService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a small valid PNG for testing."""
    img = Image.new("RGB", (32, 32), color=(255, 0, 0))
    path = tmp_path / "test.png"
    img.save(str(path), "PNG")
    return path


@pytest.fixture
def lan_server() -> LocalImageServerService:
    svc = LocalImageServerService()
    yield svc
    svc.stop()  # always clean up after each test


# ---------------------------------------------------------------------------
# ImageValidator
# ---------------------------------------------------------------------------


class TestImageValidator:
    def test_valid_png(self, sample_image: Path) -> None:
        result = ImageValidator().validate({"image_path": str(sample_image)})
        assert result.is_valid

    def test_empty_path(self) -> None:
        result = ImageValidator().validate({"image_path": ""})
        assert not result.is_valid
        assert "image_path" in result.errors

    def test_missing_file(self, tmp_path: Path) -> None:
        result = ImageValidator().validate({"image_path": str(tmp_path / "ghost.png")})
        assert not result.is_valid
        assert "image_path" in result.errors

    def test_unsupported_format(self, tmp_path: Path) -> None:
        p = tmp_path / "doc.pdf"
        p.write_bytes(b"%PDF-1.4 fake")
        result = ImageValidator().validate({"image_path": str(p)})
        assert not result.is_valid
        assert "image_path" in result.errors

    @pytest.mark.parametrize("ext", [".jpg", ".jpeg", ".bmp", ".webp", ".gif"])
    def test_accepted_extensions(self, tmp_path: Path, ext: str) -> None:
        p = tmp_path / f"img{ext}"
        p.write_bytes(b"fake image data")
        result = ImageValidator().validate({"image_path": str(p)})
        # File exists and has accepted ext — validator should pass
        assert result.is_valid


# ---------------------------------------------------------------------------
# LocalImageServerService
# ---------------------------------------------------------------------------


class TestLocalImageServerService:
    def test_start_returns_http_url(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        url = lan_server.start(sample_image)
        assert url.startswith("http://")
        assert url.endswith("/")

    def test_is_running_after_start(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        assert not lan_server.is_running
        lan_server.start(sample_image)
        assert lan_server.is_running

    def test_not_running_after_stop(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        lan_server.start(sample_image)
        lan_server.stop()
        assert not lan_server.is_running

    def test_current_url_matches_start(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        url = lan_server.start(sample_image)
        assert lan_server.current_url == url

    def test_current_url_cleared_after_stop(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        lan_server.start(sample_image)
        lan_server.stop()
        assert lan_server.current_url == ""

    def test_restart_replaces_server(
        self, lan_server: LocalImageServerService, sample_image: Path, tmp_path: Path
    ) -> None:
        img2 = Image.new("RGB", (16, 16), color=(0, 255, 0))
        path2 = tmp_path / "second.png"
        img2.save(str(path2), "PNG")

        url1 = lan_server.start(sample_image)
        url2 = lan_server.start(path2)
        assert url1 != url2  # different port each time

    def test_missing_file_raises(self, lan_server: LocalImageServerService) -> None:
        with pytest.raises(ImageShareError, match="not found"):
            lan_server.start("/nonexistent/image.png")

    def test_unsupported_format_raises(
        self, lan_server: LocalImageServerService, tmp_path: Path
    ) -> None:
        p = tmp_path / "doc.pdf"
        p.write_bytes(b"%PDF fake")
        with pytest.raises(ImageShareError, match="Unsupported"):
            lan_server.start(p)

    def test_server_serves_html_on_root(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        url = lan_server.start(sample_image)
        with urllib.request.urlopen(url, timeout=5) as resp:
            content = resp.read()
        assert b"<html" in content.lower()
        assert b"<img" in content.lower()

    def test_server_serves_image_bytes(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        url = lan_server.start(sample_image)
        image_url = url.rstrip("/") + "/image"
        with urllib.request.urlopen(image_url, timeout=5) as resp:
            data = resp.read()
        assert data == sample_image.read_bytes()

    def test_server_404_on_unknown_path(
        self, lan_server: LocalImageServerService, sample_image: Path
    ) -> None:
        import urllib.error

        url = lan_server.start(sample_image)
        bad_url = url.rstrip("/") + "/secret.txt"
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(bad_url, timeout=5)
        assert exc_info.value.code == 404

    def test_stop_is_idempotent(self, lan_server: LocalImageServerService) -> None:
        lan_server.stop()  # stop without ever starting — must not raise
        lan_server.stop()


# ---------------------------------------------------------------------------
# ImageUploaderService (mocked network)
# ---------------------------------------------------------------------------


class TestImageUploaderService:
    def test_upload_returns_url(self, sample_image: Path) -> None:
        fake_url = "https://0x0.st/Abc123.png"
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_url.encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            url = ImageUploaderService().upload(sample_image)

        assert url == fake_url

    def test_upload_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ImageShareError, match="not found"):
            ImageUploaderService().upload(tmp_path / "ghost.png")

    def test_upload_http_error_raises(self, sample_image: Path) -> None:
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError(
                "https://0x0.st", 413, "Request Entity Too Large", {}, None
            ),
        ):
            with pytest.raises(ImageShareError, match="Upload rejected"):
                ImageUploaderService().upload(sample_image)

    def test_upload_network_error_raises(self, sample_image: Path) -> None:
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("Network unreachable"),
        ):
            with pytest.raises(ImageShareError, match="Network error"):
                ImageUploaderService().upload(sample_image)

    def test_upload_unexpected_response_raises(self, sample_image: Path) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"error: rate limited"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(ImageShareError, match="Unexpected response"):
                ImageUploaderService().upload(sample_image)
