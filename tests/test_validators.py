"""Tests for input validators."""

from __future__ import annotations

import pytest

from domain.validators import (
    EmailValidator,
    GeoValidator,
    PhoneValidator,
    SMSValidator,
    TextValidator,
    URLValidator,
    VCardValidator,
    WiFiValidator,
)


class TestTextValidator:
    def test_valid(self) -> None:
        result = TextValidator().validate({"text": "Hello World"})
        assert result.is_valid

    def test_empty(self) -> None:
        result = TextValidator().validate({"text": ""})
        assert not result.is_valid
        assert "text" in result.errors

    def test_too_long(self) -> None:
        result = TextValidator().validate({"text": "x" * 3000})
        assert not result.is_valid


class TestURLValidator:
    def test_valid_https(self) -> None:
        assert URLValidator().validate({"url": "https://example.com"}).is_valid

    def test_valid_http(self) -> None:
        assert URLValidator().validate({"url": "http://example.com/path?q=1"}).is_valid

    def test_missing_scheme(self) -> None:
        result = URLValidator().validate({"url": "example.com"})
        assert not result.is_valid

    def test_empty(self) -> None:
        assert not URLValidator().validate({"url": ""}).is_valid


class TestEmailValidator:
    def test_valid(self) -> None:
        assert EmailValidator().validate({"email": "user@example.com"}).is_valid

    def test_invalid(self) -> None:
        assert not EmailValidator().validate({"email": "notanemail"}).is_valid

    def test_empty(self) -> None:
        assert not EmailValidator().validate({"email": ""}).is_valid


class TestPhoneValidator:
    def test_valid(self) -> None:
        assert PhoneValidator().validate({"phone": "+1 555 123 4567"}).is_valid

    def test_invalid(self) -> None:
        assert not PhoneValidator().validate({"phone": "abc"}).is_valid

    def test_empty(self) -> None:
        assert not PhoneValidator().validate({"phone": ""}).is_valid


class TestSMSValidator:
    def test_valid(self) -> None:
        result = SMSValidator().validate({"phone": "+15551234567", "message": "Hi"})
        assert result.is_valid

    def test_missing_message(self) -> None:
        result = SMSValidator().validate({"phone": "+15551234567", "message": ""})
        assert not result.is_valid
        assert "message" in result.errors


class TestVCardValidator:
    def test_valid_minimal(self) -> None:
        result = VCardValidator().validate({"first_name": "John", "last_name": ""})
        assert result.is_valid

    def test_no_name(self) -> None:
        result = VCardValidator().validate({"first_name": "", "last_name": ""})
        assert not result.is_valid

    def test_invalid_email(self) -> None:
        result = VCardValidator().validate({
            "first_name": "John", "last_name": "Doe", "email": "notvalid"
        })
        assert not result.is_valid


class TestWiFiValidator:
    def test_valid_wpa(self) -> None:
        result = WiFiValidator().validate({"ssid": "MyNet", "security": "WPA", "password": "secret"})
        assert result.is_valid

    def test_no_ssid(self) -> None:
        result = WiFiValidator().validate({"ssid": "", "security": "WPA", "password": "secret"})
        assert not result.is_valid

    def test_no_password_secured(self) -> None:
        result = WiFiValidator().validate({"ssid": "MyNet", "security": "WPA", "password": ""})
        assert not result.is_valid

    def test_open_no_password(self) -> None:
        result = WiFiValidator().validate({"ssid": "OpenNet", "security": "nopass", "password": ""})
        assert result.is_valid


class TestGeoValidator:
    def test_valid(self) -> None:
        result = GeoValidator().validate({"latitude": "37.7749", "longitude": "-122.4194"})
        assert result.is_valid

    def test_out_of_range_lat(self) -> None:
        result = GeoValidator().validate({"latitude": "100", "longitude": "0"})
        assert not result.is_valid

    def test_non_numeric(self) -> None:
        result = GeoValidator().validate({"latitude": "abc", "longitude": "0"})
        assert not result.is_valid
