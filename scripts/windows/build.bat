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

echo Done.
endlocal
cd ..

pip install -v .
