@echo off
echo ======================================================
echo Enhanced Steganography Application Suite
echo ======================================================
echo.
echo This application provides:
echo - Advanced steganography for images, videos, audio, documents
echo - Secure encryption with password protection  
echo - Modern React frontend with real-time progress
echo - FastAPI backend with Supabase database integration
echo.
echo ======================================================

:menu
echo.
echo Please choose an option:
echo.
echo 1. Start Backend Only (FastAPI + Database)
echo 2. Start Frontend Only (React Development Server)
echo 3. Start Both Backend and Frontend
echo 4. Setup Database Only
echo 5. Test API Health
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend  
if "%choice%"=="3" goto both
if "%choice%"=="4" goto setup_db
if "%choice%"=="5" goto health
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
goto menu

:backend
echo.
echo Starting Enhanced Backend...
echo.
start cmd /k start_enhanced_backend.bat
echo Backend starting in new window...
echo.
pause
goto menu

:frontend
echo.
echo Starting React Frontend...
echo.
start cmd /k start_frontend.bat
echo Frontend starting in new window...
echo.
pause
goto menu

:both
echo.
echo Starting Both Backend and Frontend...
echo.
echo Starting Backend...
start cmd /k start_enhanced_backend.bat
timeout /t 5 /nobreak > nul
echo.
echo Starting Frontend...
start cmd /k start_frontend.bat
echo.
echo Both services starting in separate windows...
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:5173
echo - API Docs: http://localhost:8000/docs
echo.
pause
goto menu

:setup_db
echo.
echo Setting up database...
call setup_supabase_env.bat
python setup_database.py
echo.
pause
goto menu

:health
echo.
echo Testing API health...
call setup_supabase_env.bat
python -c "
import requests
try:
    response = requests.get('http://localhost:8000/api/health', timeout=5)
    if response.status_code == 200:
        print('✅ API is healthy!')
        print('Response:', response.json())
    else:
        print('❌ API returned status:', response.status_code)
except Exception as e:
    print('❌ API is not running or unreachable')
    print('Error:', str(e))
    print('Make sure to start the backend first (option 1 or 3)')
"
echo.
pause
goto menu

:exit
echo.
echo Thank you for using Enhanced Steganography Application!
echo.
exit /b

:eof