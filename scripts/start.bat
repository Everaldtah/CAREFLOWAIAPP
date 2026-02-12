@echo off
REM CareFlow AI - Quick Start Script for Windows

echo ========================================
echo CareFlow AI - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env >nul

    REM Generate secure keys using PowerShell
    for /f "delims=" %%A in ('powershell -Command "$bytes = New-Object byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); [System.Convert]::ToBase64String($bytes)"') do set SECRET_KEY=%%A
    for /f "delims=" %%A in ('powershell -Command "$bytes = New-Object byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); [System.Convert]::ToBase64String($bytes)"') do set SECRET_KEY_REFRESH=%%A
    for /f "delims=" %%A in ('powershell -Command "$bytes = New-Object byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); [System.BitConverter]::ToString($bytes).Replace('-','').ToLower()"') do set ENCRYPTION_KEY=%%A

    REM Update .env with generated keys
    powershell -Command "(Get-Content .env) -replace 'change-this-secret-key-in-production-use-openssl-rand-base64-32', '%SECRET_KEY%' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'change-this-refresh-secret-key-in-production', '%SECRET_KEY_REFRESH%' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'change-this-encryption-key-32-bytes-hex-exactly', '%ENCRYPTION_KEY%' | Set-Content .env"

    echo Generated secure keys and updated .env
) else (
    echo .env file exists
)

echo.
echo Starting services...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 15 /nobreak

echo.
echo Running database migrations...
docker-compose exec backend alembic upgrade head

echo.
echo Seeding database with demo data...
docker-compose exec backend python scripts/seed_db.py

echo.
echo ========================================
echo CareFlow AI is now running!
echo ========================================
echo.
echo Access Points:
echo ---------------
echo   Frontend:      http://localhost:3000
echo   Backend API:   http://localhost:8000
echo   API Docs:      http://localhost:8000/docs
echo   PgAdmin:       http://localhost:5050
echo.
echo Demo Accounts:
echo --------------
echo   Admin:    admin@careflow.ai / Admin123!
echo   Provider: doctor@careflow.ai / Doctor123!
echo   Patient:  patient@example.com / Patient123!
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause
