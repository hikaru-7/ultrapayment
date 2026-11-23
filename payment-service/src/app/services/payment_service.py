from ..repositories.payment_repository import PaymentRepository
from ..schemas.payment import PaymentCreate
from .payment_state_machine import PaymentStateMachine, PaymentStatus


class PaymentNotFoundError(Exception):
    pass


class PaymentService:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    def create_payment(self, data: PaymentCreate):
        try:
            payment = self.repository.create(
                merchant_id=data.merchant_id,
                amount=data.amount,
                currency=data.currency,
            )

            self.repository.create_attempt(
                payment_id=payment.id,
            )

            self.repository.commit()
            self.repository.refresh(payment)

            return payment

        except Exception:
            self.repository.rollback()
            raise

    def get_payment(self, payment_id: int):
        payment = self.repository.get_by_id(payment_id)

        if payment is None:
            raise PaymentNotFoundError()

        return payment

    def get_payments(
        self,
        limit: int,
        offset: int,
    ):
        return self.repository.get_all(
            limit=limit,
            offset=offset,
        )

    def _change_status(
        self,
        payment_id: int,
        new_status: PaymentStatus,
    ):
        try:
            payment = self.repository.get_by_id_for_update(
                payment_id,
            )

            if payment is None:
                raise PaymentNotFoundError()

            PaymentStateMachine.transition(
                payment,
                new_status,
            )

            self.repository.commit()
            self.repository.refresh(payment)

            return payment

        except Exception:
            self.repository.rollback()
            raise

    def process_payment(self, payment_id: int):
        return self._change_status(
            payment_id,
            PaymentStatus.PROCESSING,
        )

    def succeed_payment(self, payment_id: int):
        return self._change_status(
            payment_id,
            PaymentStatus.SUCCEEDED,
        )

    def fail_payment(self, payment_id: int):
        return self._change_status(
            payment_id,
            PaymentStatus.FAILED,
        )