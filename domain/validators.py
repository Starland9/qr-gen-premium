"""Input validators for each QR code type."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: dict[str, str] = field(default_factory=dict)


class TextValidator:
    """Validates plain text QR data."""

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        text = data.get("text", "").strip()
        if not text:
            errors["text"] = "Text cannot be empty."
        elif len(text) > 2953:
            errors["text"] = "Text is too long for a QR code (max 2953 chars)."
        return ValidationResult(is_valid=not errors, errors=errors)


class URLValidator:
    """Validates URL QR data."""

    _URL_RE = re.compile(
        r"^(https?://)"
        r"([a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+)$"
    )

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        url = data.get("url", "").strip()
        if not url:
            errors["url"] = "URL cannot be empty."
        elif not self._URL_RE.match(url):
            errors["url"] = "Invalid URL format. Must start with http:// or https://."
        return ValidationResult(is_valid=not errors, errors=errors)


class EmailValidator:
    """Validates email QR data."""

    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        email = data.get("email", "").strip()
        if not email:
            errors["email"] = "Email cannot be empty."
        elif not self._EMAIL_RE.match(email):
            errors["email"] = "Invalid email address."
        return ValidationResult(is_valid=not errors, errors=errors)


class PhoneValidator:
    """Validates phone number QR data."""

    _PHONE_RE = re.compile(r"^\+?[\d\s\-().]{6,20}$")

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        phone = data.get("phone", "").strip()
        if not phone:
            errors["phone"] = "Phone number cannot be empty."
        elif not self._PHONE_RE.match(phone):
            errors["phone"] = "Invalid phone number format."
        return ValidationResult(is_valid=not errors, errors=errors)


class SMSValidator:
    """Validates SMS QR data."""

    _PHONE_RE = re.compile(r"^\+?[\d\s\-().]{6,20}$")

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        phone = data.get("phone", "").strip()
        message = data.get("message", "").strip()
        if not phone:
            errors["phone"] = "Phone number cannot be empty."
        elif not self._PHONE_RE.match(phone):
            errors["phone"] = "Invalid phone number format."
        if not message:
            errors["message"] = "Message cannot be empty."
        return ValidationResult(is_valid=not errors, errors=errors)


class VCardValidator:
    """Validates vCard QR data."""

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        first = data.get("first_name", "").strip()
        last = data.get("last_name", "").strip()
        if not first and not last:
            errors["first_name"] = "At least a first or last name is required."
        phone = data.get("phone", "").strip()
        if phone and not re.match(r"^\+?[\d\s\-().]{6,20}$", phone):
            errors["phone"] = "Invalid phone number format."
        email = data.get("email", "").strip()
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            errors["email"] = "Invalid email address."
        return ValidationResult(is_valid=not errors, errors=errors)


class WiFiValidator:
    """Validates WiFi QR data."""

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        ssid = data.get("ssid", "").strip()
        if not ssid:
            errors["ssid"] = "SSID cannot be empty."
        security = data.get("security", "WPA")
        password = data.get("password", "").strip()
        if security != "nopass" and not password:
            errors["password"] = "Password required for secured networks."
        return ValidationResult(is_valid=not errors, errors=errors)


class GeoValidator:
    """Validates geographic coordinate QR data."""

    def validate(self, data: dict[str, str]) -> ValidationResult:
        errors: dict[str, str] = {}
        try:
            lat = float(data.get("latitude", ""))
            if not (-90 <= lat <= 90):
                errors["latitude"] = "Latitude must be between -90 and 90."
        except (ValueError, TypeError):
            errors["latitude"] = "Latitude must be a valid number."
        try:
            lon = float(data.get("longitude", ""))
            if not (-180 <= lon <= 180):
                errors["longitude"] = "Longitude must be between -180 and 180."
        except (ValueError, TypeError):
            errors["longitude"] = "Longitude must be a valid number."
        return ValidationResult(is_valid=not errors, errors=errors)
