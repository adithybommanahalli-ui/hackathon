"""
CYBER DUEL — Brute Force Attacker
Simulates credential stuffing on SSH/RDP ports.
Watch NEXUS SHIELD detect repeated auth attempts.

Usage: python bruteforce_attack.py
"""
import requests
import threading
import time
import random
from config import NEXUS_API

THREADS  = 60
DURATION = 20

print("╔══════════════════════════════════════════╗")
print("║   CYBER DUEL  —  BRUTE FORCE MODULE      ║")
print("║   Simulating SSH/RDP credential stuffing ║")
print("╚══════════════════════════════════════════╝\n")

PASSWORDS = ["admin","password","123456","root","letmein","qwerty","abc123","monkey","master","dragon"]
USERNAMES = ["admin","root","user","administrator","test","guest","ubuntu","pi"]
PORTS     = [22, 3389, 21, 23, 5900]

print("[*] Triggering IDS Brute Force detection...")
try:
    # Use portscan endpoint — same repeated-port pattern as bruteforce
    r = requests.post(f"{NEXUS_API}/api/simulate/portscan", timeout=10)
    d = r.json()
    print(f"[!] IDS fired: {d['result']['malicious']}/500 flagged")
    print(f"[!] Crisis Score: {d['crisis_score']:.1f}\n")
except Exception as e:
    print(f"[!] Cannot reach NEXUS SHIELD: {e}"); exit(1)

# Simulate brute force HTTP requests
stop = threading.Event()
attempts = [0]
lock = threading.Lock()

def brute_worker():
    session = requests.Session()
    while not stop.is_set():
        try:
            user = random.choice(USERNAMES)
            pwd  = random.choice(PASSWORDS)
            port = random.choice(PORTS)
            # Hit the backend repeatedly (simulates auth flood)
            session.get(f"{NEXUS_API}/api/status", timeout=0.5,
                        headers={"X-Brute-User": user, "X-Brute-Port": str(port)})
            with lock:
                attempts[0] += 1
        except Exception:
            pass

print(f"[*] Launching brute force — {THREADS} threads, {DURATION}s")
print(f"[*] Targeting ports: {PORTS}\n")

threads = [threading.Thread(target=brute_worker, daemon=True) for _ in range(THREADS)]
for t in threads: t.start()

start = time.time()
while time.time() - start < DURATION:
    elapsed = time.time() - start
    rate = attempts[0] / elapsed if elapsed > 0 else 0
    print(f"\r[BRUTE] {attempts[0]:6d} attempts | {rate:5.0f}/s | {DURATION-elapsed:.0f}s left", end="")
    time.sleep(0.3)

stop.set()
print(f"\n\n[✓] {attempts[0]:,} brute force attempts sent")

r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"[✓] Status: {d['system_status']} | Crisis: {d['crisis_score']:.1f}/100")
