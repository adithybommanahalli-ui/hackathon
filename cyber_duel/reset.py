"""
CYBER DUEL — Reset NEXUS SHIELD back to green/SECURE state.
Usage: python reset.py
"""
import requests
from config import NEXUS_API

print("[*] Resetting NEXUS SHIELD to baseline...")
r = requests.post(f"{NEXUS_API}/api/reset", timeout=5)
d = r.json()
print(f"[✓] {d['message']}")

r2 = requests.get(f"{NEXUS_API}/api/status")
d2 = r2.json()
print(f"[✓] Status: {d2['system_status']} | Crisis Score: {d2['crisis_score']:.1f}")
