from __future__ import annotations

import sys

from ui.main_window import build_application


def main() -> int:
    app = build_application()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
