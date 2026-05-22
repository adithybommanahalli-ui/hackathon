"""
DoS Attack Simulator — attacks your own backend to trigger IDS detection
Run this while the dashboard is open to see real alerts fire.

Usage: python attack_dos.py
"""
import requests
import threading
import time
import random

TARGET = "http://localhost:8000"
THREADS = 50
DURATION = 20  # seconds

print(f"[ATTACK] Starting DoS flood against {TARGET}")
print(f"[ATTACK] {THREADS} threads for {DURATION} seconds")
print("[ATTACK] Watch your dashboard go RED...\n")

stop_flag = threading.Event()
hit_count = 0
lock = threading.Lock()

def flood():
    global hit_count
    endpoints = ["/api/status", "/api/status", "/api/status"]
    session = requests.Session()
    while not stop_flag.is_set():
        try:
            ep = random.choice(endpoints)
            session.get(f"{TARGET}{ep}", timeout=1)
            with lock:
                hit_count += 1
        except Exception:
            pass

# Trigger the IDS detection first
print("[ATTACK] Triggering IDS DoS detection...")
try:
    r = requests.post(f"{TARGET}/api/simulate/dos", timeout=5)
    data = r.json()
    print(f"[ATTACK] IDS Result: {data['result']['malicious']}/500 malicious packets")
    print(f"[ATTACK] Crisis Score: {data['crisis_score']}")
    print(f"[ATTACK] Status: {data['message']}\n")
except Exception as e:
    print(f"[ATTACK] Could not reach backend: {e}")
    exit(1)

# Now flood with real HTTP requests
threads = [threading.Thread(target=flood, daemon=True) for _ in range(THREADS)]
for t in threads:
    t.start()

start = time.time()
while time.time() - start < DURATION:
    elapsed = time.time() - start
    rate = hit_count / elapsed if elapsed > 0 else 0
    print(f"\r[ATTACK] Flooding... {hit_count} requests | {rate:.0f} req/s | {DURATION - elapsed:.0f}s left", end="")
    time.sleep(0.5)

stop_flag.set()
print(f"\n\n[ATTACK] Done. Sent {hit_count} requests in {DURATION}s")
print("[ATTACK] Check your dashboard — it should show CRITICAL status")
