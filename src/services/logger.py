from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable


def configure_logging(log_dir: Path) -> Callable[[str], None]:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "vpn_profile_manager.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
    )

    def emit(message: str) -> None:
        logging.info(message)

    return emit
