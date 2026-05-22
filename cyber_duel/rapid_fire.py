"""
CYBER DUEL — Rapid Fire (All Attacks at Once)
Fires ALL attack types simultaneously in parallel threads.
Maximum chaos — guaranteed CRITICAL + CONVERGENCE ALERT.

Usage: python rapid_fire.py
"""
import requests
import threading
import time
from config import NEXUS_API

print("╔══════════════════════════════════════════════════════╗")
print("║   CYBER DUEL  —  RAPID FIRE (ALL ATTACKS)            ║")
print("║   DoS + PortScan + BruteForce + Social + FakeNews    ║")
print("╚══════════════════════════════════════════════════════╝\n")

results = {}

def attack(name, endpoint, payload=None):
    try:
        if payload:
            r = requests.post(f"{NEXUS_API}{endpoint}", json=payload, timeout=15)
        else:
            r = requests.post(f"{NEXUS_API}{endpoint}", timeout=15)
        d = r.json()
        results[name] = d
        score = d.get("crisis_score", "?")
        print(f"  [✓] {name:<20} → Crisis: {score}")
    except Exception as e:
        print(f"  [✗] {name:<20} → Error: {e}")

ATTACKS = [
    ("DoS Attack",       "/api/simulate/dos",      None),
    ("Port Scan",        "/api/simulate/portscan",  None),
    ("Social Panic",     "/api/social/analyze",     {"topic": "cyberattack emergency war crisis hack breach panic"}),
    ("Disinformation",   "/api/social/analyze",     {"topic": "fake news disinformation propaganda conspiracy hoax"}),
    ("Social Anger",     "/api/social/analyze",     {"topic": "government failure attack emergency shutdown anger"}),
]

print("[*] Firing ALL attack vectors simultaneously...\n")

threads = [
    threading.Thread(target=attack, args=(name, ep, payload))
    for name, ep, payload in ATTACKS
]
for t in threads: t.start()
for t in threads: t.join()

print("\n[*] Second salvo in 2s...")
time.sleep(2)

threads2 = [
    threading.Thread(target=attack, args=(name, ep, payload))
    for name, ep, payload in ATTACKS[:2]  # DoS + PortScan again
]
for t in threads2: t.start()
for t in threads2: t.join()

# Final status
print(f"\n{'═'*54}")
time.sleep(1)
r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"\n  Crisis Score  : {d['crisis_score']:.1f} / 100")
print(f"  System Status : {d['system_status']}")
print(f"  WS Clients    : {d['active_connections']}")

if d["system_status"] == "CRITICAL":
    print("\n  ✅ MAXIMUM DAMAGE — localhost:5173 shows:")
    print("     🔴 CRITICAL  |  ⚠️ CONVERGENCE ALERT  |  🔔 BEEP")
else:
    print(f"\n  ⚠  {d['system_status']} — run again for full CRITICAL")

print(f"\n  Reset: python reset.py")
print(f"{'═'*54}\n")
