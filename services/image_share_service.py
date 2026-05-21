"""Image sharing service.

Provides two strategies for turning a local image file into a public URL that
can be encoded as a QR code:

* :class:`LocalImageServerService` — zero-config LAN server using Python's
  built-in ``http.server``.  Works instantly on the same WiFi network; the
  app must remain open for the URL to stay alive.

* :class:`ImageUploaderService` — uploads the image anonymously to a free
  public hosting endpoint (``0x0.st``) using Python's stdlib ``urllib``.
  The URL is permanent and works globally, but the image is publicly
  accessible.

Both services have *no* Qt dependency and return a plain URL string.
"""

from __future__ import annotations

import mimetypes
import socket
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from core.exceptions import ImageShareError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}


def _get_lan_ip() -> str:
    """Return the machine's LAN IP address, or 127.0.0.1 as a fallback."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _find_free_port() -> int:
    """Bind to port 0 to let the OS assign a free port, then return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _make_handler(image_path: Path, content_type: str) -> type[BaseHTTPRequestHandler]:
    """Return a request-handler class that serves *image_path* at any path."""

    _HTML = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{image_path.name}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #0f1117;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      font-family: system-ui, sans-serif;
      color: #f0f0f5;
    }}
    img {{
      max-width: 100%;
      max-height: 90vh;
      object-fit: contain;
      border-radius: 8px;
      box-shadow: 0 4px 32px rgba(0,0,0,.6);
    }}
    p {{ margin-top: 12px; font-size: 13px; color: #8b8fa8; }}
  </style>
</head>
<body>
  <img src="/image" alt="{image_path.name}">
  <p>{image_path.name}</p>
</body>
</html>"""
    _HTML_BYTES = _HTML.encode()

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path in ("/", ""):
                self._send(_HTML_BYTES, "text/html; charset=utf-8")
            elif self.path == "/image":
                try:
                    data = image_path.read_bytes()
                except OSError:
                    self.send_error(404)
                    return
                self._send(data, content_type)
            else:
                self.send_error(404)

        def _send(self, data: bytes, ctype: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt: str, *args: object) -> None:  # noqa: ARG002
            pass  # suppress request logging to stdout

    return _Handler


# ---------------------------------------------------------------------------
# Local LAN server
# ---------------------------------------------------------------------------


class LocalImageServerService:
    """Serve a single image file over HTTP on the local network.

    Usage::

        svc = LocalImageServerService()
        url = svc.start("/path/to/photo.jpg")
        # url → "http://192.168.1.5:49823/"  (encode this as QR)
        svc.stop()          # stop when done
    """

    def __init__(self) -> None:
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._current_url: str = ""

    @property
    def is_running(self) -> bool:
        """True if the server is currently serving a file."""
        return self._server is not None

    @property
    def current_url(self) -> str:
        """The URL that was returned by the last successful :meth:`start` call."""
        return self._current_url

    def start(self, image_path: str | Path) -> str:
        """Start (or restart) the server to serve *image_path*.

        Args:
            image_path: Path to the image file to serve.

        Returns:
            The LAN URL (e.g. ``http://192.168.1.5:49823/``) to encode as QR.

        Raises:
            ImageShareError: If the file is missing, the format is unsupported,
                             or the server cannot bind to a port.
        """
        path = Path(image_path)
        if not path.exists():
            raise ImageShareError(f"Image file not found: {path}")
        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise ImageShareError(
                f"Unsupported image format '{path.suffix}'. "
                f"Accepted: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}."
            )

        self.stop()  # stop any previous server before starting a new one

        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        handler_cls = _make_handler(path, content_type)

        lan_ip = _get_lan_ip()
        try:
            port = _find_free_port()
            # Bind to the LAN interface only (not 0.0.0.0) to limit exposure
            server = HTTPServer((lan_ip, port), handler_cls)
        except OSError as exc:
            raise ImageShareError(f"Could not start server: {exc}") from exc

        self._server = server
        self._thread = threading.Thread(
            target=server.serve_forever, name="ImageServer", daemon=True
        )
        self._thread.start()

        self._current_url = f"http://{lan_ip}:{port}/"
        return self._current_url

    def stop(self) -> None:
        """Shut down the HTTP server if it is running."""
        if self._server is not None:
            self._server.shutdown()
            self._server = None
            self._thread = None
            self._current_url = ""


# ---------------------------------------------------------------------------
# Anonymous online upload
# ---------------------------------------------------------------------------


class ImageUploaderService:
    """Upload an image to a free anonymous hosting service and return its URL.

    The default endpoint is `0x0.st <https://0x0.st>`_ which accepts HTTP
    multipart POST uploads and returns a plain-text URL.  The upload is
    permanent and publicly accessible — only use for images the user is
    comfortable sharing publicly.

    No third-party libraries are required (uses Python's stdlib ``urllib``).
    """

    _ENDPOINT = "https://0x0.st"

    def upload(self, image_path: str | Path) -> str:
        """Upload *image_path* and return the hosted URL.

        Args:
            image_path: Path to the image file to upload.

        Returns:
            The public URL of the uploaded image.

        Raises:
            ImageShareError: If the file is missing, the upload fails, or the
                             server returns an unexpected response.
        """
        path = Path(image_path)
        if not path.exists():
            raise ImageShareError(f"Image file not found: {path}")

        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

        try:
            url = self._post_multipart(path, content_type)
        except ImageShareError:
            raise
        except Exception as exc:
            raise ImageShareError(f"Upload failed: {exc}") from exc

        if not url.startswith("http"):
            raise ImageShareError(f"Unexpected response from hosting service: {url!r}")
        return url

    def _post_multipart(self, path: Path, content_type: str) -> str:
        """Build and send a multipart/form-data POST request without requests lib."""
        boundary = "----QRGenBoundary7MA4YWxkTrZu0gW"
        data = path.read_bytes()

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            f"Content-Type: {content_type}\r\n"
            f"\r\n"
        ).encode() + data + f"\r\n--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            self._ENDPOINT,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8").strip()
        except urllib.error.HTTPError as exc:
            raise ImageShareError(
                f"Upload rejected (HTTP {exc.code}): {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ImageShareError(
                f"Network error during upload: {exc.reason}"
            ) from exc
