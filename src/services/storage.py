from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List

from models.profile import VpnProfile, load_profiles, save_profiles


class ProfileStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.profile_path = base_dir / "profiles.json"
        self.ovpn_dir = base_dir / "ovpn"

    def load(self) -> List[VpnProfile]:
        return load_profiles(self.profile_path)

    def save(self, profiles: List[VpnProfile]) -> None:
        save_profiles(self.profile_path, profiles)

    def import_ovpn(self, source_path: Path) -> Path:
        self.ovpn_dir.mkdir(parents=True, exist_ok=True)
        destination = self.ovpn_dir / source_path.name
        counter = 1
        while destination.exists():
            destination = self.ovpn_dir / f"{source_path.stem}-{counter}{source_path.suffix}"
            counter += 1
        shutil.copy2(source_path, destination)
        return destination

    def import_json_profiles(self, source_path: Path) -> List[VpnProfile]:
        with source_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        profiles = [VpnProfile.from_json(entry) for entry in data.get("profiles", [])]
        return profiles
