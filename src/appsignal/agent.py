from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from . import internal_logger as logger
from .config import Config


@dataclass
class Agent:
    package_path: Path = Path(__file__).parent
    agent_path: Path = package_path / "appsignal-agent"
    platform_path: Path = package_path / "_appsignal_platform"
    _active: bool = False

    @property
    def active(self) -> bool:
        return self._active

    def start(self, config: Config) -> None:
        config.set_private_environ()

        if self.architecture_and_platform() == ["any"]:
            message = "AppSignal agent is not available for this platform."
            # When a collector is used, the data still reaches it without the
            # agent, so only what the agent reports itself is lost. The client
            # names that, and saying nothing is sent would be wrong.
            if not config.should_use_collector():
                message += (
                    " The integration is now running in no-op mode therefore"
                    " no data will be sent to AppSignal."
                )
            print(message)
            return

        p = subprocess.Popen(
            [self.agent_path, "start", "--private"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.wait(timeout=1)
        returncode = p.returncode
        if returncode == 0:
            self._active = True
        else:
            output, _ = p.communicate()
            out = output.decode("utf-8")
            print(f"AppSignal agent is unable to start ({returncode}): ", out)

    def stop(self, config: Config) -> None:
        working_dir = config.option("working_directory_path") or "/tmp/appsignal"
        lock_path = os.path.join(working_dir, "agent.lock")
        try:
            with open(lock_path) as file:
                line = file.readline()
                pid = int(line.split(";")[2])
                os.kill(pid, signal.SIGTERM)
                # Give the agent time to send what it holds before this
                # process exits, which matters where the whole environment is
                # frozen once it does. When a collector is used the agent only
                # holds host, NGINX and StatsD metrics, so losing its last
                # batch is worth a shutdown that is two seconds quicker.
                if not config.should_use_collector():
                    time.sleep(2)
        except FileNotFoundError:
            logger.info("Agent lock file not found; not stopping the agent")

        self._active = False

    def diagnose(self, config: Config) -> bytes:
        config.set_private_environ()
        return subprocess.run(
            [self.agent_path, "diagnose", "--private"], capture_output=True
        ).stdout

    def version(self) -> bytes:
        return subprocess.run(
            [self.agent_path, "--version"], capture_output=True
        ).stdout.split()[1]

    def architecture_and_platform(self) -> list[str]:
        try:
            with open(self.platform_path) as file:
                return file.read().split("-", 1)
        except FileNotFoundError:
            return ["", ""]
