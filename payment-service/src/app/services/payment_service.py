from ..repositories.payment_repository import PaymentRepository
from ..schemas.payment import PaymentCreate
from .payment_state_machine import PaymentStateMachine


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

    def process_payment(self, payment_id: int):
        payment = self.get_payment(payment_id)

        PaymentStateMachine.process(payment)

        self.repository.commit()
        self.repository.refresh(payment)

        return payment

    def succeed_payment(self, payment_id: int):
        payment = self.get_payment(payment_id)

        PaymentStateMachine.succeed(payment)

        self.repository.commit()
        self.repository.refresh(payment)

        return payment

    def fail_payment(self, payment_id: int):
        payment = self.get_payment(payment_id)

        PaymentStateMachine.fail(payment)

        self.repository.commit()
        self.repository.refresh(payment)

        return payment