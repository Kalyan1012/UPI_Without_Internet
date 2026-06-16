from pydantic import BaseModel
from datetime import datetime


class PaymentInstruction(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float
    nonce: str
    signed_at: datetime