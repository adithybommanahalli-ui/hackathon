"""
CYBER DUEL — DoS Attacker
Hits NEXUS SHIELD with DoS detection + HTTP flood.
Watch localhost:5173 dashboard go RED instantly.

Usage: python dos_attack.py
"""
import requests
import threading
import time
import random
from config import NEXUS_API

THREADS  = 80
DURATION = 25

print("╔══════════════════════════════════════════╗")
print("║   CYBER DUEL  —  DoS ATTACK MODULE       ║")
print("║   Target: NEXUS SHIELD  →  :5173         ║")
print("╚══════════════════════════════════════════╝\n")

# ── Fire IDS detection (this pushes state to 100% threat) ────────────────────
print("[*] Triggering IDS DoS detection...")
try:
    r = requests.post(f"{NEXUS_API}/api/simulate/dos", timeout=10)
    d = r.json()
    print(f"[!] {d['result']['malicious']}/500 packets → DoS")
    print(f"[!] Crisis Score : {d['crisis_score']:.1f}")
    print(f"[!] Status       : {d['result']['threat_level']*100:.0f}% threat level\n")
except Exception as e:
    print(f"[!] Cannot reach NEXUS SHIELD at {NEXUS_API}: {e}")
    exit(1)

# ── HTTP flood ────────────────────────────────────────────────────────────────
stop = threading.Event()
hits = [0]
lock = threading.Lock()

def flood():
    session = requests.Session()
    while not stop.is_set():
        try:
            session.get(f"{NEXUS_API}/api/status", timeout=0.5)
            with lock:
                hits[0] += 1
        except Exception:
            pass

print(f"[*] Flooding with {THREADS} threads for {DURATION}s...")
print("[*] Open localhost:5173 — watch packet rate spike!\n")

threads = [threading.Thread(target=flood, daemon=True) for _ in range(THREADS)]
for t in threads: t.start()

start = time.time()
while time.time() - start < DURATION:
    elapsed = time.time() - start
    rate = hits[0] / elapsed if elapsed > 0 else 0
    bar  = "█" * min(50, int(rate / 30))
    print(f"\r[FLOOD] {hits[0]:6d} reqs | {rate:6.0f} req/s |{bar:<50}| {DURATION-elapsed:.0f}s", end="")
    time.sleep(0.3)

stop.set()
print(f"\n\n[✓] Sent {hits[0]:,} requests in {DURATION}s")

r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"[✓] Status       : {d['system_status']}")
print(f"[✓] Crisis Score : {d['crisis_score']:.1f}/100")
print(f"[✓] WS Clients   : {d['active_connections']} (dashboard viewers)")
