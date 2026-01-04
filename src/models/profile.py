from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid


PROFILE_VERSION = 1


@dataclass
class VpnProfile:
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    vpn_type: str = "openconnect"  # "openconnect" or "openvpn"
    server: str = ""
    group: Optional[str] = None
    username: Optional[str] = None
    ovpn_path: Optional[Path] = None

    def to_json(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["ovpn_path"] = str(self.ovpn_path) if self.ovpn_path else None
        payload["version"] = PROFILE_VERSION
        return payload

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> "VpnProfile":
        profile = cls(
            profile_id=payload.get("profile_id", str(uuid.uuid4())),
            name=payload.get("name", ""),
            vpn_type=payload.get("vpn_type", "openconnect"),
            server=payload.get("server", ""),
            group=payload.get("group"),
            username=payload.get("username"),
            ovpn_path=Path(payload["ovpn_path"]) if payload.get("ovpn_path") else None,
        )
        return profile


def load_profiles(path: Path) -> List[VpnProfile]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    profiles: List[VpnProfile] = []
    for entry in raw.get("profiles", []):
        profiles.append(VpnProfile.from_json(entry))
    return profiles


def save_profiles(path: Path, profiles: List[VpnProfile]) -> None:
    payload = {
        "version": PROFILE_VERSION,
        "profiles": [profile.to_json() for profile in profiles],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
