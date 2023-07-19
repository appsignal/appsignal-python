from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Config


@dataclass
class Agent:
    path: Path = Path(__file__).parent / "appsignal-agent"
    active: bool = False

    def start(self, config: Config) -> None:
        config.set_private_environ()
        p = subprocess.Popen(
            [self.path, "start", "--private"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.wait(timeout=1)
        returncode = p.returncode
        if returncode == 0:
            self.active = True
        else:
            output, _ = p.communicate()
            out = output.decode("utf-8")
            print(f"AppSignal agent is unable to start ({returncode}): ", out)

    def diagnose(self) -> bytes:
        return subprocess.run([self.path, "diagnose"], capture_output=True).stdout

    def version(self) -> bytes:
        return subprocess.run(
            [self.path, "--version"], capture_output=True
        ).stdout.split()[-1]


agent = Agent()
