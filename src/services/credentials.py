from __future__ import annotations

from typing import Optional

import keyring


class CredentialService:
    def __init__(self, service_name: str = "VPN-Profile-Manager") -> None:
        self.service_name = service_name

    def store_password(self, profile_id: str, username: str, password: str) -> None:
        keyring.set_password(self._key(profile_id, username), username, password)

    def get_password(self, profile_id: str, username: str) -> Optional[str]:
        return keyring.get_password(self._key(profile_id, username), username)

    def clear_password(self, profile_id: str, username: str) -> None:
        try:
            keyring.delete_password(self._key(profile_id, username), username)
        except keyring.errors.PasswordDeleteError:
            # Nothing to clean up when the entry does not exist
            pass

    def _key(self, profile_id: str, username: str) -> str:
        return f"{self.service_name}:{profile_id}:{username}"
