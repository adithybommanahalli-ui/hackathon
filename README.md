# NEXUS SHIELD + CYBER DUEL 🛡️⚔️

Real-time cyber-social intelligence dashboard, plus attack simulator to stress-test it.

## Repo Structure

```
nexus-shield/   → Main app (FastAPI backend + React dashboard)
cyber_duel/     → Attack scripts that hit nexus-shield's API
index.html      → Standalone older attack/IDS demo page
```

## Quick Start

### 1. Backend
```bash
cd nexus-shield/backend
pip install -r requirements.txt
python train_model.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend
```bash
cd nexus-shield/frontend
npm install
npm run dev
```
Dashboard → http://localhost:5173

### 3. Attack it (Cyber Duel)
```bash
cd cyber_duel
python launch.py
```
Pick attacks (DoS, PortScan, BruteForce, Slowloris, Social Panic, Fake News, Coordinated, Rapid Fire) and watch the dashboard react in real time.

Reset anytime: `python reset.py`

## How It Works

- **IDS Engine**: RandomForest classifies traffic as BENIGN / DoS / PortScan / BruteForce
- **Emotion Engine**: Sentiment + fake-news detection on social topics
- **Crisis Score**: `0.40×Network + 0.35×Emotion + 0.25×FakeNews`
- **Convergence Alert**: fires when network threat AND social anger both >70%

| Score | Status |
|-------|--------|
| 0–40  | 🟢 SECURE |
| 41–70 | 🟡 CAUTION |
| 71–100| 🔴 CRITICAL |

## Stack

FastAPI · React + Vite + Tailwind · Recharts · scikit-learn · HuggingFace Transformers · WebSockets

Aditya Basavaraj, CSE DEPARTMENT, GM UNIVERSITY, DAVANGERE
