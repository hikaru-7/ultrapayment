from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.payment import Payment, PaymentAttempt


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
        self.db.flush()

        return payment

    def create_attempt(
        self,
        payment_id: int,
    ) -> PaymentAttempt:
        attempt = PaymentAttempt(
            payment_id=payment_id,
        )

        self.db.add(attempt)
        self.db.flush()

        return attempt

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, payment: Payment) -> None:
        self.db.refresh(payment)

    def get_by_id(self, payment_id: int) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

    def get_by_id_for_update(
        self,
        payment_id: int,
    ) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .with_for_update()
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