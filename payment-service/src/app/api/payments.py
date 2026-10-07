from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..repositories.payment_repository import PaymentRepository
from ..schemas.payment import PaymentCreate, PaymentResponse
from ..services.payment_service import PaymentNotFoundError, PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


def get_payment_service(
    db: Annotated[Session, Depends(get_db)],
) -> PaymentService:
    repository = PaymentRepository(db)

    return PaymentService(repository)


PaymentServiceDep = Annotated[
    PaymentService,
    Depends(get_payment_service),
]


@router.post("", response_model=PaymentResponse)
def create_payment(
    data: PaymentCreate,
    service: PaymentServiceDep,
):
    return service.create_payment(data)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    service: PaymentServiceDep,
):
    try:
        return service.get_payment(payment_id)
    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        ) from exc


@router.get("", response_model=list[PaymentResponse])
def get_payments(
    service: PaymentServiceDep,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return service.get_payments(
        limit=limit,
        offset=offset,
    )