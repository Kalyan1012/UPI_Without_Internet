from fastapi import FastAPI
from pydantic import BaseModel
from app.services.account_service import AccountService

app = FastAPI()
from app.database.db import init_db

init_db()
service = AccountService()


class CreateAccountRequest(BaseModel):
    user_id: str


class TransferRequest(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float

class DepositRequest(BaseModel):
    user_id: str
    amount: float


@app.post("/account/deposit")
def deposit(request: DepositRequest):
    return service.deposit(request.user_id, request.amount)



@app.post("/account/create")
def create_account(request: CreateAccountRequest):
    return service.create_account(request.user_id)


@app.get("/account/{user_id}")
def get_account(user_id: str):
    return service.get_account(user_id)


@app.post("/account/transfer")
def transfer(request: TransferRequest):
    return service.transfer(
        request.transaction_id,
        request.sender_id,
        request.receiver_id,
        request.amount
    )


@app.get("/transactions")
def get_transactions():
    return service.get_transactions()


@app.get("/accounts")
def get_all_accounts():
    return service.get_all_accounts()    
