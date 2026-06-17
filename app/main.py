from fastapi import FastAPI
from pydantic import BaseModel

from app.services.account_service import AccountService
from app.database.db import init_db, SessionLocal
from app.models.account_table import AccountTable
from app.simulator.mesh_simulator import mesh_simulator
from app.services.demo_service import demo_service
from app.services.bridge_service import BridgeService
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import os
bridge_service = BridgeService()
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
service = AccountService()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATE_DIR)
# -----------------------------
# DB SEEDING (RUN ON STARTUP)
# -----------------------------
def seed_users():
    db = SessionLocal()

    users = ["kalyan", "cutie", "rahul", "madhu"]

    for user in users:
        if not user or len(user.strip()) == 0:
            continue  # skip empty names

        existing = db.query(AccountTable).filter(
            AccountTable.user_id == user
        ).first()

        if not existing:
            db.add(AccountTable(user_id=user, balance=1000))

    db.commit()
    db.close()

@app.on_event("startup")
def startup_event():
    global service, bridge_service

    init_db()
    seed_users()

    service = AccountService()
    bridge_service = BridgeService()

# -----------------------------
# REQUEST MODELS
# -----------------------------

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


class DemoPaymentRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float


# -----------------------------
# ACCOUNT APIs
# -----------------------------
#@app.post("/account/deposit")
#def deposit(request: DepositRequest):
#    return service.deposit(request.user_id, request.amount)


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


@app.get("/accounts")
def get_all_accounts():
    return service.get_all_accounts()


@app.get("/transactions")
def get_transactions():
    return service.get_transactions()

@app.post("/reset")
def reset():
    result = service.reset_all()

    # ALSO reset mesh memory
    for device in mesh_simulator.devices:
        device.packets.clear()

    return {
        "message": "System fully reset (DB + Mesh cleared)"
    }

# -----------------------------
# DEMO: OFFLINE PAYMENT
# -----------------------------
@app.post("/demo/send")
def demo_send(request: DemoPaymentRequest):
    packet = demo_service.create_payment_packet(
        sender_id=request.sender_id,
        receiver_id=request.receiver_id,
        amount=request.amount,
    )

    mesh_simulator.inject_packet(packet)

    return {
        "message": "Packet injected into mesh",
        "packet_id": packet.packet_id,
    }
# -----------------------------
# MESH SIMULATION APIs
# -----------------------------
@app.post("/mesh/gossip")
def run_gossip():
    mesh_simulator.gossip_round()
    return {"message": "Gossip round completed"}

@app.get("/mesh/state")
def get_mesh_state():
    return {
        "devices": [
            {
                "device_id": d.device_id,
                "has_internet": d.has_internet,
                "packets": [p.packet_id for p in d.packets]
            }
            for d in mesh_simulator.devices
        ]
    }

@app.post("/mesh/flush")
def flush_bridge():
    results = []

    for device in mesh_simulator.devices:
        if device.has_internet:
            for packet in list(device.packets):  # copy safe iteration
                result = bridge_service.process_bridge_packet(packet)
                results.append(result)

            # clear packets after upload
            device.packets.clear()

    return {
        "message": "Bridge flush completed",
        "results": results
    }


# -----------------------------
# FIXED HOME ROUTE
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Using explicit keyword arguments prevents Starlette/Jinja2 positional signature confusion
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )