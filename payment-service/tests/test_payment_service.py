from decimal import Decimal

import pytest

from app.schemas.payment import PaymentCreate
from app.services.payment_service import (
    PaymentNotFoundError,
    PaymentService,
)


class FakePayment:
    def __init__(
        self,
        payment_id,
        merchant_id,
        amount,
        currency,
    ):
        self.id = payment_id
        self.merchant_id = merchant_id
        self.amount = amount
        self.currency = currency


class FakePaymentRepository:
    def __init__(self):
        self.created_payment = None
        self.payment_to_return = None
        self.all_payments = []

        self.attempt_created = False
        self.committed = False
        self.rolled_back = False

    def create(
        self,
        merchant_id: str,
        amount: Decimal,
        currency: str,
    ):
        self.created_payment = FakePayment(
            payment_id=1,
            merchant_id=merchant_id,
            amount=amount,
            currency=currency,
        )

        return self.created_payment

    def create_attempt(self, payment_id: int):
        self.attempt_created = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def refresh(self, payment):
        pass

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

    assert result.merchant_id == "merchant-1"
    assert result.amount == Decimal("10.50")
    assert result.currency == "EUR"

    assert repository.attempt_created is True
    assert repository.committed is True
    assert repository.rolled_back is False


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