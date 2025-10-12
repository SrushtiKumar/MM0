@echo off
echo Setting up Supabase environment variables for Video Steganography Project
echo ========================================================================

echo Setting SUPABASE_URL...
set SUPABASE_URL=https://ldhzvzxmnshpboocnpiv.supabase.co

echo Setting SUPABASE_KEY...
set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkaHp2enhtbnNocGJvb2NucGl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NjQ1NzYsImV4cCI6MjA3NDU0MDU3Nn0.FR-fWoLFwmRehDZ-06u3mkVNoVg0nO6LiBzd3tqOuAc

echo.
echo Environment variables set successfully!
echo.
echo Project Details:
echo   URL: %SUPABASE_URL%
echo   Key: %SUPABASE_KEY:~0,20%...
echo   Project: vf_datacenter (Mumbai region)
echo.
echo You can now run:
echo   python setup_database.py    - to create database tables
echo   python supabase_service.py  - to test the connection
echo.
echo Note: These environment variables are only set for this session.
echo For permanent setup, add them to your system environment variables.