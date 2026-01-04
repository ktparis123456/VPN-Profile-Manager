from __future__ import annotations

from typing import Optional

from models.profile import VpnProfile
from services.dependencies import DependencyDetector
from services.process_manager import ProcessManager

from .base import VpnBackend


class OpenVpnBackend(VpnBackend):
    name = "OpenVPN"

    def __init__(self, detector: DependencyDetector, processes: ProcessManager) -> None:
        self.detector = detector
        self.processes = processes

    def connect(self, profile: VpnProfile, password: Optional[str]) -> None:
        if not self.detector.openvpn_ready():
            raise RuntimeError("OpenVPN client not found")
        if not profile.ovpn_path:
            raise RuntimeError("OpenVPN profile is missing an .ovpn file")
        command = [str(self.detector.openvpn_path), "--config", str(profile.ovpn_path)]
        if profile.username:
            command.extend(["--auth-user-pass"])
        process = self.processes.start(command, workdir=profile.ovpn_path.parent)
        if password and process.process.stdin:
            process.process.stdin.write(password + "\n")
            process.process.stdin.flush()

    def disconnect(self) -> None:
        self.processes.stop()

    def is_connected(self) -> bool:
        return self.processes.is_running()
