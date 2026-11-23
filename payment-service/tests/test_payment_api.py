from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.payments import get_payment_service
from app.main import app
from app.services.payment_service import PaymentNotFoundError
from app.services.payment_state_machine import InvalidPaymentTransitionError


class FakePayment:
    def __init__(
        self,
        payment_id: int,
        status: str,
    ):
        self.id = payment_id
        self.merchant_id = "api-test"
        self.amount = Decimal("100.00")
        self.currency = "EUR"
        self.status = status


class FakePaymentService:
    def __init__(self):
        self.payment = FakePayment(
            payment_id=1,
            status="created",
        )

    def process_payment(self, payment_id: int):
        if payment_id != self.payment.id:
            raise PaymentNotFoundError()

        if self.payment.status != "created":
            raise InvalidPaymentTransitionError(
                f"Cannot change payment status "
                f"from {self.payment.status} to processing"
            )

        self.payment.status = "processing"

        return self.payment

    def succeed_payment(self, payment_id: int):
        if payment_id != self.payment.id:
            raise PaymentNotFoundError()

        if self.payment.status != "processing":
            raise InvalidPaymentTransitionError(
                f"Cannot change payment status "
                f"from {self.payment.status} to succeeded"
            )

        self.payment.status = "succeeded"

        return self.payment

    def fail_payment(self, payment_id: int):
        if payment_id != self.payment.id:
            raise PaymentNotFoundError()

        if self.payment.status != "processing":
            raise InvalidPaymentTransitionError(
                f"Cannot change payment status "
                f"from {self.payment.status} to failed"
            )

        self.payment.status = "failed"

        return self.payment


def create_client(
    service: FakePaymentService,
) -> TestClient:
    app.dependency_overrides[get_payment_service] = lambda: service

    return TestClient(app)


def test_process_payment():
    service = FakePaymentService()
    client = create_client(service)

    response = client.post("/payments/1/process")

    assert response.status_code == 200
    assert response.json()["status"] == "processing"

    app.dependency_overrides.clear()


def test_process_payment_not_found():
    service = FakePaymentService()
    client = create_client(service)

    response = client.post("/payments/999/process")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

    app.dependency_overrides.clear()


def test_invalid_transition_returns_conflict():
    service = FakePaymentService()
    service.payment.status = "succeeded"

    client = create_client(service)

    response = client.post("/payments/1/process")

    assert response.status_code == 409
    assert "Cannot change payment status" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_processing_payment_can_succeed():
    service = FakePaymentService()
    service.payment.status = "processing"

    client = create_client(service)

    response = client.post("/payments/1/succeed")

    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"

    app.dependency_overrides.clear()


def test_processing_payment_can_fail():
    service = FakePaymentService()
    service.payment.status = "processing"

    client = create_client(service)

    response = client.post("/payments/1/fail")

    assert response.status_code == 200
    assert response.json()["status"] == "failed"

    app.dependency_overrides.clear()