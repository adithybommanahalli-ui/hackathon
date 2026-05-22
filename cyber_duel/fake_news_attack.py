"""
CYBER DUEL — Fake News / Disinformation Attack
Floods NEXUS SHIELD with disinformation topics to max out
the fake news ratio and social panic score.

Usage: python fake_news_attack.py
"""
import requests
import time
from config import NEXUS_API

DISINFO_TOPICS = [
    "government cover up fake news disinformation propaganda lies",
    "false flag operation conspiracy crisis fabricated emergency",
    "media manipulation fake attack staged incident hoax",
    "bot network spreading panic misinformation viral fake",
    "deepfake video politician scandal fabricated evidence",
    "social media manipulation election interference fake accounts",
    "AI generated fake news crisis disinformation campaign",
]

print("╔══════════════════════════════════════════╗")
print("║   CYBER DUEL  —  DISINFORMATION MODULE   ║")
print("║   Flooding fake news + panic signals     ║")
print("╚══════════════════════════════════════════╝\n")

print("[*] Injecting disinformation topics...\n")

for i, topic in enumerate(DISINFO_TOPICS, 1):
    print(f"[{i}/{len(DISINFO_TOPICS)}] \"{topic[:55]}\"")
    try:
        r = requests.post(
            f"{NEXUS_API}/api/social/analyze",
            json={"topic": topic},
            timeout=15,
        )
        d = r.json()
        fn = d["analysis"]["fake_news"]
        s  = d["analysis"]["sentiment"]
        print(f"       📰 Fake: {fn['fake_ratio']*100:.0f}%  "
              f"😡 Angry: {s['angry']*100:.0f}%  "
              f"🤖 Bot: {d['analysis']['bot_activity']*100:.0f}%  "
              f"Crisis: {d['crisis_score']:.1f} → {d['status']}")
    except Exception as e:
        print(f"       [ERROR] {e}")
    time.sleep(0.8)

print("\n[✓] Disinformation attack complete")
r = requests.get(f"{NEXUS_API}/api/status")
d = r.json()
print(f"[✓] Final Status: {d['system_status']} | Crisis: {d['crisis_score']:.1f}/100")
