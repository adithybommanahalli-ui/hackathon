"""
Train IDS Model - Generates synthetic CIC-IDS-like data and trains RandomForest classifier
Run this script once before starting the backend server.

Usage: python train_model.py
"""
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings("ignore")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "ids_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "models", "ids_scaler.pkl")

# ─── Feature names ────────────────────────────────────────────────────────────
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

# ─── Class labels ─────────────────────────────────────────────────────────────
# 0=BENIGN, 1=DoS, 2=PortScan, 3=BruteForce
N_SAMPLES = 10000
N_PER_CLASS = N_SAMPLES // 4


def generate_benign(n: int, rng) -> np.ndarray:
    """Normal web/app traffic."""
    return np.column_stack([
        rng.normal(800, 200, n).clip(200, 1500),        # packet_length
        rng.normal(0.5, 0.2, n).clip(0.05, 3.0),        # flow_duration (sec)
        rng.normal(50, 15, n).clip(5, 200),              # packet_rate (pkt/s)
        rng.normal(40000, 12000, n).clip(1000, 120000),  # byte_rate
        rng.normal(2.0, 0.8, n).clip(0, 6),              # flag_count
        rng.choice([80, 443, 8080, 22, 53, 3306, 5432, 6379], n).astype(float),
        rng.choice([6, 17], n).astype(float),            # TCP=6, UDP=17
        rng.normal(0.02, 0.01, n).clip(0.001, 0.2),     # inter_arrival_time
    ])


def generate_dos(n: int, rng) -> np.ndarray:
    """DoS/DDoS: high packet rate, tiny packets, very short inter-arrival."""
    return np.column_stack([
        rng.normal(64, 12, n).clip(40, 120),             # packet_length: small
        rng.normal(0.001, 0.0005, n).clip(0.0001, 0.01),# flow_duration: tiny
        rng.normal(9500, 800, n).clip(6000, 15000),      # packet_rate: extreme
        rng.normal(608000, 60000, n).clip(300000, 1000000),  # byte_rate: huge
        rng.normal(0.2, 0.1, n).clip(0, 1),              # flag_count: low (SYN flood)
        rng.choice([80, 443, 8080], n).astype(float),    # targeting web ports
        np.full(n, 6.0),                                 # TCP
        rng.normal(0.0001, 0.00005, n).clip(0, 0.001),  # inter_arrival_time: near 0
    ])


def generate_portscan(n: int, rng) -> np.ndarray:
    """Port scan: sequential ports, tiny SYN packets, moderate rate."""
    ports = rng.integers(1, 65535, n).astype(float)
    return np.column_stack([
        rng.normal(40, 8, n).clip(20, 80),               # packet_length: tiny SYN
        rng.normal(0.05, 0.02, n).clip(0.005, 0.3),      # flow_duration: short
        rng.normal(180, 40, n).clip(50, 500),             # packet_rate: moderate
        rng.normal(7200, 1500, n).clip(1000, 20000),      # byte_rate: low
        rng.normal(8, 1.5, n).clip(4, 14),               # flag_count: high SYN
        ports,                                            # sequential/random ports
        np.full(n, 6.0),                                 # TCP
        rng.normal(0.006, 0.002, n).clip(0.001, 0.05),  # inter_arrival_time
    ])


def generate_bruteforce(n: int, rng) -> np.ndarray:
    """Brute force: repeated same port (22/3389), high frequency, auth packets."""
    target_ports = rng.choice([22, 3389, 21, 23, 5900], n).astype(float)
    return np.column_stack([
        rng.normal(200, 40, n).clip(80, 400),            # packet_length: auth size
        rng.normal(0.1, 0.03, n).clip(0.02, 0.5),        # flow_duration
        rng.normal(400, 80, n).clip(100, 800),            # packet_rate: high
        rng.normal(80000, 15000, n).clip(10000, 200000),  # byte_rate
        rng.normal(3, 0.8, n).clip(1, 6),                # flag_count
        target_ports,                                     # same port repeated
        np.full(n, 6.0),                                 # TCP
        rng.normal(0.003, 0.001, n).clip(0.0005, 0.02), # inter_arrival_time
    ])


def main():
    print("=" * 60)
    print("  NEXUS SHIELD — IDS Model Training")
    print("=" * 60)

    rng = np.random.default_rng(2024)

    print(f"\n[1/5] Generating {N_SAMPLES} synthetic samples...")
    X_benign = generate_benign(N_PER_CLASS, rng)
    X_dos = generate_dos(N_PER_CLASS, rng)
    X_portscan = generate_portscan(N_PER_CLASS, rng)
    X_bruteforce = generate_bruteforce(N_PER_CLASS, rng)

    X = np.vstack([X_benign, X_dos, X_portscan, X_bruteforce])
    y = np.array(
        [0] * N_PER_CLASS +  # BENIGN
        [1] * N_PER_CLASS +  # DoS
        [2] * N_PER_CLASS +  # PortScan
        [3] * N_PER_CLASS    # BruteForce
    )

    print(f"    Dataset shape: {X.shape}")
    print(f"    Classes: BENIGN={N_PER_CLASS}, DoS={N_PER_CLASS}, "
          f"PortScan={N_PER_CLASS}, BruteForce={N_PER_CLASS}")

    print("\n[2/5] Splitting train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n[3/5] Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    print("\n[4/5] Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n    Accuracy: {acc * 100:.2f}%")
    print("\n    Classification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["BENIGN", "DoS", "PortScan", "BruteForce"],
        )
    )

    if acc < 0.95:
        print(f"    ⚠ Accuracy {acc:.2%} below 95% target — consider more samples")
    else:
        print(f"    ✓ Accuracy {acc:.2%} meets >95% target")

    print("\n[5/5] Saving model...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"    Model saved → {MODEL_PATH}")

    # Feature importance
    importances = model.feature_importances_
    print("\n    Feature Importances:")
    for name, imp in sorted(
        zip(FEATURE_NAMES, importances), key=lambda x: -x[1]
    ):
        bar = "█" * int(imp * 40)
        print(f"    {name:25s} {imp:.4f}  {bar}")

    print("\n" + "=" * 60)
    print("  Training complete! Model ready for inference.")
    print("=" * 60)


if __name__ == "__main__":
    main()
