💸 Offline UPI Mesh — Python FastAPI Demo

A FastAPI-based backend that simulates offline UPI payments over a mesh network.

You’re in a basement with no internet. You send ₹500 to a friend. Your phone encrypts the transaction, broadcasts it through nearby devices, and the packet hops device-to-device until one device gets internet and syncs it to this backend.

The backend decrypts the packet, ensures idempotency, and settles the payment exactly once.

This repo is the Python version of a distributed offline payment system, including a full mesh network simulator + banking backend + UI dashboard.

📌 Table of Contents
What this demo proves
How to run it
The demo flow (step by step)
Architecture
The three hard problems solved
File-by-file walkthrough
API reference
What is NOT real
Limitations
🚀 What this demo proves

This system demonstrates:

1. Offline payment can move securely through untrusted devices
Payload is encrypted using AES + RSA hybrid encryption
Intermediary phones cannot read or modify data
2. Duplicate packets are safely handled
Even if multiple devices upload the same payment
Backend ensures exactly-once settlement
3. Replay attacks are rejected
Old or reused packets cannot be reprocessed
⚙️ How to run it
📦 Prerequisites
Python 3.10+
pip installed

Check:

python --version
▶️ Install dependencies
pip install -r requirements.txt
🚀 Run server
uvicorn app.main:app --reload

🐳 Containerization (Docker)
Alternatively, you can run the entire environment (FastAPI application + Database services) isolated inside Docker containers using Docker Compose.

1. Spin up the containers in detached mode:
docker compose up -d

2. If you update packages in requirements.txt, force a clean rebuild bypassing the cache:
docker compose down
docker compose build --no-cache
docker compose up -d

3. Verify the container status:
docker ps -a

🌐 Open UI
http://localhost:8000
🔄 Demo flow (step by step)

The UI has three main stages:

Step 1 — Inject payment
User enters sender, receiver, amount
Backend creates encrypted payment packet
Packet is injected into first mesh device

👉 No money is deducted yet

Step 2 — Gossip network
Devices randomly share packets with neighbors
Packet spreads across mesh network
TTL decreases per hop

👉 Still no money movement

Step 3 — Bridge sync
Devices with internet upload packets
Backend decrypts payload
Transaction is validated and settled

👉 REAL MONEY UPDATE happens here

🧠 Architecture
SENDER
  │
  │ encrypt (AES + RSA)
  ▼
Mesh Packet (ciphertext)
  │
  ▼
[ phone-alice ] → [ phone-bob ] → [ phone-charlie ]
         │
         ▼
   phone-bridge (internet)
         │
         ▼
FastAPI Backend
   ├── decrypt packet
   ├── idempotency check
   ├── account validation
   ├── transaction settlement
   └── DB update
🧩 The three hard problems solved
Problem 1: Secure transmission through strangers
Solution:

Hybrid encryption:

AES-256 encrypts payload
RSA encrypts AES key
AES-GCM ensures tamper detection

👉 Nobody in the mesh can read or modify data

Problem 2: Duplicate packet storms
Problem:

Same packet reaches backend multiple times from different devices

Solution:
Idempotency using transaction_id set
Only first packet is processed

👉 Ensures exactly-once settlement

Problem 3: Replay attacks
Problem:

Old packets can be resent later

Solution:
Each packet has nonce + timestamp
Backend rejects stale or duplicate packets
📁 File structure
app/
│
├── main.py                  # FastAPI entrypoint + APIs
├── services/
│   ├── account_service.py   # Banking logic (deposit, transfer, reset)
│   ├── demo_service.py      # Creates encrypted payment packets
│   ├── bridge_service.py    # Decrypt + settle logic
│   └── crypto_service.py    # AES + RSA encryption layer
│
├── mesh/
│   ├── mesh_simulator.py    # Gossip network simulation
│   ├── mesh_packet.py       # Packet structure
│   └── virtual_device.py    # Simulated phones
│
├── models/
│   ├── account_table.py     # DB model
│   └── transaction_table.py # Ledger
│
├── database/
│   └── db.py                # SQLite + Session setup
│
├── templates/
│   └── index.html           # UI dashboard
│
└── static/
    └── style.css            # UI styling
🌐 API reference
Method	Endpoint	Description
GET	/	UI dashboard
GET	/accounts	List all users
POST	/account/create	Create user
POST	/account/deposit	Add money
POST	/account/transfer	Direct transfer
POST	/demo/send	Inject offline packet
POST	/mesh/gossip	Spread packets
POST	/mesh/flush	Sync to backend
POST	/reset	Reset system
⚠️ What is NOT real

This is a simulation project, not production UPI.

Component	Reality
Mesh network	Simulated (no Bluetooth)
Devices	Virtual Python objects
Encryption	Demo-grade hybrid crypto
Database	SQLite
Idempotency	In-memory + DB
Settlement	Local backend logic
🚧 Limitations
No real offline Bluetooth communication
No real bank integration
No authentication system (PIN not included)
Mesh is fully simulated in memory
No mobile app (yet)
💡 Key insight

This system demonstrates:

“How offline payments could work using opportunistic mesh networking + delayed settlement”

🏁 Final takeaway

This project shows:

Distributed systems thinking
Encryption design
Idempotent backend design
Eventual consistency model
Real-world fintech architecture simulation