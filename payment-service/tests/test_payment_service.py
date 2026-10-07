from decimal import Decimal

import pytest
from app.schemas.payment import PaymentCreate
from app.services.payment_service import (
    PaymentNotFoundError,
    PaymentService,
)


class FakePaymentRepository:
    def __init__(self):
        self.created_payment = None
        self.payment_to_return = None
        self.all_payments = []

    def create(
        self,
        merchant_id: str,
        amount: Decimal,
        currency: str,
    ):
        self.created_payment = {
            "merchant_id": merchant_id,
            "amount": amount,
            "currency": currency,
        }

        return self.created_payment

    def get_by_id(self, payment_id: int):
        return self.payment_to_return

    def get_all(
        self,
        limit: int,
        offset: int,
    ):
        return self.all_payments[offset : offset + limit]


def test_create_payment():
    repository = FakePaymentRepository()
    service = PaymentService(repository)

    data = PaymentCreate(
        merchant_id="merchant-1",
        amount=Decimal("10.50"),
        currency="EUR",
    )

    result = service.create_payment(data)

    assert result["merchant_id"] == "merchant-1"
    assert result["amount"] == Decimal("10.50")
    assert result["currency"] == "EUR"


def test_get_payment():
    repository = FakePaymentRepository()
    repository.payment_to_return = {
        "id": 1,
        "merchant_id": "merchant-1",
    }

    service = PaymentService(repository)

    result = service.get_payment(1)

    assert result["id"] == 1


def test_get_payment_not_found():
    repository = FakePaymentRepository()
    service = PaymentService(repository)

    with pytest.raises(PaymentNotFoundError):
        service.get_payment(999)


def test_get_payments_with_pagination():
    repository = FakePaymentRepository()
    repository.all_payments = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]

    service = PaymentService(repository)

    result = service.get_payments(
        limit=2,
        offset=1,
    )

    assert result == [
        {"id": 2},
        {"id": 3},
    ]