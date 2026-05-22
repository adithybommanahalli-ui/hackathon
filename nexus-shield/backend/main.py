"""
NEXUS SHIELD — FastAPI Backend
Real-Time Cybersecurity & Social Intelligence Platform
"""
import asyncio
import json
import os
import random
import time
from typing import Dict, List, Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Import engines ───────────────────────────────────────────────────────────
from models.ids_engine import IDSEngine
from models.emotion_engine import EmotionEngine
from models.convergence_engine import calculate_crisis_score, generate_threat_event

# ─── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NEXUS SHIELD API",
    description="Real-Time Cybersecurity & Social Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Engine singletons ────────────────────────────────────────────────────────
ids_engine = IDSEngine()
emotion_engine = EmotionEngine()

# ─── Global state ─────────────────────────────────────────────────────────────
class AppState:
    def __init__(self):
        self.network_threat_level: float = 0.05
        self.emotion_anger_level: float = 0.15
        self.fake_news_ratio: float = 0.10
        self.packet_counter = {"total": 0, "malicious": 0, "safe": 0}
        self.recent_events: List[Dict] = []
        self.recent_packets: List[Dict] = []
        self.recent_social: List[Dict] = []
        self.current_topic: str = "cybersecurity"
        self.demo_mode: bool = False
        self.packet_rate_history: List[float] = [random.uniform(30, 80) for _ in range(20)]
        self.active_attack: Optional[str] = None
        self.attack_decay_counter: int = 0

    def add_event(self, event: Dict):
        self.recent_events.insert(0, event)
        self.recent_events = self.recent_events[:50]  # keep last 50

    def tick_packet_rate(self):
        if self.active_attack == "dos":
            rate = random.uniform(7000, 12000)
        elif self.active_attack == "portscan":
            rate = random.uniform(150, 400)
        else:
            rate = random.uniform(30, 120)
        self.packet_rate_history.append(rate)
        self.packet_rate_history = self.packet_rate_history[-60:]  # last 60 ticks
        return rate


state = AppState()

# ─── WebSocket connection manager ─────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, data: Dict):
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


# ─── Background task: push live data every 3 seconds ─────────────────────────
async def live_data_broadcaster():
    """Continuously push threat data to all connected WebSocket clients."""
    while True:
        await asyncio.sleep(3)   # was 10 — now 3s for snappy updates
        try:
            # Decay attack state slowly
            if state.active_attack and state.attack_decay_counter > 0:
                state.attack_decay_counter -= 1
                if state.attack_decay_counter == 0:
                    state.active_attack = None
                    # Slow decay — keep threat visible for a while
                    state.network_threat_level = max(0.05, state.network_threat_level * 0.6)

            # Demo mode: randomly shift values
            if state.demo_mode:
                _apply_demo_drift()

            # Generate benign background traffic
            if not state.active_attack:
                features = ids_engine.generate_benign_features(20)
                result = ids_engine.analyze_batch(features)
                if "error" not in result:
                    state.packet_counter["total"] += result["total_packets"]
                    state.packet_counter["safe"] += result["safe"]
                    state.network_threat_level = max(
                        0.02, state.network_threat_level * 0.85 + result["threat_level"] * 0.15
                    )

            rate = state.tick_packet_rate()

            # Crisis score
            crisis = calculate_crisis_score(
                state.network_threat_level,
                state.emotion_anger_level,
                state.fake_news_ratio,
            )

            # Build payload
            payload = {
                "type": "live_update",
                "timestamp": time.time(),
                "network_score": round(state.network_threat_level * 100, 1),
                "emotion_score": round(state.emotion_anger_level * 100, 1),
                "crisis_score": crisis["crisis_score"],
                "status": crisis["status"],
                "convergence_alert": crisis["convergence_alert"],
                "packet_counter": state.packet_counter,
                "packet_rate": round(rate, 1),
                "packet_rate_history": state.packet_rate_history[-30:],
                "active_attack": state.active_attack,
                "recent_events": state.recent_events[:10],
                "recent_social": state.recent_social[:5],
                "emotion_breakdown": {
                    "angry": round(state.emotion_anger_level * 0.6, 3),
                    "fear": round(state.emotion_anger_level * 0.4, 3),
                    "neutral": round(max(0, 0.5 - state.emotion_anger_level * 0.3), 3),
                    "positive": round(max(0, 0.3 - state.emotion_anger_level * 0.2), 3),
                },
                "fake_news_ratio": state.fake_news_ratio,
                "bot_activity": round(random.uniform(0.05, 0.25 + state.emotion_anger_level * 0.3), 3),
            }

            await manager.broadcast(payload)

        except Exception as e:
            print(f"[WS Broadcaster] Error: {e}")


def _apply_demo_drift():
    """Randomly shift state values for demo mode."""
    # Occasionally trigger random events
    roll = random.random()
    if roll < 0.15:
        # Spike network threat
        state.network_threat_level = min(1.0, state.network_threat_level + random.uniform(0.2, 0.5))
        state.active_attack = random.choice(["dos", "portscan", "bruteforce"])
        state.attack_decay_counter = random.randint(2, 5)
        event = generate_threat_event(
            "network", state.active_attack.upper(), "attack",
            f"Demo: {state.active_attack.upper()} attack detected",
            state.network_threat_level,
        )
        state.add_event(event)
    elif roll < 0.30:
        # Spike social anger
        state.emotion_anger_level = min(1.0, state.emotion_anger_level + random.uniform(0.15, 0.35))
        event = generate_threat_event(
            "social", "SENTIMENT_SPIKE", "warning",
            "Demo: Public anger surge detected",
            state.emotion_anger_level,
        )
        state.add_event(event)
    else:
        # Gradual decay toward baseline
        state.network_threat_level = max(0.05, state.network_threat_level * 0.92)
        state.emotion_anger_level = max(0.10, state.emotion_anger_level * 0.95)
        state.fake_news_ratio = max(0.05, state.fake_news_ratio * 0.97)


# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(live_data_broadcaster())
    print("[NEXUS SHIELD] Backend started. WebSocket broadcaster running.")


# ─── WebSocket endpoint ───────────────────────────────────────────────────────
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state immediately on connect
        crisis = calculate_crisis_score(
            state.network_threat_level,
            state.emotion_anger_level,
            state.fake_news_ratio,
        )
        await websocket.send_json({
            "type": "initial_state",
            "timestamp": time.time(),
            "network_score": round(state.network_threat_level * 100, 1),
            "emotion_score": round(state.emotion_anger_level * 100, 1),
            "crisis_score": crisis["crisis_score"],
            "status": crisis["status"],
            "convergence_alert": crisis["convergence_alert"],
            "packet_counter": state.packet_counter,
            "packet_rate": state.packet_rate_history[-1] if state.packet_rate_history else 50,
            "packet_rate_history": state.packet_rate_history[-30:],
            "active_attack": state.active_attack,
            "recent_events": state.recent_events[:10],
            "recent_social": state.recent_social[:5],
            "emotion_breakdown": {
                "angry": round(state.emotion_anger_level * 0.6, 3),
                "fear": round(state.emotion_anger_level * 0.4, 3),
                "neutral": 0.45,
                "positive": 0.25,
            },
            "fake_news_ratio": state.fake_news_ratio,
            "bot_activity": 0.12,
        })

        # Keep connection alive, listen for client messages
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "set_topic":
                state.current_topic = msg.get("topic", "cybersecurity")
            elif msg.get("type") == "set_demo":
                state.demo_mode = msg.get("enabled", False)
            elif msg.get("type") == "reset":
                _reset_state()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket)


def _reset_state():
    state.network_threat_level = 0.05
    state.emotion_anger_level = 0.15
    state.fake_news_ratio = 0.10
    state.packet_counter = {"total": 0, "malicious": 0, "safe": 0}
    state.recent_events.clear()
    state.recent_social.clear()
    state.active_attack = None
    state.attack_decay_counter = 0
    state.packet_rate_history = [random.uniform(30, 80) for _ in range(20)]


# ─── REST Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/status")
async def get_status():
    """System health check."""
    model_loaded = ids_engine.model is not None
    crisis = calculate_crisis_score(
        state.network_threat_level,
        state.emotion_anger_level,
        state.fake_news_ratio,
    )
    return {
        "status": "online",
        "model_loaded": model_loaded,
        "demo_mode": state.demo_mode,
        "crisis_score": crisis["crisis_score"],
        "system_status": crisis["status"],
        "active_connections": len(manager.active_connections),
        "uptime": time.time(),
    }


@app.post("/api/simulate/dos")
async def simulate_dos():
    """Simulate a DoS attack through the IDS model."""
    print("[API] DoS simulation triggered")

    features = ids_engine.generate_dos_features(500)
    result = ids_engine.analyze_batch(features)

    if "error" in result:
        return {"success": False, "error": result["error"]}

    # Update global state — force to maximum threat
    state.network_threat_level = 1.0   # full red immediately
    state.active_attack = "dos"
    state.attack_decay_counter = 20    # stays red for ~60s (20 × 3s ticks)

    state.packet_counter["total"] += result["total_packets"]
    state.packet_counter["malicious"] += result["malicious"]
    state.packet_counter["safe"] += result["safe"]

    # Add to packet rate history (spike)
    for _ in range(5):
        state.packet_rate_history.append(random.uniform(8000, 12000))
    state.packet_rate_history = state.packet_rate_history[-60:]

    event = generate_threat_event(
        "network", "DoS", "attack",
        f"DoS Attack: {result['malicious']}/{result['total_packets']} malicious packets detected",
        state.network_threat_level,
    )
    state.add_event(event)

    # Broadcast immediately
    crisis = calculate_crisis_score(
        state.network_threat_level,
        state.emotion_anger_level,
        state.fake_news_ratio,
    )
    await manager.broadcast({
        "type": "attack_detected",
        "attack_type": "DoS",
        "timestamp": time.time(),
        "network_score": round(state.network_threat_level * 100, 1),
        "crisis_score": crisis["crisis_score"],
        "status": crisis["status"],
        "convergence_alert": crisis["convergence_alert"],
        "packet_counter": state.packet_counter,
        "packet_rate": random.uniform(9000, 12000),
        "packet_rate_history": state.packet_rate_history[-30:],
        "active_attack": "dos",
        "recent_events": state.recent_events[:10],
        "recent_social": state.recent_social[:5],
        "emotion_breakdown": {
            "angry": round(state.emotion_anger_level * 0.6, 3),
            "fear": round(state.emotion_anger_level * 0.4, 3),
            "neutral": round(max(0, 0.5 - state.emotion_anger_level * 0.3), 3),
            "positive": round(max(0, 0.3 - state.emotion_anger_level * 0.2), 3),
        },
        "fake_news_ratio": state.fake_news_ratio,
        "bot_activity": round(random.uniform(0.1, 0.3), 3),
    })

    return {
        "success": True,
        "attack_type": "DoS",
        "result": result,
        "threat_level": state.network_threat_level,
        "crisis_score": crisis["crisis_score"],
        "message": f"DoS simulation complete: {result['malicious']} malicious packets detected",
    }


@app.post("/api/simulate/portscan")
async def simulate_portscan():
    """Simulate a Port Scan attack through the IDS model."""
    print("[API] Port Scan simulation triggered")

    features = ids_engine.generate_portscan_features(500)
    result = ids_engine.analyze_batch(features)

    if "error" in result:
        return {"success": False, "error": result["error"]}

    state.network_threat_level = 1.0   # full red immediately
    state.active_attack = "portscan"
    state.attack_decay_counter = 18    # stays visible for ~54s

    state.packet_counter["total"] += result["total_packets"]
    state.packet_counter["malicious"] += result["malicious"]
    state.packet_counter["safe"] += result["safe"]

    for _ in range(5):
        state.packet_rate_history.append(random.uniform(200, 450))
    state.packet_rate_history = state.packet_rate_history[-60:]

    event = generate_threat_event(
        "network", "PortScan", "attack",
        f"Port Scan: {result['malicious']}/{result['total_packets']} suspicious packets",
        state.network_threat_level,
    )
    state.add_event(event)

    crisis = calculate_crisis_score(
        state.network_threat_level,
        state.emotion_anger_level,
        state.fake_news_ratio,
    )
    await manager.broadcast({
        "type": "attack_detected",
        "attack_type": "PortScan",
        "timestamp": time.time(),
        "network_score": round(state.network_threat_level * 100, 1),
        "crisis_score": crisis["crisis_score"],
        "status": crisis["status"],
        "convergence_alert": crisis["convergence_alert"],
        "packet_counter": state.packet_counter,
        "packet_rate": random.uniform(200, 450),
        "packet_rate_history": state.packet_rate_history[-30:],
        "active_attack": "portscan",
        "recent_events": state.recent_events[:10],
        "recent_social": state.recent_social[:5],
        "emotion_breakdown": {
            "angry": round(state.emotion_anger_level * 0.6, 3),
            "fear": round(state.emotion_anger_level * 0.4, 3),
            "neutral": round(max(0, 0.5 - state.emotion_anger_level * 0.3), 3),
            "positive": round(max(0, 0.3 - state.emotion_anger_level * 0.2), 3),
        },
        "fake_news_ratio": state.fake_news_ratio,
        "bot_activity": round(random.uniform(0.1, 0.3), 3),
    })

    return {
        "success": True,
        "attack_type": "PortScan",
        "result": result,
        "threat_level": state.network_threat_level,
        "crisis_score": crisis["crisis_score"],
        "message": f"Port Scan simulation: {result['malicious']} suspicious packets detected",
    }


class SocialAnalyzeRequest(BaseModel):
    topic: str


@app.post("/api/social/analyze")
async def analyze_social(request: SocialAnalyzeRequest):
    """Analyze social sentiment for a given topic."""
    print(f"[API] Social analysis for topic: {request.topic}")

    state.current_topic = request.topic
    analysis = emotion_engine.analyze(request.topic)

    # Update global state — use max to never let it drop on repeated calls
    state.emotion_anger_level = min(1.0, max(state.emotion_anger_level, analysis["emotion_anger_level"] * 1.4))
    state.fake_news_ratio = min(1.0, analysis["fake_news"]["fake_ratio"] * 1.3)

    # Add social events to feed
    for headline in analysis["headlines"][:3]:
        event = generate_threat_event(
            "social", "HEADLINE", 
            "warning" if state.emotion_anger_level > 0.5 else "safe",
            headline[:100],
            state.emotion_anger_level,
        )
        state.add_event(event)

    state.recent_social = [
        {"text": h[:100], "timestamp": time.time()} for h in analysis["headlines"]
    ]

    crisis = calculate_crisis_score(
        state.network_threat_level,
        state.emotion_anger_level,
        state.fake_news_ratio,
    )

    # Broadcast update
    await manager.broadcast({
        "type": "social_update",
        "timestamp": time.time(),
        "network_score": round(state.network_threat_level * 100, 1),
        "emotion_score": round(state.emotion_anger_level * 100, 1),
        "crisis_score": crisis["crisis_score"],
        "status": crisis["status"],
        "convergence_alert": crisis["convergence_alert"],
        "packet_counter": state.packet_counter,
        "packet_rate": state.packet_rate_history[-1] if state.packet_rate_history else 50,
        "packet_rate_history": state.packet_rate_history[-30:],
        "active_attack": state.active_attack,
        "recent_events": state.recent_events[:10],
        "recent_social": state.recent_social[:5],
        "emotion_breakdown": analysis["sentiment"],
        "fake_news_ratio": state.fake_news_ratio,
        "bot_activity": analysis["bot_activity"],
    })

    return {
        "success": True,
        "topic": request.topic,
        "analysis": analysis,
        "crisis_score": crisis["crisis_score"],
        "status": crisis["status"],
    }


@app.post("/api/reset")
async def reset_system():
    """Reset all alerts and return to green state."""
    _reset_state()
    crisis = calculate_crisis_score(
        state.network_threat_level,
        state.emotion_anger_level,
        state.fake_news_ratio,
    )
    await manager.broadcast({
        "type": "reset",
        "timestamp": time.time(),
        "network_score": round(state.network_threat_level * 100, 1),
        "emotion_score": round(state.emotion_anger_level * 100, 1),
        "crisis_score": crisis["crisis_score"],
        "status": crisis["status"],
        "convergence_alert": False,
        "packet_counter": state.packet_counter,
        "packet_rate": 50,
        "packet_rate_history": state.packet_rate_history[-30:],
        "active_attack": None,
        "recent_events": [],
        "recent_social": [],
        "emotion_breakdown": {"angry": 0.08, "fear": 0.07, "neutral": 0.55, "positive": 0.30},
        "fake_news_ratio": 0.10,
        "bot_activity": 0.08,
    })
    return {"success": True, "message": "System reset to baseline state"}


@app.post("/api/demo/toggle")
async def toggle_demo(enabled: bool = True):
    """Toggle demo mode."""
    state.demo_mode = enabled
    return {"success": True, "demo_mode": state.demo_mode}
