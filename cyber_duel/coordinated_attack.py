"""
CYBER DUEL — COORDINATED ATTACK (THE MONEY SHOT)
Fires DoS + Social Panic simultaneously across 3 waves.
Triggers the ⚠️ CONVERGENCE ALERT banner on NEXUS SHIELD.

Usage: python coordinated_attack.py
"""
import requests
import threading
import time
from config import NEXUS_API

print("╔══════════════════════════════════════════════════════╗")
print("║   CYBER DUEL  —  COORDINATED ATTACK                  ║")
print("║   Target: NEXUS SHIELD  →  localhost:5173            ║")
print("╚══════════════════════════════════════════════════════╝\n")

def cyber_strike(wave):
    print(f"[CYBER  W{wave}] ► Launching DoS attack...")
    try:
        r = requests.post(f"{NEXUS_API}/api/simulate/dos", timeout=15)
        d = r.json()
        print(f"[CYBER  W{wave}] ✓ {d['result']['malicious']}/500 malicious | Crisis: {d['crisis_score']:.1f} | {d['result']['threat_level']*100:.0f}% threat")
    except Exception as e:
        print(f"[CYBER  W{wave}] ✗ {e}")

def portscan_strike(wave):
    print(f"[SCAN   W{wave}] ► Launching Port Scan...")
    try:
        r = requests.post(f"{NEXUS_API}/api/simulate/portscan", timeout=15)
        d = r.json()
        print(f"[SCAN   W{wave}] ✓ {d['result']['malicious']}/500 flagged | Crisis: {d['crisis_score']:.1f}")
    except Exception as e:
        print(f"[SCAN   W{wave}] ✗ {e}")

def social_strike(wave, topic):
    print(f"[SOCIAL W{wave}] ► Injecting: '{topic[:50]}'")
    try:
        r = requests.post(
            f"{NEXUS_API}/api/social/analyze",
            json={"topic": topic},
            timeout=15,
        )
        d = r.json()
        s = d["analysis"]["sentiment"]
        print(f"[SOCIAL W{wave}] ✓ Angry:{s['angry']*100:.0f}% Fear:{s['fear']*100:.0f}% Fake:{d['analysis']['fake_news']['fake_ratio']*100:.0f}% | Crisis: {d['crisis_score']:.1f}")
    except Exception as e:
        print(f"[SOCIAL W{wave}] ✗ {e}")

SOCIAL_TOPICS = [
    "cyberattack emergency critical infrastructure shutdown hack breach",
    "ransomware hospital attack crisis panic government failure",
    "war cyber espionage attack breach panic disinformation",
]

# ── 3 waves of simultaneous attacks ──────────────────────────────────────────
for wave in range(1, 4):
    print(f"\n{'─'*54}")
    print(f"  WAVE {wave}/3 — Simultaneous cyber + social strike")
    print(f"{'─'*54}")

    threads = [
        threading.Thread(target=cyber_strike,   args=(wave,)),
        threading.Thread(target=social_strike,  args=(wave, SOCIAL_TOPICS[wave-1])),
    ]
    if wave == 2:
        threads.append(threading.Thread(target=portscan_strike, args=(wave,)))

    for t in threads: t.start()
    for t in threads: t.join()

    # Check status after each wave
    try:
        r = requests.get(f"{NEXUS_API}/api/status")
        d = r.json()
        print(f"\n  → Status: {d['system_status']}  |  Crisis: {d['crisis_score']:.1f}/100")
        if d["system_status"] == "CRITICAL":
            print("  ✅ CRITICAL reached — dashboard should show CONVERGENCE ALERT!")
            break
    except Exception:
        pass

    if wave < 3:
        print(f"\n  [*] Waiting 2s before next wave...")
        time.sleep(2)

# ── Final report ──────────────────────────────────────────────────────────────
print(f"\n{'═'*54}")
time.sleep(1)
try:
    r = requests.get(f"{NEXUS_API}/api/status")
    d = r.json()
    print(f"\n  FINAL RESULT")
    print(f"  Crisis Score  : {d['crisis_score']:.1f} / 100")
    print(f"  System Status : {d['system_status']}")
    print(f"  WS Clients    : {d['active_connections']} (dashboard viewers)")
    print()
    if d["system_status"] == "CRITICAL":
        print("  ✅ SUCCESS — Check localhost:5173 for:")
        print("     🔴 CRITICAL gauge (red)")
        print("     ⚠️  CONVERGENCE ALERT flashing banner")
        print("     🔔 Beep sound + popup notification")
        print("     📈 Packet rate spiked in network panel")
    else:
        print(f"  ⚠  Status is {d['system_status']} — run again to push higher")
except Exception as e:
    print(f"  Error checking status: {e}")

print(f"\n  To reset: python reset.py")
print(f"{'═'*54}\n")
