@echo off
title Flor de Dende PDV
color 0A
echo.
echo  ==========================================
echo   🌸 Flor de Dende PDV - Iniciando...
echo  ==========================================
echo.
echo [1/4] Iniciando MySQL...
sc query MySQL80 | find "RUNNING" >nul 2>&1
if %errorlevel% neq 0 (
    net start MySQL80 >nul 2>&1
    if %errorlevel% neq 0 net start MySQL >nul 2>&1
    timeout /t 4 /nobreak >nul
)
echo      MySQL OK!
echo [2/4] Iniciando Backend...
start "Backend PDV" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python manage.py runserver 8000"
timeout /t 7 /nobreak >nul
echo [3/4] Iniciando Frontend...
start "Frontend PDV" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 5 /nobreak >nul
echo [4/4] Abrindo navegador...
start "" "http://localhost:5173"
echo.
echo  Sistema rodando! Acesse: http://localhost:5173
pause
