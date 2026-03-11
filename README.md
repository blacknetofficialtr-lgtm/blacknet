# BlackEngine Technology A.Ş.

**Yapımcı Şirket:** W.E. Corp. Official

Bu repo, BlackEngine Technology A.Ş. masaüstü platformu için başlangıç mimarisi ve çalışan uygulama iskeletini içerir.

## Mevcut Durum
- Modüler Python masaüstü uygulama yapısı
- PySide6 tabanlı ana arayüz
- SQLite servis katmanı
- Paketleme (EXE) için PyInstaller scriptleri
- Temel test altyapısı

## Kurulum
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Çalıştırma
```bash
python -m warningnet
```

## EXE Üretimi (Windows)
PowerShell:
```powershell
./scripts/build_exe.ps1
```

CMD:
```bat
scripts\build_exe.bat
```

Üretilen dosya:
- `dist/BlackEngine.exe`

## Not
Teknik paket adı mevcut kod uyumluluğu için kısa vadede `warningnet` olarak korunmuştur; ürün adı ve kurumsal kimlik BlackEngine Technology A.Ş. olarak güncellenmiştir.
