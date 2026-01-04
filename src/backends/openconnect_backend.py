from __future__ import annotations

from typing import Optional

from models.profile import VpnProfile
from services.dependencies import DependencyDetector
from services.process_manager import ProcessManager

from .base import VpnBackend


class OpenConnectBackend(VpnBackend):
    name = "OpenConnect"

    def __init__(self, detector: DependencyDetector, processes: ProcessManager) -> None:
        self.detector = detector
        self.processes = processes

    def connect(self, profile: VpnProfile, password: Optional[str]) -> None:
        if not self.detector.openconnect_ready():
            raise RuntimeError("OpenConnect client not found")
        command = [str(self.detector.openconnect_path), profile.server]
        if profile.group:
            command.extend(["--authgroup", profile.group])
        if profile.username:
            command.extend(["-u", profile.username])
        if password:
            command.extend(["--passwd-on-stdin"])
        process = self.processes.start(command)
        if password and process.process.stdin:
            process.process.stdin.write(password + "\n")
            process.process.stdin.flush()

    def disconnect(self) -> None:
        self.processes.stop()

    def is_connected(self) -> bool:
        return self.processes.is_running()
