from __future__ import annotations

import os
import subprocess

from .config import Options, set_private_environ

AGENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appsignal-agent")


def start_agent(config: Options):
    set_private_environ(config)

    subprocess.Popen([AGENT_PATH, "start", "--private"])
