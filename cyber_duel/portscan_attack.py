"""
CYBER DUEL — Port Scan Attacker
Scans ports on localhost AND triggers IDS port scan detection.
Watch the dashboard show PORT SCAN badge and orange alert.

Usage: python portscan_attack.py
"""
import socket
import requests
import threading
import time
from config import NEXUS_API

TARGET_HOST = "127.0.0.1"
SCAN_PORTS  = list(range(7900, 8100))   # 200 ports around the backend

print("╔══════════════════════════════════════════╗")
print("║   CYBER DUEL  —  PORT SCAN MODULE        ║")
print("║   Target: NEXUS SHIELD                   ║")
print("╚══════════════════════════════════════════╝\n")

# ── Step 1: Trigger IDS model ─────────────────────────────────────────────────
print("[*] Triggering IDS Port Scan detection on NEXUS SHIELD...")
try:
    r = requests.post(f"{NEXUS_API}/api/simulate/portscan", timeout=10)
    d = r.json()
    print(f"[!] IDS fired: {d['result']['malicious']}/500 packets flagged as PortScan")
    print(f"[!] Crisis Score: {d['crisis_score']:.1f}")
    print(f"[!] {d['message']}\n")
except Exception as e:
    print(f"[!] Cannot reach NEXUS SHIELD: {e}")
    exit(1)

# ── Step 2: Real TCP port scan ────────────────────────────────────────────────
open_ports   = []
closed_ports = []
lock         = threading.Lock()

def scan(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.25)
    result = s.connect_ex((TARGET_HOST, port))
    s.close()
    with lock:
        if result == 0:
            open_ports.append(port)
        else:
            closed_ports.append(port)

print(f"[*] Scanning {len(SCAN_PORTS)} ports on {TARGET_HOST}...")
threads = []
for port in SCAN_PORTS:
    t = threading.Thread(target=scan, args=(port,), daemon=True)
    threads.append(t)
    t.start()
    time.sleep(0.01)   # slight delay = realistic scan pattern

for t in threads:
    t.join()

print(f"\n[✓] Scan complete")
print(f"[✓] Open ports  : {open_ports}")
print(f"[✓] Closed ports: {len(closed_ports)}")

# ── Step 3: Status ────────────────────────────────────────────────────────────
r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"\n[✓] NEXUS SHIELD Status : {d['system_status']}")
print(f"[✓] Crisis Score        : {d['crisis_score']:.1f}/100")
