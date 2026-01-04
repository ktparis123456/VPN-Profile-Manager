from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from models.profile import VpnProfile


class ProfileEditor(QDialog):
    def __init__(self, parent=None, profile: Optional[VpnProfile] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Profile Editor")
        self.profile = profile or VpnProfile()
        self.name_edit = QLineEdit(self.profile.name)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["openconnect", "openvpn"])
        self.type_combo.setCurrentText(self.profile.vpn_type)
        self.server_edit = QLineEdit(self.profile.server)
        self.group_edit = QLineEdit(self.profile.group or "")
        self.username_edit = QLineEdit(self.profile.username or "")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.ovpn_path_label = QLabel(str(self.profile.ovpn_path) if self.profile.ovpn_path else "")
        browse_button = QPushButton("Browse OVPN")
        browse_button.clicked.connect(self._choose_ovpn)
        self._build_ui(browse_button)

    def _build_ui(self, browse_button: QPushButton) -> None:
        form = QFormLayout()
        form.addRow("Name", self.name_edit)
        form.addRow("Type", self.type_combo)
        form.addRow("Server", self.server_edit)
        form.addRow("Group", self.group_edit)
        form.addRow("Username", self.username_edit)
        form.addRow("Password", self.password_edit)
        ovpn_row = QHBoxLayout()
        ovpn_row.addWidget(self.ovpn_path_label)
        ovpn_row.addWidget(browse_button)
        form.addRow("OVPN File", ovpn_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _choose_ovpn(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select OVPN file", "", "OVPN Files (*.ovpn)")
        if file_path:
            self.ovpn_path_label.setText(file_path)

    def get_profile(self) -> VpnProfile:
        profile = self.profile
        profile.name = self.name_edit.text()
        profile.vpn_type = self.type_combo.currentText()
        profile.server = self.server_edit.text()
        profile.group = self.group_edit.text() or None
        profile.username = self.username_edit.text() or None
        path_text = self.ovpn_path_label.text().strip()
        profile.ovpn_path = Path(path_text) if path_text else None
        return profile

    def get_password(self) -> str:
        return self.password_edit.text()
