from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

DEFAULT_OPENCONNECT_PATHS = [
    Path("C:/Program Files/OpenConnect/openconnect.exe"),
    Path("C:/Program Files (x86)/OpenConnect/openconnect.exe"),
]

DEFAULT_OPENVPN_PATHS = [
    Path("C:/Program Files/OpenVPN/bin/openvpn.exe"),
    Path("C:/Program Files (x86)/OpenVPN/bin/openvpn.exe"),
]


class DependencyDetector:
    def __init__(self) -> None:
        self.openconnect_path = self._find_binary("openconnect", DEFAULT_OPENCONNECT_PATHS)
        self.openvpn_path = self._find_binary("openvpn", DEFAULT_OPENVPN_PATHS)

    def refresh(self) -> None:
        self.openconnect_path = self._find_binary("openconnect", DEFAULT_OPENCONNECT_PATHS)
        self.openvpn_path = self._find_binary("openvpn", DEFAULT_OPENVPN_PATHS)

    def _find_binary(self, binary: str, windows_candidates: list[Path]) -> Optional[Path]:
        candidate = shutil.which(binary)
        if candidate:
            return Path(candidate)
        for path in windows_candidates:
            if path.exists():
                return path
        return None

    def openconnect_ready(self) -> bool:
        return self.openconnect_path is not None

    def openvpn_ready(self) -> bool:
        return self.openvpn_path is not None
