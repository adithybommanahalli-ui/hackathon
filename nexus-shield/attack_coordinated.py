"""
COORDINATED ATTACK — simultaneous cyber + social attack
This is the money shot for your demo: triggers the red flashing
CONVERGENCE ALERT banner on the dashboard.

Usage: python attack_coordinated.py
"""
import requests
import threading
import time

TARGET = "http://localhost:8000"

def cyber_attack():
    print("[CYBER ] Launching DoS attack...")
    r = requests.post(f"{TARGET}/api/simulate/dos", timeout=10)
    d = r.json()
    print(f"[CYBER ] {d['result']['malicious']}/500 malicious | Score: {d['crisis_score']:.1f}")

def social_attack():
    print("[SOCIAL] Injecting panic sentiment...")
    r = requests.post(
        f"{TARGET}/api/social/analyze",
        json={"topic": "cyberattack emergency war crisis panic hack breach"},
        timeout=10,
    )
    d = r.json()
    s = d["analysis"]["sentiment"]
    print(f"[SOCIAL] Angry: {s['angry']*100:.0f}% Fear: {s['fear']*100:.0f}% | Score: {d['crisis_score']:.1f}")

print("=" * 55)
print("  NEXUS SHIELD — COORDINATED ATTACK DEMO")
print("  Watch for the RED CONVERGENCE ALERT banner!")
print("=" * 55)
print()
print("[ATTACK] Launching simultaneous cyber + social attack...")
print()

# Fire both attacks at the same time
t1 = threading.Thread(target=cyber_attack)
t2 = threading.Thread(target=social_attack)
t1.start()
t2.start()
t1.join()
t2.join()

time.sleep(2)

# Check final state
r = requests.get(f"{TARGET}/api/status")
d = r.json()
print()
print(f"[STATUS] Crisis Score : {d['crisis_score']:.1f}/100")
print(f"[STATUS] System Status: {d['system_status']}")
print()

if d["system_status"] == "CRITICAL":
    print("✅ SUCCESS — Dashboard should show CRITICAL + CONVERGENCE ALERT")
elif d["system_status"] == "CAUTION":
    print("⚠  CAUTION state — run again to push into CRITICAL")
else:
    print("ℹ  Run the social attack again to spike emotion score higher")

print()
print("[ATTACK] To reset dashboard: python -c \"import requests; requests.post('http://localhost:8000/api/reset')\"")
