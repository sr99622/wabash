@echo off

echo Remove local __pycache__ directories
cd wabash
setlocal enabledelayedexpansion
echo Searching for __pycache__ directories under %cd% ...
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        echo Deleting "%%d"
        rmdir /s /q "%%d"
    )
)

echo Searching for existing pyd binaries
for /r %%F in ("*_wabash.cp*-win_amd64.pyd") do (
    echo Deleting %%F
    del /f "%%F"
)

endlocal
cd ..
pip install -v .
echo Done.
