from decimal import Decimal
from threading import Event, Thread
from time import sleep

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

    first_has_lock = Event()
    second_is_trying = Event()
    release_first = Event()
    second_has_lock = Event()

    def first_process():
        db = SessionLocal()
        repository = PaymentRepository(db)

        payment = repository.get_by_id_for_update(payment_id)

        print(f"Process 1 locked payment. Amount: {payment.amount}")

        first_has_lock.set()

        release_first.wait()

        payment.amount += Decimal("10.00")
        repository.commit()

        print(f"Process 1 committed. Amount: {payment.amount}")

        db.close()

    def second_process():
        first_has_lock.wait()

        db = SessionLocal()
        repository = PaymentRepository(db)

        print("Process 2 is trying to lock the same payment...")

        second_is_trying.set()

        payment = repository.get_by_id_for_update(payment_id)

        second_has_lock.set()

        print(f"Process 2 got the lock. Amount: {payment.amount}")

        payment.amount += Decimal("10.00")
        repository.commit()

        print(f"Process 2 committed. Amount: {payment.amount}")

        db.close()

    thread_one = Thread(target=first_process)
    thread_two = Thread(target=second_process)

    thread_one.start()
    thread_two.start()

    first_has_lock.wait()
    second_is_trying.wait()

    sleep(1)

    assert second_has_lock.is_set() is False

    print("Process 2 is blocked by Process 1")

    release_first.set()

    thread_one.join()
    thread_two.join()

    assert second_has_lock.is_set() is True

    check_db = SessionLocal()
    payment = check_db.get(Payment, payment_id)

    assert payment.amount == Decimal("120.00")

    check_db.delete(payment)
    check_db.commit()
    check_db.close()