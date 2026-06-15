from fastapi import FastAPI
from pydantic import BaseModel

from app.services.account_service import AccountService

app = FastAPI()
service = AccountService()


# ---------------- REQUEST MODELS ----------------

class CreateAccountRequest(BaseModel):
    user_id: str


class TransferRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float


# ---------------- ROUTES ----------------

@app.post("/account/create")
def create_account(request: CreateAccountRequest):
    account = service.create_account(request.user_id)
    return account


@app.get("/account/{user_id}")
def get_account(user_id: str):
    account = service.get_account(user_id)
    return account


@app.post("/account/transfer")
def transfer(request: TransferRequest):
    transaction = service.transfer(
        request.sender_id,
        request.receiver_id,
        request.amount
    )
    return transaction