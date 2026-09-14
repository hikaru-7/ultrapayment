import httpx
import pytest
from fastapi import HTTPException

from app.main import check_user


def test_user_service_timeout(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ReadTimeout("User service is too slow")

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(HTTPException) as error:
        check_user(1, "test-request-id")

    assert error.value.status_code == 503
    assert error.value.detail == "User service timeout"


def test_request_id_is_sent_to_user_service(monkeypatch):
    captured_headers = {}

    class FakeResponse:
        status_code = 200

    def fake_get(*args, **kwargs):
        captured_headers.update(kwargs["headers"])
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)

    check_user(1, "abc-123")

    assert captured_headers["X-Request-ID"] == "abc-123"