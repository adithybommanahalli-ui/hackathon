"""
IDS Engine - Network Intrusion Detection System
Uses trained RandomForest model to classify network traffic
"""
import numpy as np
import joblib
import os
from typing import Dict, List, Tuple

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ids_model.pkl")

# Feature names matching training data
FEATURE_NAMES = [
    "packet_length",
    "flow_duration",
    "packet_rate",
    "byte_rate",
    "flag_count",
    "port_number",
    "protocol",
    "inter_arrival_time",
]

ATTACK_TYPES = {0: "BENIGN", 1: "DoS", 2: "PortScan", 3: "BruteForce"}


class IDSEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            print("[IDS] Model loaded successfully.")
        else:
            print("[IDS] Model not found. Please run train_model.py first.")

    def predict(self, features: np.ndarray) -> Dict:
        """Predict attack type for a batch of packet feature vectors."""
        if self.model is None:
            return {"error": "Model not loaded"}

        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)

        results = []
        for pred, prob in zip(predictions, probabilities):
            results.append(
                {
                    "label": ATTACK_TYPES.get(int(pred), "UNKNOWN"),
                    "class_id": int(pred),
                    "confidence": float(np.max(prob)),
                    "probabilities": {
                        ATTACK_TYPES[i]: float(p) for i, p in enumerate(prob)
                    },
                }
            )
        return results

    def generate_dos_features(self, n: int = 50) -> np.ndarray:
        """Generate synthetic DoS attack feature vectors."""
        rng = np.random.default_rng(42)
        features = np.column_stack(
            [
                rng.normal(64, 10, n).clip(40, 100),       # packet_length: small
                rng.normal(0.001, 0.0005, n).clip(0, 0.01),# flow_duration: very short
                rng.normal(9000, 500, n).clip(7000, 12000), # packet_rate: extremely high
                rng.normal(576000, 50000, n).clip(400000, 800000),  # byte_rate: high
                rng.normal(0.1, 0.05, n).clip(0, 0.5),     # flag_count: low (SYN flood)
                rng.integers(80, 443, n).astype(float),     # port_number: common ports
                np.ones(n) * 6,                             # protocol: TCP=6
                rng.normal(0.0001, 0.00005, n).clip(0, 0.001),  # inter_arrival_time: tiny
            ]
        )
        return features

    def generate_portscan_features(self, n: int = 50) -> np.ndarray:
        """Generate synthetic Port Scan feature vectors."""
        rng = np.random.default_rng(99)
        ports = np.linspace(1, 65535, n)  # sequential port scanning
        features = np.column_stack(
            [
                rng.normal(40, 5, n).clip(20, 60),          # packet_length: tiny SYN
                rng.normal(0.05, 0.01, n).clip(0.01, 0.2),  # flow_duration: short
                rng.normal(200, 30, n).clip(100, 400),       # packet_rate: moderate
                rng.normal(8000, 1000, n).clip(4000, 15000), # byte_rate: low
                rng.normal(8, 1, n).clip(5, 12),             # flag_count: high SYN flags
                ports,                                        # port_number: sequential
                np.ones(n) * 6,                              # protocol: TCP
                rng.normal(0.005, 0.001, n).clip(0.001, 0.02),  # inter_arrival_time
            ]
        )
        return features

    def generate_benign_features(self, n: int = 50) -> np.ndarray:
        """Generate synthetic benign traffic feature vectors."""
        rng = np.random.default_rng(7)
        features = np.column_stack(
            [
                rng.normal(800, 200, n).clip(200, 1500),     # packet_length: normal
                rng.normal(0.5, 0.2, n).clip(0.1, 2.0),     # flow_duration: normal
                rng.normal(50, 15, n).clip(10, 150),         # packet_rate: normal
                rng.normal(40000, 10000, n).clip(5000, 100000),  # byte_rate: normal
                rng.normal(2, 0.5, n).clip(0, 5),            # flag_count: normal
                rng.choice([80, 443, 8080, 22, 53, 3306], n).astype(float),
                rng.choice([6, 17], n).astype(float),        # TCP or UDP
                rng.normal(0.02, 0.01, n).clip(0.001, 0.1), # inter_arrival_time
            ]
        )
        return features

    def analyze_batch(self, features: np.ndarray) -> Dict:
        """Analyze a batch and return summary statistics."""
        predictions = self.predict(features)
        if "error" in predictions:
            return predictions

        labels = [p["label"] for p in predictions]
        attack_count = sum(1 for l in labels if l != "BENIGN")
        total = len(labels)

        attack_types = {}
        for label in labels:
            if label != "BENIGN":
                attack_types[label] = attack_types.get(label, 0) + 1

        threat_level = attack_count / total if total > 0 else 0

        return {
            "total_packets": total,
            "malicious": attack_count,
            "safe": total - attack_count,
            "threat_level": round(threat_level, 3),
            "attack_types": attack_types,
            "predictions": predictions[:10],  # return first 10 for display
        }
