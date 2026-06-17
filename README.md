# 💸 UPI Offline Mesh — Demo

A FastAPI-based backend that simulates **offline UPI payments routed through a Bluetooth-style mesh network.** You’re in a basement with zero connectivity. You send your friend ₹500. Your phone encrypts the payment, broadcasts it to nearby phones, and the packet hops device-to-device until *some* phone walks outside, gets 4G, and silently uploads it to this backend. The backend decrypts, deduplicates, and settles.

This repo is the **server side** of that system, plus a software simulator of the mesh so you can demo the whole flow on a single laptop without any real Bluetooth hardware.

---

## Table of Contents

1. [What this demo proves](#what-this-demo-proves)
2. [How to run it](#how-to-run-it)
3. [The demo flow (step by step)](#the-demo-flow-step-by-step)
4. [Architecture](#architecture)
5. [The three hard problems and how they're solved](#the-three-hard-problems-and-how-theyre-solved)
6. [File-by-file walkthrough](#file-by-file-walkthrough)
7. [API reference](#api-reference)
8. [What's NOT real (and what would change for production)](#whats-not-real-and-what-would-change-for-production)
9. [Honest limitations of the concept](#honest-limitations-of-the-concept)

---

## What this demo proves

The system shows three things working end-to-end:

1. **A payment can travel from sender to backend through untrusted intermediaries** without any of them being able to read how much money is being sent, who it is for, or alter the values.
2. **Duplicate packets are handled gracefully.** Because a mesh network floods packets everywhere, the backend will receive the exact same payment multiple times from different path "bridges". The backend ensures exactly-once settlement.
3. **Replay attacks are structurally impossible.** An attacker cannot intercept a valid mesh packet and upload it again later to try to duplicate the money transfer.

---

## How to run it

### 📦 Local Python Setup

* **Prerequisites:** Python 3.10+ and `pip` installed.

Check your installation version:

python --version

Install the project dependencies:

Bash
pip install -r requirements.txt
Run the local server:

Bash
uvicorn app.main:app --reload


🐳 Docker Setup (NEW)
Alternatively, you can run the isolated application container and backend databases using Docker Compose:

Build the system images:

Bash
docker compose build
Run the stack in background mode:

Bash
docker compose up -d
If you ever change your dependencies, run a forced rebuild without cache layers:

Bash
docker compose down
docker compose build --no-cache
docker compose up -d
Check the active running container status:

Bash
docker ps -a
🌐 Open the Web UI Dashboard: Go to your browser and access http://localhost:8000

---

## The Demo Flow (Step-by-Step)

The visual UI dashboard has four actions that walk you through the entire offline payment pipeline. Follow this intended sequence to watch the mesh network operate:

### Step 1 — Compose a Payment
* **Action:** Choose a sender, receiver, amount, and PIN. Then click **"📤 Inject into Mesh"**.
* **What happens under the hood:**
  * The backend system simulates the sender's offline phone environment.
  * It generates a `PaymentInstruction` model populated with a unique cryptographic nonce and timestamp.
  * It encrypts the payload using the server's asymmetric **RSA public key** (utilizing a secure hybrid cipher layer).
  * It seals the encrypted ciphertext string into a `MeshPacket` initialized with a **Time-to-Live (TTL) value of 5**.
  * It passes the compiled packet array directly to `phone-alice` (an offline virtual device instance).
* 👉 *On the UI dashboard, you will see `phone-alice` state change to reflect that it now holds 1 packet.*

---

### Step 2 — Run Gossip Rounds
* **Action:** Click the **"🔄 Run Gossip Round"** button twice.
* **What happens under the hood:**
  * During each round execution loop, every device holding a packet broadcasts it to every other device within "simulated Bluetooth range".
  * The system decrements the internal packet TTL integer by 1 on every single hop to prevent infinite data looping.
  * **Round 1:** The packet propagates outward until every near device holds a copy.
  * **Round 2:** The packet copies persist across the device arrays, but their internal TTL tracker lowers.
* 💡 *In a real-world scenario, this peer-to-peer data swapping would occur organically via Bluetooth Low Energy (BLE) or Wi-Fi Direct as people walk past each other.*

---

### Step 3 — Bridge Node Syncs Online
* **Action:** Click the **"📡 Bridges Upload to Backend"** button.
* **What happens under the hood:**
  * In the default simulation setup, `phone-bridge` is the singular device configured with `hasInternet=true` (simulating a user walking out of the basement and catching a 4G/5G cell signal).
  * The device automatically executes an HTTP `POST` network call, pushing all its collected packet payloads directly to the gateway endpoint: `/api/bridge/ingest`.
  * **The Ingestion Pipeline:**
    1. **Hashing:** The backend creates a unique SHA-256 hash representation of the ciphertext string.
    2. **Idempotency Locking:** The server attempts to claim that specific hash inside the tracking cache.
    3. **Decryption:** If the transaction hash is unique, the server uses its **RSA private key** to reveal the plaintext instructions.
    4. **Freshness Validation:** The pipeline verifies that the `signedAt` creation timestamp falls within a safe 24-hour window.
    5. **Ledger Commit:** The server executes the account debit and credit updates within a single atomic database transaction block.
* 🎉 *Watch the Account Balances table change instantly—money has moved, and a clean new row has populated your Transaction Ledger!*

---

### Step 4 — Demonstrate Idempotency (The Killer Feature)
This stage proves how the system completely eliminates duplicate transaction attempts from multi-path routing floods.

* **Action Execution:**
  1. Click **"Reset System"** to clear the ui.
  2. Click **"Inject into Mesh"** once to create a single payment packet.
  3. Click **"Run Gossip Round"** twice so that all virtual devices hold a copy of the identical transaction packet.
  4. Click **"Bridges Upload to Backend"**.
* **The Result:** Even though multiple devices hold copies of the identical payment data packet, the server processes the payload on the very first upload and gracefully drops all subsequent duplicates. 
* 🛡️ *This guarantees that the recipient is credited exactly once, no matter how many times the packet is copied or uploaded across the network!*


---
```text
## Architecture


┌─────────────────────────────────────────────────────────────────────────┐
│                         SENDER PHONE (Offline)                          │
│  PaymentInstruction { sender, receiver, amount, pinHash, nonce, time }  │
│         │                                                               │
│         ▼ Encrypt with Server's RSA Public Key                          │
│    MeshPacket { packetId, ttl, createdAt, ciphertext }                  │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       │ Bluetooth Gossip Loops
                                       ▼
        ┌─────────┐   Hop   ┌─────────┐   Hop   ┌─────────┐
        │phone-abc│ ──────▶ │phone-xyz│ ──────▶ │phone-brg│ ◀── Walks Outside
        └─────────┘         └─────────┘         └────┬────┘    Gets 4G Signal
                                                     │
                                                     ▼ HTTP POST
┌─────────────────────────────────────────────────────────────────────────┐
│                    FASTAPI PYTHON BACKEND (This Repo)                   │
│                                                                         │
│  /api/bridge/ingest                                                     │
│         │                                                               │
│         ▼                                                               │
│    [1] Hash Ciphertext String via SHA-256                               │
│         │                                                               │
│         ▼                                                               │
│    [2] Idempotency Cache Check (atomic putIfAbsent / SETNX simulation)   │
│         │ ──▶ Duplicates are permanently rejected before any heavy lifting.│
│         ▼                                                               │
│    [3] CryptoService.decrypt(ciphertext)                                │
│         │ ──▶ RSA-OAEP unwraps AES key; AES-GCM decrypts data payload   │
│         │     and verifies the authentication tag (Tampering = Drop).   │
│         ▼                                                               │
│    [4] Freshness Check: Verify timestamp falls within a 24-hour limit   │
│         │                                                               │
│         ▼                                                               │
│    [5] AccountService.settle()                                          │
│               Executing atomic transactional state updates:             │
│               - Debit Sender Balance                                    │
│               - Credit Receiver Balance                                 │
│               - Record New Permanent Ledger Entry Row                   │
└─────────────────────────────────────────────────────────────────────────┘


```
---

## The Three Hard Problems and How They're Solved

### Problem 1: Untrusted Intermediaries
A random stranger's phone is carrying your transaction. How do you stop them from reading your payment details or changing the amount?

* **Solution:** Hybrid Encryption (RSA-OAEP + AES-GCM)
* **The Mechanics:** The sender encrypts the payload with the server's public key. Only the server holds the corresponding private key, meaning intermediate routing devices see nothing but opaque ciphertext strings.
* **Why Hybrid Encryption?** Asymmetric RSA algorithms can only encrypt small sets of data safely (~245 bytes for a 2048-bit key), whereas our transaction payload is a JSON string that could easily exceed that limit. To solve this, we use the industry-standard hybrid pattern:
  1. Generate a fresh, random AES-256 key exclusively for this specific packet.
  2. Encrypt the JSON data payload with AES-256-GCM (highly performant and authenticated).
  3. Encrypt just that unique AES key using the server's asymmetric RSA-OAEP public key.
  4. Concatenate the pieces together: `[256 bytes RSA-encrypted AES key][12 bytes IV][AES ciphertext + 16-byte GCM tag]`.
* **Why GCM specifically?** It provides authenticated encryption. If a malicious node tries to flip a single bit anywhere inside the ciphertext string, the validation check breaks instantly on decryption. The GCM authentication tag will fail to verify, and the backend throws an exception, preventing the server from being tricked into processing tampered data.

📂 *See this layout in action inside `app/services/crypto_service.py`.*

---

### Problem 2: The Duplicate Storm
Three different bridge nodes hold the exact same payment packet. They all walk out of the basement and find a cell signal at the exact same instant. They all hit the `/api/bridge/ingest` endpoint within milliseconds of each other. If the backend naively processed all three requests, the sender would be debited ₹1500 instead of ₹500.

* **Solution:** Atomic Compare-and-Set on the Ciphertext Hash
* **The Mechanics:** The absolute first action the FastAPI server takes upon receiving an incoming packet is compute its unique identifier using `SHA-256(ciphertext)`. It immediately tries to claim that hash marker in memory:


# Thread-safe in-memory check inside app/services/bridge_service.py
if packet_hash in seen_cache:
    return False  # Duplicate detected, reject instantly

seen_cache.add(packet_hash)
return True  # First claimer, allowed to proceed to decryption


Problem 3: Replay Attacks
An adversarial node who captured a valid payment ciphertext string weeks ago attempts to re-send (replay) it to the network whenever convenient to continuously drain a sender's account funds.

Solution: Two-Layer Validation

Layer 1 (Expiration Windows): Embedded deep inside the encrypted JSON block is a signedAt epoch timestamp integer. The FastAPI backend validates this value immediately after decryption and drops any incoming packets carrying a timestamp older than 24 hours. Because this parameter is locked inside the ciphertext, an attacker cannot modify the date string without instantly breaking the outer AES-GCM validation tag.

Layer 2 (Unique Nonces): Inside that same encrypted payload space, the client app generates a completely random cryptographic string unique marker (nonce). Even if a user legitimately decides to pay a restaurant exactly ₹100 twice in a row, their generated nonces will differ. This ensures their ciphertexts differ, meaning their SHA-256 identification hashes differ, allowing both to settle safely. However, an unauthorized replay attempt of a single historic packet string results in a byte-identical ciphertext string, which is caught and blocked at the Step 2 deduplication gate.

📂 See the freshness and timestamp checks inside app/services/bridge_service.py


## Tests

This project includes a high-speed parallel concurrency test suite to prove that the system can handle real-world duplicate storms and race conditions without corrupting data.

The interesting test is `test_parallel.py` — it allocates real hardware processors (OS threads) to fire three duplicate network flushes at your backend simultaneously, asserting that exactly one settles and two are dropped.

### Running the Parallel Concurrency Test

1. Start your FastAPI backend server in your first terminal:
   ```bash
   uvicorn app.main:app --reload
   Open a second terminal window, ensure your virtual environment is active, and run the test file:

  Bash
  pip install requests
  python test_parallel.py
  

## File Structure

```text
app/
├── main.py                  # FastAPI server routers, core engine, and API endpoints
│
├── services/                # Core business logic processing components
│   ├── account_service.py   # Database balances, deposits, and ledger updates
│   ├── demo_service.py      # Creates and signs the encrypted simulation packets
│   ├── bridge_service.py    # Gateway ingestion pipeline, deduplication, and sync controllers
│   └── crypto_service.py    # Symmetric (AES-GCM) and Asymmetric (RSA) security engines
│
├── mesh/                    # Simulated decentralized communication components
│   ├── mesh_simulator.py    # P2P background broadcast loops and device pairing logic
│   ├── mesh_packet.py       # Ciphertext structures, metadata frames, and TTL variables
│   └── virtual_device.py    # State tracking rules for isolated network nodes
│
├── models/                  # Storage system schema maps
│   ├── account_table.py     # High-integrity profile states and core bank logs
│   └── transaction_table.py # Double-entry ledger audit lines
│
├── database/                # Relational data engine initializations
│   └── db.py                # Database engine setup and local file bindings
│
├── templates/               # Visual presentation layers
│   └── index.html           # Full interactive dashboard management workspace
│
└── static/                  # User layout appearance rules
    └── style.css            # Stylesheets


```
---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Opens the dashboard UI. |
| `GET` | `/accounts` | Lists all user accounts. |
| `POST` | `/account/create` | Creates a new user profile. |
| `POST` | `/account/deposit` | Adds money to an account. |
| `POST` | `/account/transfer` | Performs a direct online transfer. |
| `POST` | `/demo/send` | Creates an encrypted offline packet. |
| `POST` | `/mesh/gossip` | Swaps packets between nearby devices. |
| `POST` | `/mesh/flush` | Uploads bridge packets to backend. |
| `POST` | `/reset` | Resets all data to default. |



---

## What is NOT Real

| Component | Simulation Reality |
| :--- | :--- |
| **Mesh Network** | Simulated in code loops (no actual Bluetooth/Wi-Fi hardware used). |
| **Devices** | Virtual Python objects running in host computer memory. |
| **Encryption** | Sandbox-grade hybrid cryptographic layers. |
| **Database** | Lightweight local single-file SQLite database. |
| **Idempotency** | In-memory sets backed by local database tables. |
| **Settlement** | Mocked banking logic loops running on a single local server. |



---

## Honest Limitations of the Concept

This project is a simulation of a **mesh-routed deferred settlement** system. To ensure clarity during reviews, the inherent architectural challenges of entirely offline transaction systems are outlined below:

* **No Offline Fund Verification:** The receiver cannot verify if the sender actually has the funds. When a sender hands a receiver a screen showing "₹500 sent", it is effectively a digital promissory note. If the sender's account is empty when the packet eventually hits the backend, the transaction is **REJECTED**, and the receiver loses the money. Real-world systems like *UPI Lite* bypass this by utilizing pre-funded, hardware-secured local wallets.
* **Offline Double-Spending Risk:** A malicious sender with only ₹500 in their balance could create a payment packet for Bob in one location, walk to another, and create a second packet for Carol. Whichever packet reaches an internet-connected bridge and hits the backend first settles successfully; the second packet is permanently **REJECTED** due to insufficient funds.
* **Real-World Bluetooth Constraints:** Background Bluetooth Low Energy (BLE) operations are heavily throttled on Android, and background peripheral mode is highly restricted on iOS. Reliably forming peer-to-peer mesh connections automatically while devices are in pockets is a massive hardware hurdle. This project skips that layer entirely by simulating the mesh network in memory.
* **Privacy and Metadata Overhead:** Even though routing intermediaries cannot read the encrypted contents of your transaction, the physical data packet still exists on a stranger's device as temporary metadata. A production-grade system requires deep consideration regarding data liability and privacy compliance.
