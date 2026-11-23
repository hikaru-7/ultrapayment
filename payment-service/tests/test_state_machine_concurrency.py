from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from app.db.database import SessionLocal
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService
from app.services.payment_state_machine import InvalidPaymentTransitionError


def test_concurrent_final_status_update():
    setup_db = SessionLocal()

    payment = Payment(
        merchant_id="state-machine-concurrency",
        amount=Decimal("100.00"),
        currency="EUR",
        status="processing",
    )

    setup_db.add(payment)
    setup_db.commit()
    setup_db.refresh(payment)

    payment_id = payment.id
    setup_db.close()

    start = Barrier(2)

    def update_payment(target_status: str) -> str:
        db = SessionLocal()
        repository = PaymentRepository(db)
        service = PaymentService(repository)

        try:
            start.wait()

            if target_status == "succeeded":
                service.succeed_payment(payment_id)
            else:
                service.fail_payment(payment_id)

            return target_status

        except InvalidPaymentTransitionError:
            return "rejected"

        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_one = executor.submit(
            update_payment,
            "succeeded",
        )
        future_two = executor.submit(
            update_payment,
            "failed",
        )

        results = [
            future_one.result(),
            future_two.result(),
        ]

    assert results.count("rejected") == 1
    assert len(results) == 2

    check_db = SessionLocal()
    payment = check_db.get(Payment, payment_id)

    assert payment.status in {
        "succeeded",
        "failed",
    }

    check_db.delete(payment)
    check_db.commit()
    check_db.close()