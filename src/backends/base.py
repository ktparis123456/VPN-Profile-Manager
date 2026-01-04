from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from models.profile import VpnProfile


class VpnBackend(ABC):
    name: str

    @abstractmethod
    def connect(self, profile: VpnProfile, password: Optional[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError
