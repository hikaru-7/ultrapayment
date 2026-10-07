from ..repositories.payment_repository import PaymentRepository
from ..schemas.payment import PaymentCreate


class PaymentNotFoundError(Exception):
    pass


class PaymentService:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    def create_payment(self, data: PaymentCreate):
        return self.repository.create(
            merchant_id=data.merchant_id,
            amount=data.amount,
            currency=data.currency,
        )

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