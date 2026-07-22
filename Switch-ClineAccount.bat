@echo off
title Cline - Switch Account
echo ============================================
echo  Switch Cline CLI Account
echo ============================================
echo.

:: Ask for email
set /p SWITCH_EMAIL=Enter email to log in with: 

if "%SWITCH_EMAIL%"=="" (
    echo No email entered. Exiting.
    pause
    exit /b 1
)

set CLINE_DATA=%USERPROFILE%\.cline\data
set SECRETS=%CLINE_DATA%\secrets.json
set PROVIDERS=%CLINE_DATA%\settings\providers.json
set BACKUP=%SECRETS%.backup

:: Step 1: Backup current secrets
echo [1/4] Backing up current tokens...
copy "%SECRETS%" "%BACKUP%" >nul
echo       Backup created: %BACKUP%

:: Step 2: Clear secrets
echo [2/4] Clearing secrets.json...
echo {} > "%SECRETS%"
echo       Secrets cleared.

:: Step 3: Clear provider auth tokens (no escaping needed)
echo [3/4] Clearing provider tokens...
powershell -NoProfile -Command "$p = Get-Content \"%PROVIDERS%\" -Raw | ConvertFrom-Json; $p.providers.cline.settings.auth = $null; $p.providers.cline.tokenSource = $null; try { $p.providers.'cline-pass'.settings.auth = $null } catch {}; $p | ConvertTo-Json -Depth 10 | Set-Content \"%PROVIDERS%\" -Encoding UTF8"
echo       Provider tokens cleared.

echo.
echo ============================================
echo  Tokens cleared! Launching Cline auth...
echo  Log in with: %SWITCH_EMAIL%
echo.
echo  A browser window will open. Sign in with
echo  the Google account above.
echo ============================================
echo.

:: Step 4: Launch Cline auth in browser
echo [4/4] Opening Cline auth in browser...
start "" "%USERPROFILE%\AppData\Roaming\npm\node_modules\cline\node_modules\@cline\cli-windows-x64\bin\cline.exe" auth cline

:: Step 5: Wait a moment, then open Cline in a new terminal
echo.
echo  Waiting for auth to register, then opening Cline...
timeout /t 5 /nobreak >nul
echo.
echo [5/5] Launching Cline in a new terminal...
start "Cline" cmd /k "title Cline && cline"

echo.
echo ============================================
echo  DONE - Auth flow started!
echo.
echo  A browser opened for Google login.
echo  A Cline terminal is also opening now.
echo.
echo  The new Cline terminal should pick up
echo  the auth automatically.
echo.
echo  To switch back: run this script again with
echo  your old email, OR restore the backup:
echo    copy "%BACKUP%" "%SECRETS%"
echo ============================================
pause
exit /b 0
