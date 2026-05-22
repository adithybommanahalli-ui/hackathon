"""
Port Scan Simulator — scans your own backend ports to trigger IDS detection
Run this while the dashboard is open.

Usage: python attack_portscan.py
"""
import socket
import requests
import threading
import time

TARGET_HOST = "127.0.0.1"
TARGET_API  = "http://localhost:8000"
PORT_RANGE  = range(7990, 8020)  # scan around your backend port

print(f"[SCAN] Port scanning {TARGET_HOST} ports {PORT_RANGE.start}-{PORT_RANGE.stop}")
print("[SCAN] Watch your dashboard for PORT SCAN alert...\n")

# Trigger IDS detection
print("[SCAN] Triggering IDS Port Scan detection...")
try:
    r = requests.post(f"{TARGET_API}/api/simulate/portscan", timeout=5)
    data = r.json()
    print(f"[SCAN] IDS Result: {data['result']['malicious']}/500 suspicious packets")
    print(f"[SCAN] Crisis Score: {data['crisis_score']}")
    print(f"[SCAN] Status: {data['message']}\n")
except Exception as e:
    print(f"[SCAN] Could not reach backend: {e}")
    exit(1)

# Real TCP port scan against localhost
open_ports = []
closed_ports = []

def scan_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)
    result = sock.connect_ex((TARGET_HOST, port))
    sock.close()
    if result == 0:
        open_ports.append(port)
        print(f"[SCAN] Port {port}: OPEN ✓")
    else:
        closed_ports.append(port)
        print(f"[SCAN] Port {port}: closed")

threads = []
for port in PORT_RANGE:
    t = threading.Thread(target=scan_port, args=(port,))
    threads.append(t)
    t.start()
    time.sleep(0.05)

for t in threads:
    t.join()

print(f"\n[SCAN] Scan complete.")
print(f"[SCAN] Open ports: {open_ports}")
print(f"[SCAN] Closed ports: {len(closed_ports)}")
print("[SCAN] Check your dashboard — PORT SCAN alert should be active")
