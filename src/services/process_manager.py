from __future__ import annotations

import subprocess
import threading
from pathlib import Path
from typing import Callable, List, Optional


class ManagedProcess:
    def __init__(self, process: subprocess.Popen[str], on_output: Callable[[str], None]) -> None:
        self.process = process
        self._on_output = on_output
        self._reader = threading.Thread(target=self._stream_output, daemon=True)
        self._reader.start()

    def _stream_output(self) -> None:
        if self.process.stdout is None:
            return
        for line in self.process.stdout:
            self._on_output(line.rstrip())

    def terminate(self) -> None:
        self.process.terminate()

    def is_running(self) -> bool:
        return self.process.poll() is None


class ProcessManager:
    def __init__(self, log_callback: Callable[[str], None]) -> None:
        self.log_callback = log_callback
        self.current: Optional[ManagedProcess] = None

    def start(self, command: List[str], workdir: Optional[Path] = None) -> ManagedProcess:
        if self.current and self.current.is_running():
            raise RuntimeError("A VPN process is already running")

        self.log_callback(f"Launching: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            cwd=workdir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False,
        )
        self.current = ManagedProcess(process, self.log_callback)
        return self.current

    def stop(self) -> None:
        if self.current and self.current.is_running():
            self.log_callback("Stopping VPN process")
            self.current.terminate()
            self.current = None

    def is_running(self) -> bool:
        return bool(self.current and self.current.is_running())
