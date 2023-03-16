from typing import Any
from runpy import run_path
import os
import stat
import hashlib
import tarfile
import shutil

import requests
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_relative(filename):
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


APPSIGNAL_AGENT_CONFIG = run_relative("agent.py")["APPSIGNAL_AGENT_CONFIG"]
PLATFORM_TAG_TRIPLE = run_relative("platform.py")["PLATFORM_TAG_TRIPLE"]


def platform_triple(platform: str):
    return PLATFORM_TAG_TRIPLE[platform]


def triple_filename(triple: str):
    return APPSIGNAL_AGENT_CONFIG["triples"][triple]["static"]["filename"]


def triple_checksum(triple: str):
    return APPSIGNAL_AGENT_CONFIG["triples"][triple]["static"]["checksum"]


def triple_urls(triple: str):
    mirrors = APPSIGNAL_AGENT_CONFIG["mirrors"]
    version = APPSIGNAL_AGENT_CONFIG["version"]
    filename = triple_filename(triple)

    return [f"{mirror}/{version}/{filename}" for mirror in mirrors]


def rm(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


class DownloadError(Exception):
    pass


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """
        This occurs immediately before each build.

        Any modifications to the build data will be seen by the build target.
        """

        if "_APPSIGNAL_BUILD_PLATFORM" not in os.environ:
            print("_APPSIGNAL_BUILD_PLATFORM is not set; exiting...")
            print("Hint: you may wish to run `hatch run build:all` instead?")
            exit(1)

        platform_tag = os.environ["_APPSIGNAL_BUILD_PLATFORM"]

        build_data["tag"] = f"py3-none-{platform_tag}"
        build_data["pure_python"] = False

        triple = platform_triple(platform_tag)

        agent_path = os.path.join(self.root, "src", "appsignal", "appsignal-agent")
        rm(agent_path)

        tempdir_path = os.path.join(self.root, "tmp", triple)
        os.makedirs(tempdir_path, exist_ok=True)

        tempagent_path = os.path.join(tempdir_path, "appsignal_agent")

        if not os.path.exists(tempagent_path):
            temptar_path = os.path.join(tempdir_path, triple_filename(triple))

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

            print(f"Extracted agent binary to {tempagent_path}")
            rm(temptar_path)
        else:
            print(f"Using cached agent binary at {tempagent_path}")

        shutil.copy(tempagent_path, agent_path)
        os.chmod(agent_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

        print(f"Copied agent binary to {agent_path}")
