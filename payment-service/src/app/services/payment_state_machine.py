from enum import Enum

from ..models.payment import Payment


class PaymentStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class InvalidPaymentTransitionError(Exception):
    pass


ALLOWED_TRANSITIONS = {
    PaymentStatus.CREATED: {
        PaymentStatus.PROCESSING,
    },
    PaymentStatus.PROCESSING: {
        PaymentStatus.SUCCEEDED,
        PaymentStatus.FAILED,
    },
    PaymentStatus.SUCCEEDED: set(),
    PaymentStatus.FAILED: set(),
}


class PaymentStateMachine:
    @staticmethod
    def transition(
        payment: Payment,
        new_status: PaymentStatus,
    ) -> Payment:
        current_status = PaymentStatus(payment.status)

        if new_status not in ALLOWED_TRANSITIONS[current_status]:
            raise InvalidPaymentTransitionError(
                f"Cannot change payment status "
                f"from {current_status.value} to {new_status.value}"
            )

        payment.status = new_status.value

        return payment

    @staticmethod
    def process(payment: Payment) -> Payment:
        return PaymentStateMachine.transition(
            payment,
            PaymentStatus.PROCESSING,
        )

    @staticmethod
    def succeed(payment: Payment) -> Payment:
        return PaymentStateMachine.transition(
            payment,
            PaymentStatus.SUCCEEDED,
        )

    @staticmethod
    def fail(payment: Payment) -> Payment:
        return PaymentStateMachine.transition(
            payment,
            PaymentStatus.FAILED,
        )