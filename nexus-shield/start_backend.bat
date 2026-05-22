@echo off
echo ============================================
echo   NEXUS SHIELD - Starting Backend Server
echo ============================================
cd /d "%~dp0backend"

echo [1/2] Checking IDS model...
if not exist "models\ids_model.pkl" (
    echo Model not found. Training now...
    python train_model.py
)

echo [2/2] Starting FastAPI server on http://127.0.0.1:8001
echo.
echo API Docs: http://127.0.0.1:8001/docs
echo WebSocket: ws://127.0.0.1:8001/ws/live
echo.
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
