@echo off
echo ============================================
echo   NEXUS SHIELD - Starting Frontend
echo ============================================
cd /d "%~dp0frontend"
echo Starting React dev server on http://localhost:5173
echo.
npm run dev
