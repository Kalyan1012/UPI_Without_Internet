from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: datetime = datetime.utcnow()