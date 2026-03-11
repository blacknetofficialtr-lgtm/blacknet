@echo off
setlocal

python -m pip install -r requirements.txt
pyinstaller --noconfirm --windowed --name BlackEngine --onefile -m warningnet

echo Build complete: dist\BlackEngine.exe
endlocal
