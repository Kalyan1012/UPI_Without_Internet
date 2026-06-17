import requests
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:8000"

def fire_flush():
    """Simulates a bridge phone waking up and flushing its mesh data to the backend"""
    try:
        response = requests.post(f"{BASE_URL}/mesh/flush")
        return response.status_code
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_true_parallel_flush_storm():
    print("\n[1/4] Resetting system state to defaults...")
    requests.post(f"{BASE_URL}/reset")

    print("[2/4] Injecting offline payment from kalyan to cutie (₹500)...")
    # Using your actual database users so the transaction can legally process!
    setup_res = requests.post(f"{BASE_URL}/demo/send", json={
        "sender_id": "kalyan",
        "receiver_id": "cutie",
        "amount": 500
    })
    
    print("      Flooding the mesh via gossip rounds...")
    requests.post(f"{BASE_URL}/mesh/gossip")
    requests.post(f"{BASE_URL}/mesh/gossip")

    print("[3/4] Attacking backend with 3 parallel OS threads flushing data at once...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fire_flush) for _ in range(3)]
        statuses = [future.result() for future in futures]

    print(f"Server response statuses from the storm: {statuses}")
    
    print("[4/4] Verifying Balance Sheet against Double-Spending...")
    acc_res = requests.get(f"{BASE_URL}/accounts")
    print(f"Final Balance Sheet: {acc_res.text}")
    
    # Let's inspect if your system has absolute transaction protection
    if "kalyan" in acc_res.text:
        balances = acc_res.json()
        kalyan_balance = next(u["balance"] for u in balances if u["user_id"] == "kalyan")
        cutie_balance = next(u["balance"] for u in balances if u["user_id"] == "cutie")
        
        print(f"\n📊 RESULTS ANALYSIS:")
        print(f"kalyan's Balance: ₹{kalyan_balance}")
        print(f"cutie's Balance:  ₹{cutie_balance}")
        
        if kalyan_balance == 500.0 and cutie_balance == 1500.0:
            print("🏆 PERFECT PASS! Money moved exactly once. Deduplication worked flawlessly under parallel load!")
        elif kalyan_balance < 500.0:
            print("❌ FAILURE: The duplicate storm bypassed your cache and debited kalyan multiple times!")
        else:
            print("⚠️ NOTE: Money did not move. Check if your backend requires running a /mesh/flush or manually triggering ingestion.")

if __name__ == "__main__":
    test_true_parallel_flush_storm()