import hashlib
import os
import shutil
import stat
import subprocess
import sysconfig
import tarfile
from runpy import run_path
from typing import Any, Dict

import requests
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_relative(filename):
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


APPSIGNAL_AGENT_CONFIG = run_relative("agent.py")["APPSIGNAL_AGENT_CONFIG"]
TRIPLE_PLATFORM_TAG = run_relative("platform.py")["TRIPLE_PLATFORM_TAG"]


def triple_filename(triple: str):
    return APPSIGNAL_AGENT_CONFIG["triples"][triple]["static"]["filename"]


def triple_checksum(triple: str):
    return APPSIGNAL_AGENT_CONFIG["triples"][triple]["static"]["checksum"]


def triple_urls(triple: str):
    mirrors = APPSIGNAL_AGENT_CONFIG["mirrors"]
    version = APPSIGNAL_AGENT_CONFIG["version"]
    filename = triple_filename(triple)

    return [f"{mirror}/{version}/{filename}" for mirror in mirrors]


def rm(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def should_download(agent_path: str, version_path: str) -> bool:
    if not os.path.exists(agent_path):
        return True

    if not os.path.exists(version_path):
        return True

    with open(version_path, "r") as version:
        return version.read() != APPSIGNAL_AGENT_CONFIG["version"]


def this_triple() -> str:
    platform = sysconfig.get_platform()
    [os, *_, arch] = platform.split("-")

    if os == "macosx":
        os = "darwin"

    if arch == "universal2":
        arch = "arm64"

    if os == "linux":
        ldd_run = subprocess.run(["ldd", "--version"], capture_output=True)
        if b"musl" in ldd_run.stderr:
            os = "linux-musl"

    return f"{arch}-{os}"


class DownloadError(Exception):
    pass


class CustomBuildHook(BuildHookInterface):
    def initialize(self, _version: str, build_data: Dict[str, Any]) -> None:
        """
        This occurs immediately before each build.

        Any modifications to the build data will be seen by the build target.
        """

        triple = None

        if "_APPSIGNAL_BUILD_TRIPLE" in os.environ:
            triple = os.environ["_APPSIGNAL_BUILD_TRIPLE"]
        else:
            triple = this_triple()
            print(
                f"_APPSIGNAL_BUILD_TRIPLE not set; building for local triple ({triple})"
            )

        platform_tag = TRIPLE_PLATFORM_TAG[triple]

        build_data["tag"] = f"py3-none-{platform_tag}"
        build_data["pure_python"] = False

        agent_path = os.path.join(self.root, "src", "appsignal", "appsignal-agent")

        if os.environ.get(
            "_APPSIGNAL_BUILD_AGENT_PATH", ""
        ).strip() == "--keep-agent" and os.path.isfile(agent_path):
            print(f"Using existing agent binary at {agent_path}")
            return

        rm(agent_path)

        tempdir_path = os.path.join(self.root, "tmp", triple)
        os.makedirs(tempdir_path, exist_ok=True)

        tempagent_path = os.path.join(tempdir_path, "appsignal_agent")
        tempversion_path = os.path.join(tempdir_path, "version")

        if os.environ.get("_APPSIGNAL_BUILD_AGENT_PATH", "").strip() != "":
            tempagent_path = os.path.abspath(
                os.environ["_APPSIGNAL_BUILD_AGENT_PATH"].strip()
            )

            if not os.path.isfile(tempagent_path):
                print(
                    f"Custom agent binary at {tempagent_path} is not a file; exiting..."
                )
                exit(1)

            print(f"Using custom agent binary at {tempagent_path}")
        elif should_download(tempagent_path, tempversion_path):
            temptar_path = os.path.join(tempdir_path, triple_filename(triple))

            rm(tempagent_path)
            rm(tempversion_path)
            rm(temptar_path)

            with open(temptar_path, "wb") as temptar:
                for url in triple_urls(triple):
                    try:
                        r = requests.get(url, allow_redirects=True)
                        if r.status_code != 200:
                            raise DownloadError("Status code is not 200")

                        if hashlib.sha256(r.content).hexdigest() != triple_checksum(
                            triple
                        ):
                            raise DownloadError("Checksum does not match")

                        temptar.write(r.content)
                    except DownloadError as e:
                        print(f"Something went wrong downloading from `{url}`: {e}")
                    else:
                        break
                else:
                    print("Failed to download from any mirrors; exiting...")
                    exit(1)

            print(f"Downloaded agent tarball for {triple}")

            with tarfile.open(temptar_path, "r:*") as tar:
                with open(tempagent_path, "wb") as agent:
                    tar_agent = tar.extractfile("appsignal-agent")
                    if tar_agent is not None:
                        agent.write(tar_agent.read())
                    else:
                        print("Failed to extract agent binary; exiting...")
                        exit(1)

            with open(tempversion_path, "w") as version:
                version.write(APPSIGNAL_AGENT_CONFIG["version"])

            print(f"Extracted agent binary to {tempagent_path}")
            rm(temptar_path)
        else:
            print(f"Using cached agent binary at {tempagent_path}")

        shutil.copy(tempagent_path, agent_path)
        os.chmod(agent_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

        print(f"Copied agent binary to {agent_path}")
