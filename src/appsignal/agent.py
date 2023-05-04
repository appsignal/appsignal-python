from __future__ import annotations

import os
import subprocess

from .config import Config

AGENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appsignal-agent")


def start_agent(config: Config):
    config.set_private_environ()

    subprocess.Popen([AGENT_PATH, "start", "--private"])
