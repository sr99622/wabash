@echo off
setlocal

:: --- Accept user input or command line argument ---
if "%~1"=="" (
    echo Select Python version to install:
    echo [310] Python 3.10.11
    echo [311] Python 3.11.9
    echo [312] Python 3.12.9
    echo [313] Python 3.13.2
    set /p PYVER="Enter version (e.g. 310): "
) else (
    set PYVER=%~1
)

:: --- Validate input ---
if /i "%PYVER%"=="310" (
    set PYNAME=Python310
    set PYFILE=python-3.10.11-amd64.exe
    set PYURL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
) else if /i "%PYVER%"=="311" (
    set PYNAME=Python311
    set PYFILE=python-3.11.9-amd64.exe
    set PYURL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
) else if /i "%PYVER%"=="312" (
    set PYNAME=Python312
    set PYFILE=python-3.12.9-amd64.exe
    set PYURL=https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
) else if /i "%PYVER%"=="313" (
    set PYNAME=Python313
    set PYFILE=python-3.13.2-amd64.exe
    set PYURL=https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe
) else (
    echo Invalid selection "%PYVER%".
    echo Valid options: 310, 311, 312, 313
    exit /b 1
)

:: --- Install if not already present ---
if not exist "%LOCALAPPDATA%\Programs\Python\%PYNAME%\" (
    echo Downloading %PYFILE%...
    curl -L -o "%PYFILE%" "%PYURL%"
    echo Installing %PYNAME% silently...
    "%PYFILE%" /passive /quiet
    echo Deleting downloaded file %PYFILE%...
    del "%PYFILE%"
) else (
    echo %PYNAME% is already installed.
)

echo Done.
endlocal
