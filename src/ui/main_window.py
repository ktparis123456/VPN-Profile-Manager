from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

from backends.openconnect_backend import OpenConnectBackend
from backends.openvpn_backend import OpenVpnBackend
from models.profile import VpnProfile
from services.credentials import CredentialService
from services.dependencies import DependencyDetector
from services.logger import configure_logging
from services.process_manager import ProcessManager
from services.storage import ProfileStorage
from ui.import_dialog import ImportDialog
from ui.profile_editor import ProfileEditor


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VPN Profile Manager")
        self.base_dir = self._determine_base_dir()
        self.log = configure_logging(self.base_dir / "logs")
        self.dependencies = DependencyDetector()
        self.storage = ProfileStorage(self.base_dir)
        self.credentials = CredentialService()
        self.process_manager = ProcessManager(self._log_to_ui)

        self.backends: Dict[str, object] = {
            "openconnect": OpenConnectBackend(self.dependencies, self.process_manager),
            "openvpn": OpenVpnBackend(self.dependencies, self.process_manager),
        }
        self.current_backend: Optional[object] = None

        self.profiles: List[VpnProfile] = self.storage.load()

        self.filter_edit = QLineEdit()
        self.profile_list = QListWidget()
        self.status_label = QLabel("Ready")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self._build_ui()
        self._refresh_profile_list()

    def _determine_base_dir(self) -> Path:
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        target = base / "VPN-Profile-Manager"
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _build_ui(self) -> None:
        toolbar = QToolBar()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_profile)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._edit_profile)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_profile)
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._import_profiles)
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self._connect_selected)
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self._disconnect)

        for widget in [add_btn, edit_btn, delete_btn, import_btn, connect_btn, disconnect_btn]:
            toolbar.addWidget(widget)
        self.addToolBar(toolbar)

        filter_row = QHBoxLayout()
        self.filter_edit.setPlaceholderText("Filter profiles")
        self.filter_edit.textChanged.connect(self._refresh_profile_list)
        filter_row.addWidget(QLabel("Filter:"))
        filter_row.addWidget(self.filter_edit)

        left = QVBoxLayout()
        left.addLayout(filter_row)
        left.addWidget(self.profile_list)
        left.addWidget(self.status_label)

        right = QVBoxLayout()
        right.addWidget(QLabel("Logs"))
        right.addWidget(self.log_view)

        layout = QHBoxLayout()
        layout.addLayout(left, 1)
        layout.addLayout(right, 1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _refresh_profile_list(self) -> None:
        filter_text = self.filter_edit.text().lower()
        self.profile_list.clear()
        for profile in self.profiles:
            if filter_text and filter_text not in profile.name.lower():
                continue
            item = QListWidgetItem(f"{profile.name} ({profile.vpn_type})")
            item.setData(Qt.UserRole, profile)
            self.profile_list.addItem(item)

    def _add_profile(self) -> None:
        dialog = ProfileEditor(self)
        if dialog.exec() == QDialog.Accepted:
            profile = dialog.get_profile()
            password = dialog.get_password()
            self.profiles.append(profile)
            self.storage.save(self.profiles)
            if password and profile.username:
                self.credentials.store_password(profile.profile_id, profile.username, password)
            self._refresh_profile_list()
            self._log_to_ui(f"Added profile {profile.name}")

    def _edit_profile(self) -> None:
        profile = self._selected_profile()
        if not profile:
            QMessageBox.warning(self, "Edit Profile", "Select a profile first")
            return
        dialog = ProfileEditor(self, profile)
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            updated = dialog.get_profile()
            if password and updated.username:
                self.credentials.store_password(updated.profile_id, updated.username, password)
            self.storage.save(self.profiles)
            self._refresh_profile_list()
            self._log_to_ui(f"Updated profile {updated.name}")

    def _delete_profile(self) -> None:
        profile = self._selected_profile()
        if not profile:
            return
        if profile.username:
            self.credentials.clear_password(profile.profile_id, profile.username)
        self.profiles = [p for p in self.profiles if p.profile_id != profile.profile_id]
        self.storage.save(self.profiles)
        self._refresh_profile_list()
        self._log_to_ui(f"Deleted profile {profile.name}")

    def _import_profiles(self) -> None:
        dialog = ImportDialog(self.storage, self)
        if dialog.exec() == QDialog.Accepted:
            imported = dialog.get_imported()
            if not imported:
                return
            for profile in imported:
                self.profiles.append(profile)
            self.storage.save(self.profiles)
            self._refresh_profile_list()
            self._log_to_ui(f"Imported {len(imported)} profile(s)")

    def _connect_selected(self) -> None:
        profile = self._selected_profile()
        if not profile:
            QMessageBox.warning(self, "Connect", "Select a profile to connect")
            return
        backend = self.backends.get(profile.vpn_type)
        if backend is None:
            QMessageBox.critical(self, "Connect", f"Unsupported VPN type {profile.vpn_type}")
            return
        password = self._get_password(profile)
        try:
            backend.connect(profile, password)
            self.current_backend = backend
            self.status_label.setText(f"Connected via {profile.name}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Connect", str(exc))
            self._log_to_ui(str(exc))

    def _disconnect(self) -> None:
        if self.current_backend:
            self.current_backend.disconnect()
            self.status_label.setText("Disconnected")
            self._log_to_ui("Disconnected from VPN")
            self.current_backend = None

    def _selected_profile(self) -> Optional[VpnProfile]:
        item = self.profile_list.currentItem()
        if not item:
            return None
        return item.data(Qt.UserRole)

    def _get_password(self, profile: VpnProfile) -> Optional[str]:
        if profile.username:
            stored = self.credentials.get_password(profile.profile_id, profile.username)
            if stored:
                return stored
            password, ok = QInputDialog.getText(self, "Password Required", "Password:", QLineEdit.Password)
            if ok and password:
                self.credentials.store_password(profile.profile_id, profile.username, password)
                return password
        return None

    def _log_to_ui(self, message: str) -> None:
        self.log(message)
        self.log_view.append(message)


def build_application() -> QApplication:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app
