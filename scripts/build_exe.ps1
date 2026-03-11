python -m pip install -r requirements.txt
pyinstaller --noconfirm --windowed --name WarningNET --onefile -m warningnet
Write-Host "Build complete: dist/WarningNET.exe"
