# WarningNET (1.3.26.FAA)

WarningNET; hız, güvenlik, gizlilik ve kontrol odaklı **modüler bir masaüstü güvenlik platformu** olarak bu repoda çalışan bir MVP uygulama halinde sunulmuştur.

## Çalışan Özellikler (MVP)
- **Dashboard:** indeks sayısı, vault öğe sayısı, disk kullanım yüzdesi, premium durumu.
- **File Search:** klasör indeksleme (SQLite), ada/uzantıya göre hızlı arama.
- **System Scanner:** temel disk kullanım özeti.
- **Encryption:** AES-256-GCM şifreleme altyapısı (Vault içinde kullanılır).
- **BlackBox Vault:** dosya ekleme, UUID ile saklama, şifreli depolama, listeleme.
- **Network Analyzer:** URL risk puanı + bulgular.
- **Settings:** uygulama veri dizini görünümü.
- **Premium:** 50 TL modeline uygun aktivasyon ekranı (örnek kod akışı).
- **Crash & Log:** yakalanmamış hataları `~/.warningnet/crash.log` dosyasına yazar.

## Teknoloji
- Python
- PySide6
- SQLite
- cryptography (AES-256-GCM)

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
- `dist/WarningNET.exe`

## Not
Bu sürüm, tam ürün hedefinin profesyonel bir temel mimari uygulamasıdır. Rust hızlandırma, gelişmiş index engine, brute-force kilidi, güvenli silme ve lisans backend tarafı sonraki iterasyonlarda genişletilecektir.
