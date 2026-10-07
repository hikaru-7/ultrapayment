from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        merchant_id: str,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        payment = Payment(
            merchant_id=merchant_id,
            amount=amount,
            currency=currency,
        )

        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

    def get_all(
        self,
        limit: int,
        offset: int,
    ) -> list[Payment]:
        return (
            self.db.query(Payment)
            .offset(offset)
            .limit(limit)
            .all()
        )