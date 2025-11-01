rem this file needs to be run in admin mode
set BASE_PATH=%CD%

rem remove local __pycache__ directories
cd wabash
setlocal enabledelayedexpansion
echo Searching for __pycache__ directories under %cd% ...
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        echo Deleting "%%d"
        rmdir /s /q "%%d"
    )
)
endlocal
cd ..

mkdir %BASE_PATH%\installer
cd %BASE_PATH%\installer
if not exist "%ProgramFiles(x86)%\NSIS\" (
    curl -OL https://prdownloads.sourceforge.net/nsis/nsis-3.11-setup.exe?download
    nsis-3.11-setup.exe
    echo "Wait for the NSIS installer to finish, then type the enter key"
    pause
)
if not exist cpython-3.13.3+20250517-x86_64-pc-windows-msvc-install_only.tar.gz (
    curl -OL https://github.com/astral-sh/python-build-standalone/releases/download/20250517/cpython-3.13.3+20250517-x86_64-pc-windows-msvc-install_only.tar.gz
)
mkdir "%ProgramFiles(x86)%\wabash"
tar -xzf cpython-3.13.3+20250517-x86_64-pc-windows-msvc-install_only.tar.gz -C "%ProgramFiles(x86)%\wabash"
cd "%ProgramFiles(x86)%\wabash"
python\python -m venv env
env\Scripts\pip install %BASE_PATH% torch torchvision openvino
cd %BASE_PATH%\installer
copy %BASE_PATH%\wabash\gui\resources\wabash.ico .
copy %BASE_PATH%\scripts\windows\wabash.nsi .
copy %BASE_PATH%\LICENSE .
"%ProgramFiles(x86)%\NSIS\makensis" wabash.nsi
rmdir /q /s "%ProgramFiles(x86)%\wabash"
cd %BASE_PATH%