from decimal import Decimal

import pytest

from app.models.payment import Payment
from app.services.payment_state_machine import (
    InvalidPaymentTransitionError,
    PaymentStateMachine,
)


def create_payment(status: str) -> Payment:
    return Payment(
        merchant_id="state-machine-test",
        amount=Decimal("100.00"),
        currency="EUR",
        status=status,
    )


def test_created_can_be_processed():
    payment = create_payment("created")

    PaymentStateMachine.process(payment)

    assert payment.status == "processing"


def test_processing_can_succeed():
    payment = create_payment("processing")

    PaymentStateMachine.succeed(payment)

    assert payment.status == "succeeded"


def test_processing_can_fail():
    payment = create_payment("processing")

    PaymentStateMachine.fail(payment)

    assert payment.status == "failed"


def test_created_cannot_succeed_directly():
    payment = create_payment("created")

    with pytest.raises(InvalidPaymentTransitionError):
        PaymentStateMachine.succeed(payment)

    assert payment.status == "created"


def test_succeeded_cannot_be_processed_again():
    payment = create_payment("succeeded")

    with pytest.raises(InvalidPaymentTransitionError):
        PaymentStateMachine.process(payment)

    assert payment.status == "succeeded"


def test_failed_cannot_succeed():
    payment = create_payment("failed")

    with pytest.raises(InvalidPaymentTransitionError):
        PaymentStateMachine.succeed(payment)

    assert payment.status == "failed"