@echo off
title Death Must Die - Russifier: Install
echo ==================================================
echo    DEATH MUST DIE - RUSSIFIER INSTALL
echo    Russian messages will follow from the installer.
echo ==================================================
echo.
where powershell >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PowerShell not found on this computer.
    pause
    exit /b 1
)
if not exist "%~dp0Install-Rus.ps1" (
    echo [ERROR] Install-Rus.ps1 not found next to this .bat file.
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Rus.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed - see messages above.
) else (
    echo.
    echo Done. You can close this window and start the game.
)
pause
