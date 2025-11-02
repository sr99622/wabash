@echo off
setlocal

rem this script should be run from the project directory
set BASE_PATH=%CD%

rem remove local __pycache__ directories
cd "%BASE_PATH%\wabash"
setlocal enabledelayedexpansion
echo -- Searching for __pycache__ directories under %cd% ...
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        echo -- Deleting "%%d"
        rmdir /s /q "%%d"
    )
)
endlocal
cd "%BASE_PATH%"

echo -- Checking for installed NSIS
if not exist "%ProgramFiles(x86)%\NSIS\" (
    echo -- The NSIS executable will be downloaded
    curl -OL https://prdownloads.sourceforge.net/nsis/nsis-3.11-setup.exe?download
    nsis-3.11-setup.exe
    echo -- Wait for the NSIS installer to finish, then type the enter key
    pause
) else (
    echo -- Found existing NSIS
)

rem remove any previous installation artifacts
if exist "%BASE_PATH%\installer" (
    echo -- A previous temporary installer directory exists. Deleting...
    rmdir /s /q "%BASE_PATH%\installer"
)
echo -- Creating a new installer directory at %BASE_PATH%\installer
mkdir "%BASE_PATH%\installer"
cd "%BASE_PATH%\installer"

echo -- Downloading portable Python from Astral
curl -OL https://github.com/astral-sh/python-build-standalone/releases/download/20250517/cpython-3.13.3+20250517-x86_64-pc-windows-msvc-install_only.tar.gz

echo -- Creating a staging directory for installer components
mkdir "%BASE_PATH%\installer\staging"
tar -xzf cpython-3.13.3+20250517-x86_64-pc-windows-msvc-install_only.tar.gz -C "%BASE_PATH%\installer\staging"
cd %BASE_PATH%\installer\staging

echo -- Creating portable virtual environment
python\python -m venv env
env\Scripts\python -m ensurepip --upgrade
env\Scripts\python -m pip install --upgrade pip setuptools wheel
env\Scripts\pip install "%BASE_PATH%"

echo -- Copying files from repository for installer access
cd "%BASE_PATH%\installer"
copy "%BASE_PATH%\wabash\gui\resources\wabash.ico" .
copy "%BASE_PATH%\scripts\windows\wabash.nsi" .
copy "%BASE_PATH%\LICENSE" .

echo -- Starting build for executable installer
set "NSIS_EXE=%ProgramFiles(x86)%\NSIS\makensis"
"%NSIS_EXE%" wabash.nsi

echo -- Made the installer file in the folder %BASE_PATH%\installer
cd "%BASE_PATH%"

echo -- Done
endlocal