from decimal import Decimal

import pytest

from app.models.payment import Payment
from app.services.payment_state_machine import (
    InvalidPaymentTransitionError,
    PaymentStateMachine,
    PaymentStatus,
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


def test_succeeded_cannot_be_processed_again():
    payment = create_payment("succeeded")

    with pytest.raises(InvalidPaymentTransitionError):
        PaymentStateMachine.process(payment)

    assert payment.status == "succeeded"


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        (PaymentStatus.CREATED, PaymentStatus.CREATED),
        (PaymentStatus.CREATED, PaymentStatus.SUCCEEDED),
        (PaymentStatus.CREATED, PaymentStatus.FAILED),
        (PaymentStatus.PROCESSING, PaymentStatus.CREATED),
        (PaymentStatus.PROCESSING, PaymentStatus.PROCESSING),
        (PaymentStatus.SUCCEEDED, PaymentStatus.CREATED),
        (PaymentStatus.SUCCEEDED, PaymentStatus.SUCCEEDED),
        (PaymentStatus.SUCCEEDED, PaymentStatus.FAILED),
        (PaymentStatus.FAILED, PaymentStatus.CREATED),
        (PaymentStatus.FAILED, PaymentStatus.PROCESSING),
        (PaymentStatus.FAILED, PaymentStatus.SUCCEEDED),
        (PaymentStatus.FAILED, PaymentStatus.FAILED),
    ],
)
def test_forbidden_transitions(
    current_status: PaymentStatus,
    new_status: PaymentStatus,
):
    payment = create_payment(current_status.value)

    with pytest.raises(InvalidPaymentTransitionError):
        PaymentStateMachine.transition(
            payment,
            new_status,
        )

    assert payment.status == current_status.value