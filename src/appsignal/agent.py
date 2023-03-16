from __future__ import annotations

import os
import subprocess

from .config import Options
from typing import cast

AGENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appsignal-agent")

OPTION_PRIVATE_ENV_VAR = Options(
    name="_APPSIGNAL_APP_NAME",
    push_api_key="_APPSIGNAL_PUSH_API_KEY",
    environment="_APPSIGNAL_ENVIRONMENT",
    log_level="_APPSIGNAL_LOG_LEVEL",
)


def set_agent_defaults():
    os.environ["_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP"] = "true"


def start_agent(config: Options):
    set_agent_defaults()

    for option, value in config.items():
        if option in OPTION_PRIVATE_ENV_VAR:
            os.environ[cast(dict, OPTION_PRIVATE_ENV_VAR)[option]] = str(value)

    subprocess.Popen([AGENT_PATH])
