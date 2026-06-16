from fastapi import FastAPI
from pydantic import BaseModel
from app.services.account_service import AccountService

app = FastAPI()
service = AccountService()


class CreateAccountRequest(BaseModel):
    user_id: str


class TransferRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float


@app.post("/account/create")
def create_account(request: CreateAccountRequest):
    return service.create_account(request.user_id)


@app.get("/account/{user_id}")
def get_account(user_id: str):
    return service.get_account(user_id)


@app.post("/account/transfer")
def transfer(request: TransferRequest):
    return service.transfer(
        request.sender_id,
        request.receiver_id,
        request.amount
    )


@app.get("/transactions")
def get_transactions():
    
    return service.get_transactions()
