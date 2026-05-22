"""
CYBER DUEL — Main Launcher
Interactive menu — choose your attack against NEXUS SHIELD.

Usage: python launch.py
"""
import subprocess
import sys
import os
import requests

def get_status():
    try:
        r = requests.get("http://localhost:8000/api/status", timeout=2)
        d = r.json()
        score  = d.get("crisis_score", 0)
        status = d.get("system_status", "?")
        clients= d.get("active_connections", 0)
        color  = "🔴" if status == "CRITICAL" else "🟡" if status == "CAUTION" else "🟢"
        return f"{color} {status}  |  Score: {score:.1f}/100  |  Dashboard viewers: {clients}"
    except Exception:
        return "⚫ NEXUS SHIELD OFFLINE — start backend first"

MENU = """
╔══════════════════════════════════════════════════════════╗
║          CYBER DUEL — ATTACK LAUNCHER v2.0               ║
║          Target: NEXUS SHIELD  →  localhost:5173         ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   NETWORK ATTACKS                                        ║
║   [1]  DoS Attack          → Flood packets, spike rate   ║
║   [2]  Port Scan           → Sequential port detection   ║
║   [3]  Brute Force         → SSH/RDP credential stuffing ║
║   [4]  Slowloris           → Connection exhaustion       ║
║                                                          ║
║   SOCIAL ATTACKS                                         ║
║   [5]  Social Panic        → Spike anger/fear score      ║
║   [6]  Fake News Flood     → Max out disinformation      ║
║                                                          ║
║   COMBINED ATTACKS                                       ║
║   [7]  Coordinated Attack  → Cyber + Social → CONVERGENCE║
║   [8]  RAPID FIRE 💥       → ALL attacks simultaneously  ║
║                                                          ║
║   CONTROL                                                ║
║   [9]  Reset Dashboard     → Back to green / SECURE      ║
║   [0]  Exit                                              ║
╚══════════════════════════════════════════════════════════╝"""

SCRIPTS = {
    "1": "dos_attack.py",
    "2": "portscan_attack.py",
    "3": "bruteforce_attack.py",
    "4": "slowloris_attack.py",
    "5": "social_attack.py",
    "6": "fake_news_attack.py",
    "7": "coordinated_attack.py",
    "8": "rapid_fire.py",
    "9": "reset.py",
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

while True:
    print(MENU)
    print(f"  NEXUS SHIELD: {get_status()}\n")
    choice = input("  Select attack [0-9]: ").strip()

    if choice == "0":
        print("\n[*] Exiting CYBER DUEL.\n")
        break
    elif choice in SCRIPTS:
        script = SCRIPTS[choice]
        print(f"\n[*] Launching {script}...\n{'─'*58}\n")
        subprocess.run([sys.executable, script])
        print(f"\n{'─'*58}")
        input("\n  Press ENTER to return to menu...")
    else:
        print("  [!] Invalid choice.\n")
