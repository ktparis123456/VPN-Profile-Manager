from __future__ import annotations

from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from models.profile import VpnProfile
from services.storage import ProfileStorage


class ImportDialog(QDialog):
    def __init__(self, storage: ProfileStorage, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import Profiles")
        self.storage = storage
        self.imported: List[VpnProfile] = []
        self.status_label = QLabel("Select a profiles.json or .ovpn file to import")
        self.preview = QListWidget()
        choose_button = QPushButton("Choose file")
        choose_button.clicked.connect(self._choose_file)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.preview)
        layout.addWidget(choose_button)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _choose_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Profiles", "", "Profiles (*.json *.ovpn)")
        if not file_path:
            return
        path = Path(file_path)
        if path.suffix.lower() == ".ovpn":
            copied = self.storage.import_ovpn(path)
            profile = VpnProfile(name=path.stem, vpn_type="openvpn", ovpn_path=copied)
            self.imported = [profile]
            self._render_preview([profile])
            self.status_label.setText(f"Imported OVPN file to {copied}")
        else:
            profiles = self.storage.import_json_profiles(path)
            self.imported = profiles
            self._render_preview(profiles)
            self.status_label.setText(f"Imported {len(profiles)} profiles from JSON")

    def _render_preview(self, profiles: List[VpnProfile]) -> None:
        self.preview.clear()
        for profile in profiles:
            item = QListWidgetItem(f"{profile.name} ({profile.vpn_type})")
            item.setData(256, profile)
            self.preview.addItem(item)

    def get_imported(self) -> List[VpnProfile]:
        return self.imported
