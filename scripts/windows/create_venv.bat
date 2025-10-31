@echo off
setlocal

:: --- Accept Python version input ---
if "%~1"=="" (
    echo Select Python version for virtual environment:
    echo [310] Python 3.10
    echo [311] Python 3.11
    echo [312] Python 3.12
    echo [313] Python 3.13
    set /p PYVER="Enter version (e.g. 310): "
) else (
    set PYVER=%~1
)

:: --- Accept environment name input ---
if "%~2"=="" (
    set /p VENVNAME="Enter virtual environment name: "
) else (
    set VENVNAME=%~2
)

:: --- Validate Python version ---
if /i "%PYVER%"=="310" (
    set PYNAME=Python310
) else if /i "%PYVER%"=="311" (
    set PYNAME=Python311
) else if /i "%PYVER%"=="312" (
    set PYNAME=Python312
) else if /i "%PYVER%"=="313" (
    set PYNAME=Python313
) else (
    echo Invalid Python version "%PYVER%".
    echo Valid options: 310, 311, 312, 313
    exit /b 1
)

set PYEXE=%LOCALAPPDATA%\Programs\Python\%PYNAME%\python.exe

:: --- Check Python existence ---
if not exist "%PYEXE%" (
    echo Python executable not found at:
    echo %PYEXE%
    echo Please install Python %PYVER% first.
    exit /b 1
)

:: --- Create the virtual environment ---
echo Creating virtual environment "%VENVNAME%" using %PYNAME%...
"%PYEXE%" -m venv "%VENVNAME%"

if exist "%VENVNAME%\Scripts\activate.bat" (
    echo Virtual environment "%VENVNAME%" created successfully.
    echo To activate it, run:
    echo     call "%VENVNAME%\Scripts\activate"
) else (
    echo Failed to create virtual environment "%VENVNAME%".
    exit /b 1
)

endlocal
