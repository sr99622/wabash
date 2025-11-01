@echo off
setlocal

:: --- Accept user input or command line argument ---
if "%~1"=="" (
    echo Select Python version to start:
    echo [310] Python 3.10
    echo [311] Python 3.11
    echo [312] Python 3.12
    echo [313] Python 3.13
    set /p PYVER="Enter version (e.g. 310): "
) else (
    set PYVER=%~1
)

:: --- Validate input and set Python path ---
if /i "%PYVER%"=="310" (
    set PYNAME=Python310
) else if /i "%PYVER%"=="311" (
    set PYNAME=Python311
) else if /i "%PYVER%"=="312" (
    set PYNAME=Python312
) else if /i "%PYVER%"=="313" (
    set PYNAME=Python313
) else (
    echo Invalid selection "%PYVER%".
    echo Valid options: 310, 311, 312, 313
    exit /b 1
)

set PYEXE=%LOCALAPPDATA%\Programs\Python\%PYNAME%\python.exe

:: --- Check existence ---
if not exist "%PYEXE%" (
    echo Python executable not found at:
    echo %PYEXE%
    echo Please install Python %PYVER% first.
    exit /b 1
)

echo Starting %PYNAME%...
"%PYEXE%"
endlocal
