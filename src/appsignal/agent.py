from __future__ import annotations

import os
import subprocess

from .config import Config

AGENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appsignal-agent")
agent_active = False


def is_agent_active():
    global agent_active
    return agent_active


def _reset_agent_active():
    global agent_active
    agent_active = False


def agent_is_active():
    global agent_active
    agent_active = True


def start_agent(config: Config):
    config.set_private_environ()
    p = subprocess.Popen(
        [AGENT_PATH, "start", "--private"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait(timeout=1)
    returncode = p.returncode
    if returncode == 0:
        agent_is_active()
    else:
        output, _ = p.communicate()
        out = output.decode("utf-8")
        print(f"AppSignal agent is unable to start ({returncode}): ", out)
