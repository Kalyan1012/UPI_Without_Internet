from dataclasses import dataclass

@dataclass
class Account:
    user_id: str
    balance: float = 0.0