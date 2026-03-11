from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from warningnet.modules.file_search import FileSearchService
from warningnet.modules.network_analyzer import analyze_url
from warningnet.modules.premium import PremiumService
from warningnet.modules.system_scanner import disk_summary
from warningnet.modules.vault import VaultService
from warningnet.services.database import APP_DIR, Database


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BlackEngine Technology A.Ş.")
        self.resize(1200, 750)

        self.db = Database()
        self.file_search = FileSearchService(self.db)
        self.vault = VaultService(self.db)
        self.premium = PremiumService(self.db)

        root = QWidget()
        layout = QHBoxLayout(root)

        self.nav = QListWidget()
        self.nav.setFixedWidth(220)
        for item in [
            "Dashboard",
            "File Search",
            "System Scanner",
            "Encryption",
            "BlackBox Vault",
            "Network Analyzer",
            "Settings",
            "Premium",
        ]:
            QListWidgetItem(item, self.nav)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._file_search_page())
        self.pages.addWidget(self._scanner_page())
        self.pages.addWidget(self._encryption_page())
        self.pages.addWidget(self._vault_page())
        self.pages.addWidget(self._network_page())
        self.pages.addWidget(self._settings_page())
        self.pages.addWidget(self._premium_page())

        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)

        layout.addWidget(self.nav)
        layout.addWidget(self.pages)
        self.setCentralWidget(root)

    def _dashboard_page(self) -> QWidget:
        page = QWidget()
        grid = QGridLayout(page)

        with self.db.connect() as conn:
            indexed = conn.execute("SELECT COUNT(*) c FROM indexed_files").fetchone()["c"]
            vault_count = conn.execute("SELECT COUNT(*) c FROM vault_items").fetchone()["c"]

        usage = disk_summary(Path.home())
        premium_status = "Aktif" if self.premium.is_active() else "Ücretsiz"

        cards = {
            "Toplam İndekslenen Dosya": str(indexed),
            "Vault Öğe Sayısı": str(vault_count),
            "Disk Kullanımı": f"%{usage['used_percent']}",
            "Güvenlik Durumu": "İzleniyor",
            "Premium": premium_status,
            "Sürüm": "1.3.26.FAA",
        }

        row = col = 0
        for title, value in cards.items():
            widget = QWidget()
            v = QVBoxLayout(widget)
            t = QLabel(title)
            t.setStyleSheet("font-size: 14px; color: #9aa4b2;")
            val = QLabel(value)
            val.setStyleSheet("font-size: 26px; font-weight: bold;")
            v.addWidget(t)
            v.addWidget(val)
            widget.setStyleSheet("background:#121826; border:1px solid #2a3345; border-radius:8px; padding:12px;")
            grid.addWidget(widget, row, col)
            col += 1
            if col == 3:
                row += 1
                col = 0
        return page

    def _file_search_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        self.index_path = QLineEdit(str(Path.home()))
        btn_choose = QPushButton("Klasör Seç")
        btn_index = QPushButton("İndeksle")
        row1 = QHBoxLayout()
        row1.addWidget(self.index_path)
        row1.addWidget(btn_choose)
        row1.addWidget(btn_index)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Dosya ara...")
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("Uzantı (örn: .pdf)")
        btn_search = QPushButton("Ara")
        row2 = QHBoxLayout()
        row2.addWidget(self.search_input)
        row2.addWidget(self.ext_input)
        row2.addWidget(btn_search)

        self.search_table = QTableWidget(0, 3)
        self.search_table.setHorizontalHeaderLabels(["Ad", "Yol", "Boyut"])

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.search_table)

        btn_choose.clicked.connect(self._choose_index_folder)
        btn_index.clicked.connect(self._index_now)
        btn_search.clicked.connect(self._search_now)
        return page

    def _scanner_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.scan_result = QPlainTextEdit()
        self.scan_result.setReadOnly(True)
        btn_scan = QPushButton("Sistem Özeti Al")
        btn_scan.clicked.connect(self._scan_system)
        layout.addWidget(btn_scan)
        layout.addWidget(self.scan_result)
        return page

    def _encryption_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Encryption modülü BlackBox Vault içinde aktif olarak kullanılmaktadır (AES-256-GCM)."))
        return page

    def _vault_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        row = QHBoxLayout()
        self.vault_file = QLineEdit()
        self.vault_password = QLineEdit()
        self.vault_password.setEchoMode(QLineEdit.Password)
        self.vault_password.setPlaceholderText("Vault parolası")
        btn_pick = QPushButton("Dosya Seç")
        btn_add = QPushButton("Vault'a Ekle")
        row.addWidget(self.vault_file)
        row.addWidget(self.vault_password)
        row.addWidget(btn_pick)
        row.addWidget(btn_add)

        self.vault_table = QTableWidget(0, 2)
        self.vault_table.setHorizontalHeaderLabels(["ID", "Orijinal Ad"])
        self._refresh_vault_table()

        btn_pick.clicked.connect(self._pick_vault_file)
        btn_add.clicked.connect(self._add_to_vault)

        layout.addLayout(row)
        layout.addWidget(self.vault_table)
        return page

    def _network_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        btn = QPushButton("Analiz Et")
        self.network_out = QPlainTextEdit()
        self.network_out.setReadOnly(True)
        btn.clicked.connect(self._analyze_url)
        layout.addWidget(self.url_input)
        layout.addWidget(btn)
        layout.addWidget(self.network_out)
        return page

    def _settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(f"Uygulama dizini: {APP_DIR}")
        layout.addWidget(label)
        return page

    def _premium_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.premium_code_input = QLineEdit()
        self.premium_code_input.setPlaceholderText("Aktivasyon kodu")
        btn = QPushButton("Aktifleştir")
        self.premium_status_label = QLabel("Durum: Aktif" if self.premium.is_active() else "Durum: Ücretsiz")
        btn.clicked.connect(self._activate_premium)
        layout.addWidget(QLabel("Premium Fiyat: 50 TL (IBAN manuel ödeme)"))
        layout.addWidget(self.premium_code_input)
        layout.addWidget(btn)
        layout.addWidget(self.premium_status_label)
        return page

    def _choose_index_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "İndekslenecek klasör")
        if folder:
            self.index_path.setText(folder)

    def _index_now(self) -> None:
        count = self.file_search.index_directory(Path(self.index_path.text().strip()))
        QMessageBox.information(self, "İndeks", f"{count} dosya indekslendi.")

    def _search_now(self) -> None:
        rows = self.file_search.search(self.search_input.text().strip(), self.ext_input.text().strip())
        self.search_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.search_table.setItem(i, 0, QTableWidgetItem(row["name"]))
            self.search_table.setItem(i, 1, QTableWidgetItem(row["path"]))
            self.search_table.setItem(i, 2, QTableWidgetItem(str(row["size"])))

    def _scan_system(self) -> None:
        usage = disk_summary(Path.home())
        self.scan_result.setPlainText(
            f"Toplam: {usage['total']}\nKullanılan: {usage['used']}\nBoş: {usage['free']}\nDoluluk: %{usage['used_percent']}"
        )

    def _pick_vault_file(self) -> None:
        file, _ = QFileDialog.getOpenFileName(self, "Vault için dosya seç")
        if file:
            self.vault_file.setText(file)

    def _add_to_vault(self) -> None:
        if not self.vault_file.text().strip() or not self.vault_password.text().strip():
            QMessageBox.warning(self, "Eksik bilgi", "Dosya ve parola zorunludur")
            return
        item_id = self.vault.add_file(Path(self.vault_file.text().strip()), self.vault_password.text().strip())
        self._refresh_vault_table()
        QMessageBox.information(self, "Vault", f"Dosya eklendi. ID: {item_id}")

    def _refresh_vault_table(self) -> None:
        rows = self.vault.list_items()
        self.vault_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.vault_table.setItem(i, 0, QTableWidgetItem(row["id"]))
            self.vault_table.setItem(i, 1, QTableWidgetItem(row["original_name"]))

    def _analyze_url(self) -> None:
        result = analyze_url(self.url_input.text().strip())
        lines = [f"Risk: {result['risk']} ({result['score']}/100)"]
        lines.extend(f"- {f}" for f in result["findings"]) if result["findings"] else lines.append("- Şüpheli bulgu yok")
        self.network_out.setPlainText("\n".join(lines))

    def _activate_premium(self) -> None:
        ok = self.premium.activate(self.premium_code_input.text())
        if ok:
            self.premium_status_label.setText("Durum: Aktif")
            QMessageBox.information(self, "Premium", "Premium başarıyla aktif edildi")
        else:
            QMessageBox.warning(self, "Premium", "Kod doğrulanamadı")


def setup_crash_logging() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    crash_log = APP_DIR / "crash.log"

    def exception_hook(exc_type, exc, tb):
        with crash_log.open("a", encoding="utf-8") as f:
            f.write("\n---\n")
            traceback.print_exception(exc_type, exc, tb, file=f)
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = exception_hook


def run() -> None:
    setup_crash_logging()
    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
        QWidget { background-color: #0b1020; color: #e7ecf3; }
        QLineEdit, QPlainTextEdit, QTableWidget, QListWidget { background-color: #121826; border: 1px solid #2a3345; }
        QPushButton { background-color: #1f6feb; border: 0; border-radius: 6px; padding: 8px; }
        QPushButton:hover { background-color: #2f81f7; }
        """
    )
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
