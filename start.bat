@echo off
title KeyPerson-Mgmt

echo [1/2] Starting backend...
start "backend" cmd /c "cd /d D:\shujuku\key_person_mgmt\backend && python run.py"
ping -n 4 127.0.0.1 >nul

echo [2/2] Starting frontend...
start "frontend" cmd /c "cd /d D:\shujuku\key_person_mgmt\frontend && npm run dev"
ping -n 3 127.0.0.1 >nul

echo =============================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo Login:    admin / 123456
echo =============================================
pause
