@echo off
setlocal

python -m pip install -r requirements.txt
pyinstaller --noconfirm --windowed --name WarningNET --onefile -m warningnet

echo Build complete: dist\WarningNET.exe
endlocal
