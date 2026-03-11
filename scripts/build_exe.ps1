python -m pip install -r requirements.txt
pyinstaller --noconfirm --windowed --name BlackEngine --onefile -m warningnet
Write-Host "Build complete: dist/BlackEngine.exe"
