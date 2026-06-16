from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database import db
from app.models.account_table import AccountTable
from app.database.db import SessionLocal
from app.models.transaction_table import TransactionTable
import uuid
from datetime import datetime


class AccountService:
    def __init__(self):
        pass  # no more in-memory storage

    # ---------------- CREATE ACCOUNT ----------------
    def create_account(self, user_id: str):
        db = SessionLocal()

        # check if account exists
        existing = db.query(AccountTable).filter(AccountTable.user_id == user_id).first()

        if existing:
            db.close()
            raise HTTPException(status_code=409, detail="Account already exists")

        account = AccountTable(user_id=user_id, balance=0.0)

        db.add(account)
        db.commit()
        db.refresh(account)

        db.close()
        return {
    "user_id": account.user_id,
    "balance": account.balance
        }

    # ---------------- GET ACCOUNT ----------------
    def get_account(self, user_id: str):
        db = SessionLocal()

        account = db.query(AccountTable).filter(AccountTable.user_id == user_id).first()

        db.close()
        if not account:
            db.close()
            raise HTTPException(status_code=404, detail="Account not found")

        return {
            "user_id": account.user_id,
            "balance": account.balance
        }

    # ---------------- TRANSFER ----------------
    def transfer(self, sender_id: str, receiver_id: str, amount: float):
        db = SessionLocal()

        sender = db.query(AccountTable).filter(AccountTable.user_id == sender_id).first()
        receiver = db.query(AccountTable).filter(AccountTable.user_id == receiver_id).first()

        if not sender or not receiver:
            db.close()
            raise HTTPException(status_code=404, detail="Account not found")

        if sender.balance < amount:
            db.close()
            raise HTTPException(status_code=400, detail="Insufficient balance")

        sender.balance -= amount
        receiver.balance += amount



        transaction = TransactionTable(
        id=str(uuid.uuid4()),
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        timestamp=datetime.utcnow()
)

        db.add(transaction)
        db.commit()
        db.close()
        
        return {
            "id": transaction.id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "timestamp": transaction.timestamp
        }      

    def get_transactions(self):
        db = SessionLocal()

        transactions = db.query(TransactionTable).all()

        db.close()
        return transactions
    def get_all_accounts(self):
        db = SessionLocal()

        accounts = db.query(AccountTable).all()

        result = []
        for acc in accounts:
            result.append({
                "user_id": acc.user_id,
                "balance": acc.balance
            })

        db.close()
        return result
    def deposit(self, user_id: str, amount: float):
        db = SessionLocal()

        account = db.query(AccountTable).filter(AccountTable.user_id == user_id).first()

        if not account:
            db.close()
            raise HTTPException(status_code=404, detail="Account not found")

        account.balance += amount

        db.commit()
        db.close()

        return {
            "user_id": user_id,
            "new_balance": account.balance
        }