from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    merchant_id: str
    amount: Decimal = Field(ge=0)
    currency: str


class PaymentResponse(BaseModel):
    id: int
    merchant_id: str
    amount: Decimal
    currency: str
    status: str