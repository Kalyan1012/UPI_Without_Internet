from app.models.account import Account
from app.models.transaction import Transaction


class AccountService:
    def __init__(self):
        # in-memory storage (temporary "database")
        self.accounts = {}

    def create_account(self, user_id: str) -> Account:
        if user_id in self.accounts:
            raise Exception("Account already exists")

        account = Account(user_id=user_id, balance=0.0)
        self.accounts[user_id] = account
        return account

    def get_account(self, user_id: str) -> Account:
        return self.accounts.get(user_id)

    def transfer(self, sender_id: str, receiver_id: str, amount: float) -> Transaction:
        sender = self.accounts.get(sender_id)
        receiver = self.accounts.get(receiver_id)

        if not sender or not receiver:
            raise Exception("Account not found")

        if sender.balance < amount:
            raise Exception("Insufficient balance")

        sender.balance -= amount
        receiver.balance += amount

        return Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount
        )