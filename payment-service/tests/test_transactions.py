from decimal import Decimal

import pytest

from app.db.database import SessionLocal
from app.models.payment import Payment, PaymentAttempt
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentCreate
from app.services.payment_service import PaymentService


def test_transaction_rolls_back(monkeypatch):
    db = SessionLocal()
    repository = PaymentRepository(db)
    service = PaymentService(repository)

    data = PaymentCreate(
        merchant_id="rollback-test",
        amount=Decimal("25.50"),
        currency="EUR",
    )

    payment_id = []

    def fail_attempt(payment_id: int):
        raise RuntimeError("forced failure")

    original_create = repository.create

    def create_and_remember(*args, **kwargs):
        payment = original_create(*args, **kwargs)
        payment_id.append(payment.id)
        return payment

    monkeypatch.setattr(repository, "create", create_and_remember)
    monkeypatch.setattr(repository, "create_attempt", fail_attempt)

    with pytest.raises(RuntimeError):
        service.create_payment(data)

    db.close()

    check_db = SessionLocal()

    assert check_db.get(Payment, payment_id[0]) is None

    assert (
        check_db.query(PaymentAttempt)
        .filter(PaymentAttempt.payment_id == payment_id[0])
        .first()
        is None
    )

    check_db.close()


def test_concurrent_payment_update():
    setup_db = SessionLocal()

    payment = Payment(
        merchant_id="concurrency-test",
        amount=Decimal("100.00"),
        currency="EUR",
    )

    setup_db.add(payment)
    setup_db.commit()
    setup_db.refresh(payment)

    payment_id = payment.id
    setup_db.close()

    db_one = SessionLocal()
    db_two = SessionLocal()

    payment_one = db_one.get(Payment, payment_id)
    payment_two = db_two.get(Payment, payment_id)

    payment_one.amount += Decimal("10.00")
    payment_two.amount += Decimal("10.00")

    db_one.commit()
    db_two.commit()

    db_one.close()
    db_two.close()

    check_db = SessionLocal()
    payment = check_db.get(Payment, payment_id)

    assert payment.amount == Decimal("110.00")

    check_db.delete(payment)
    check_db.commit()
    check_db.close()