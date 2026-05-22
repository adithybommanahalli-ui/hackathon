"""
CYBER DUEL — Social Panic Injector
Floods NEXUS SHIELD with high-anger topics to spike the
Social Pulse panel and push emotion score into RED.

Usage: python social_attack.py
"""
import requests
import time
from config import NEXUS_API

PANIC_TOPICS = [
    "cyberattack critical infrastructure emergency shutdown",
    "ransomware hospital attack crisis panic",
    "government hack breach emergency response",
    "power grid attack blackout emergency",
    "war cyber espionage attack breach panic",
    "financial system hack crash emergency",
    "disinformation campaign crisis public panic anger",
]

print("╔══════════════════════════════════════════╗")
print("║   CYBER DUEL  —  SOCIAL PANIC MODULE     ║")
print("║   Target: NEXUS SHIELD Social Pulse      ║")
print("╚══════════════════════════════════════════╝\n")

print("[*] Injecting panic topics into NEXUS SHIELD...\n")

for i, topic in enumerate(PANIC_TOPICS, 1):
    print(f"[{i}/{len(PANIC_TOPICS)}] Topic: \"{topic}\"")
    try:
        r = requests.post(
            f"{NEXUS_API}/api/social/analyze",
            json={"topic": topic},
            timeout=15,
        )
        d = r.json()
        s = d["analysis"]["sentiment"]
        fn = d["analysis"]["fake_news"]["fake_ratio"]
        print(f"      😡 Angry: {s['angry']*100:.0f}%  "
              f"😨 Fear: {s['fear']*100:.0f}%  "
              f"📰 Fake: {fn*100:.0f}%  "
              f"🔴 Crisis: {d['crisis_score']:.1f}  "
              f"→ {d['status']}")
    except Exception as e:
        print(f"      [ERROR] {e}")
    time.sleep(1.2)

print("\n[✓] Social attack complete")
r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"[✓] Final Status     : {d['system_status']}")
print(f"[✓] Final Crisis Score: {d['crisis_score']:.1f}/100")
