import httpx
import pytest
from app.clients.user_client import UserClient, UserServiceTimeoutError


def test_user_service_timeout(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ReadTimeout("User service is too slow")

    monkeypatch.setattr(httpx, "get", fake_get)

    client = UserClient()

    with pytest.raises(UserServiceTimeoutError):
        client.ensure_user_exists(
            user_id=1,
            request_id="test-request-id",
        )


def test_request_id_is_sent_to_user_service(monkeypatch):
    captured_headers = {}

    class FakeResponse:
        status_code = 200

    def fake_get(*args, **kwargs):
        captured_headers.update(kwargs["headers"])
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)

    client = UserClient()

    client.ensure_user_exists(
        user_id=1,
        request_id="abc-123",
    )

    assert captured_headers["X-Request-ID"] == "abc-123"
