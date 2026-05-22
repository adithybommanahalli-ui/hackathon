"""
Convergence Engine - Crisis Score Calculator
Combines network threat + social emotion signals into unified NEXUS SCORE
"""
from typing import Dict, Tuple


def calculate_crisis_score(
    network_threat_level: float,
    emotion_anger_level: float,
    fake_news_ratio: float,
) -> Dict:
    """
    Crisis Score Formula:
    crisis_score = (0.40 * network_threat_level +
                    0.35 * emotion_anger_level +
                    0.25 * fake_news_ratio) * 100

    Convergence Alert: network_threat_level > 0.7 AND emotion_anger_level > 0.7
    """
    # Clamp inputs to [0, 1]
    ntl = max(0.0, min(1.0, network_threat_level))
    eal = max(0.0, min(1.0, emotion_anger_level))
    fnr = max(0.0, min(1.0, fake_news_ratio))

    raw_score = (0.40 * ntl + 0.35 * eal + 0.25 * fnr) * 100
    crisis_score = round(min(100.0, max(0.0, raw_score)), 1)

    convergence_alert = ntl > 0.7 and eal > 0.7

    # Determine status
    if crisis_score <= 40:
        status = "SECURE"
        color = "green"
    elif crisis_score <= 70:
        status = "CAUTION"
        color = "yellow"
    else:
        status = "CRITICAL"
        color = "red"

    return {
        "crisis_score": crisis_score,
        "network_threat_level": round(ntl, 3),
        "emotion_anger_level": round(eal, 3),
        "fake_news_ratio": round(fnr, 3),
        "convergence_alert": convergence_alert,
        "status": status,
        "color": color,
        "breakdown": {
            "network_contribution": round(0.40 * ntl * 100, 1),
            "emotion_contribution": round(0.35 * eal * 100, 1),
            "fake_news_contribution": round(0.25 * fnr * 100, 1),
        },
    }


def generate_threat_event(
    source: str,
    event_type: str,
    severity: str,
    description: str,
    score: float,
) -> Dict:
    """Create a standardized threat event for the timeline."""
    import time

    severity_map = {"safe": "green", "warning": "yellow", "attack": "red"}

    return {
        "id": f"{source}_{int(time.time() * 1000)}",
        "timestamp": time.time(),
        "source": source,  # "network" or "social"
        "event_type": event_type,
        "severity": severity,
        "color": severity_map.get(severity, "green"),
        "description": description,
        "score": round(score, 3),
    }
