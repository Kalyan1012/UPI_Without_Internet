from fastapi import HTTPException
from app.database.db import SessionLocal
from app.models.account_table import AccountTable
from app.models.transaction_table import TransactionTable
from datetime import datetime


class AccountService:
    def __init__(self):
        self.processed_transactions = set()

    # ---------------- CREATE ACCOUNT ----------------
    def create_account(self, user_id: str):
        db = SessionLocal()

        try:
            existing = db.query(AccountTable).filter(
                AccountTable.user_id == user_id
            ).first()

            if existing:
                raise HTTPException(status_code=409, detail="Account already exists")

            account = AccountTable(user_id=user_id, balance=0.0)

            db.add(account)
            db.commit()
            db.refresh(account)

            return {
                "user_id": account.user_id,
                "balance": account.balance
            }

        finally:
            db.close()

    # ---------------- GET ACCOUNT ----------------
    def get_account(self, user_id: str):
        db = SessionLocal()

        try:
            account = db.query(AccountTable).filter(
                AccountTable.user_id == user_id
            ).first()

            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            return {
                "user_id": account.user_id,
                "balance": account.balance
            }

        finally:
            db.close()

    # ---------------- TRANSFER MONEY ----------------
    def transfer(self, transaction_id: str, sender_id: str, receiver_id: str, amount: float):
        db = SessionLocal()

        try:
            # 🔒 Idempotency check
            existing_txn = db.query(TransactionTable).filter(
                TransactionTable.id == transaction_id
            ).first()

            if existing_txn:
                return {"message": "duplicate transaction ignored"}

            sender = db.query(AccountTable).filter(
                AccountTable.user_id == sender_id
            ).first()

            receiver = db.query(AccountTable).filter(
                AccountTable.user_id == receiver_id
            ).first()

            if not sender:
                raise HTTPException(status_code=404, detail=f"Sender not found: {sender_id}")

            if not receiver:
                raise HTTPException(status_code=404, detail=f"Receiver not found: {receiver_id}")

            if sender.balance < amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")

            # 💸 update balances
            sender.balance -= amount
            receiver.balance += amount

            # 🧾 transaction record
            transaction = TransactionTable(
                id=transaction_id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                amount=amount,
                timestamp=datetime.utcnow()
            )

            db.add(transaction)
            db.commit()

            return {
                "message": "transfer successful",
                "transaction_id": transaction_id
            }

        finally:
            db.close()

    # ---------------- DEPOSIT ----------------
    def deposit(self, user_id: str, amount: float):
        db = SessionLocal()

        try:
            account = db.query(AccountTable).filter(
                AccountTable.user_id == user_id
            ).first()

            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            account.balance += amount
            db.commit()

            return {
                "user_id": user_id,
                "new_balance": account.balance
            }

        finally:
            db.close()

    # ---------------- GET ALL ACCOUNTS ----------------
    def get_all_accounts(self):
        db = SessionLocal()

        try:
            accounts = db.query(AccountTable).all()

            return [
                {
                    "user_id": acc.user_id,
                    "balance": acc.balance
                }
                for acc in accounts
            ]

        finally:
            db.close()

    # ---------------- GET TRANSACTIONS ----------------
    def get_transactions(self):
        db = SessionLocal()

        try:
            return db.query(TransactionTable).all()

        finally:
            db.close()

    # ---------------- RESET SYSTEM ----------------
    def reset_all(self):
        db = SessionLocal()

        try:
            db.query(TransactionTable).delete()
            db.query(AccountTable).delete()
            db.commit()

            users = ["kalyan", "cutie", "rahul", "priya"]

            for user in users:
                db.add(AccountTable(user_id=user.lower(), balance=1000))

            db.commit()

            return {"message": "reset + clean seed done"}

        finally:
            db.close()