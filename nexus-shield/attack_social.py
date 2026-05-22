"""
Social Panic Injector — floods social analysis with panic topics
to spike the emotion/anger score and trigger convergence alert.

Usage: python attack_social.py
"""
import requests
import time

TARGET = "http://localhost:8000"

PANIC_TOPICS = [
    "cyberattack emergency critical infrastructure",
    "war crisis panic emergency",
    "hack breach attack government",
    "ransomware hospital shutdown emergency",
    "power grid attack blackout crisis",
]

print("[SOCIAL] Injecting panic topics to spike emotion score...")
print("[SOCIAL] Watch the Social Pulse panel go RED...\n")

for i, topic in enumerate(PANIC_TOPICS):
    print(f"[SOCIAL] Injecting topic {i+1}/{len(PANIC_TOPICS)}: '{topic}'")
    try:
        r = requests.post(
            f"{TARGET}/api/social/analyze",
            json={"topic": topic},
            timeout=10,
        )
        data = r.json()
        sentiment = data["analysis"]["sentiment"]
        print(f"         Angry: {sentiment['angry']*100:.0f}%  "
              f"Fear: {sentiment['fear']*100:.0f}%  "
              f"Crisis: {data['crisis_score']:.1f}  "
              f"Status: {data['status']}")
    except Exception as e:
        print(f"         Error: {e}")
    time.sleep(1)

print("\n[SOCIAL] Done. Check dashboard for emotion spike and possible CONVERGENCE ALERT")
