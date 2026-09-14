@echo off
title Death Must Die - Russifier: Remove
echo ==================================================
echo    DEATH MUST DIE - RUSSIFIER REMOVE
echo    Russian messages will follow from the installer.
echo ==================================================
echo.
where powershell >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PowerShell not found on this computer.
    pause
    exit /b 1
)
if not exist "%~dp0Uninstall-Rus.ps1" (
    echo [ERROR] Uninstall-Rus.ps1 not found next to this .bat file.
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Uninstall-Rus.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Removal failed - see messages above.
) else (
    echo.
    echo Done. You can close this window and play in English.
)
pause
