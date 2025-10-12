@echo off
echo ======================================================
echo Starting React Frontend Application
echo ======================================================

cd frontend

echo.
echo 1. Installing Node.js dependencies...
npm install

echo.
echo 2. Starting React development server...
echo Frontend will be available at: http://localhost:5173
echo.

npm run dev