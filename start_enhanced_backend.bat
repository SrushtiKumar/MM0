@echo off
echo ======================================================
echo Starting Enhanced Steganography Application
echo ======================================================

echo.
echo 1. Setting up environment variables...
call setup_supabase_env.bat

echo.
echo 2. Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 3. Setting up database tables...
python setup_database.py

echo.
echo 4. Starting FastAPI backend server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

python enhanced_app.py