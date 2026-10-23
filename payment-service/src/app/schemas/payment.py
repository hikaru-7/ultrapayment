from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    merchant_id: str
    amount: Decimal = Field(ge=0)
    currency: str = Field(
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )


class PaymentResponse(BaseModel):
    id: int
    merchant_id: str
    amount: Decimal
    currency: str
    status: str