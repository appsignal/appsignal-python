from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Config


@dataclass
class Agent:
    package_path: Path = Path(__file__).parent
    agent_path: Path = package_path / "appsignal-agent"
    platform_path: Path = package_path / "_appsignal_platform"
    active: bool = False

    def start(self, config: Config) -> None:
        if self.architecture_and_platform() == ["any"]:
            print(
                "AppSignal agent is not available for this platform. "
                "The integration is now running in no-op mode. "
                "No data will be sent to AppSignal."
            )
            return
        
        config.set_private_environ()

        p = subprocess.Popen(
            [self.agent_path, "start", "--private"],
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

    def diagnose(self, config: Config) -> bytes | None:
        if self.architecture_and_platform() == ["any"]:
            print(
                "AppSignal agent is not available for this platform. "
                "It is not possible to run diagnostics."
            )
            return None

        config.set_private_environ()
        return subprocess.run(
            [self.agent_path, "diagnose", "--private"], capture_output=True
        ).stdout

    def version(self) -> bytes | None:
        if self.architecture_and_platform() == ["any"]:
            print(
                "AppSignal agent is not available for this platform. "
                "It is not possible to obtain the agent version."
            )
            return None
        return subprocess.run(
            [self.agent_path, "--version"], capture_output=True
        ).stdout.split()[1]

    def architecture_and_platform(self) -> list[str]:
        try:
            with open(self.platform_path) as file:
                return file.read().split("-", 1)
        except FileNotFoundError:
            return ["", ""]

agent = Agent()

@dataclass
class Collector:
    package_path: Path = Path(__file__).parent
    agent_path: Path = package_path / "appsignal-collector"
    platform_path: Path = package_path / "_appsignal_platform"
    active: bool = False

    def start(self, config: Config) -> None:
        if self.architecture_and_platform() == ["any"]:
            print(
                "AppSignal collector is not available for this platform. "
                "The integration is now running in no-op mode. "
                "No data will be sent to AppSignal."
            )
            return
        
        config.set_public_environ()

        p = subprocess.Popen(
            [self.agent_path, "start"]
        )
        # p.wait(timeout=1)
        # returncode = p.returncode
        # if returncode == 0:
        #     self.active = True
        # else:
        #     output, _ = p.communicate()
        #     out = output.decode("utf-8")
        #     print(f"AppSignal collector is unable to start ({returncode}): ", out)

    def diagnose(self, config: Config) -> bytes | None:
        print(
            "AppSignal collector does not support diagnostics."
        )
        return None

    def version(self) -> bytes | None:
        if self.architecture_and_platform() == ["any"]:
            print(
                "AppSignal collector is not available for this platform. "
                "It is not possible to obtain the collector version."
            )
            return None
        
        return subprocess.run(
            [self.agent_path, "--version"], capture_output=True
        ).stdout.split()[1]

    def architecture_and_platform(self) -> list[str]:
        try:
            with open(self.platform_path) as file:
                return file.read().split("-", 1)
        except FileNotFoundError:
            return ["", ""]

collector = Collector()
