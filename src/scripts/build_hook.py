from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import sysconfig
import tarfile
from runpy import run_path
from typing import Any, Union, Literal

import requests
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_relative(filename: str) -> dict[str, Any]:
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))

Binary = Literal["agent", "collector"]
BINARIES: list[Binary] = ["agent", "collector"]

DEFAULT_ENABLED: dict[Binary, bool] = {
    "agent": True,
    "collector": False,
}

def binary_enabled_env_var(binary: Binary) -> str:
    return f"_APPSIGNAL_BUILD_{binary.upper()}_ENABLED"

APPSIGNAL_CONFIG: dict[Binary, Any] = {
    "agent": run_relative("agent.py")["APPSIGNAL_AGENT_CONFIG"],
    "collector": run_relative("collector.py")["APPSIGNAL_COLLECTOR_CONFIG"],
}

TRIPLE_PLATFORM_TAG = run_relative("platform.py")["TRIPLE_PLATFORM_TAG"]


def triple_filename(binary: Binary, triple: str) -> str:
    return APPSIGNAL_CONFIG[binary]["triples"][triple]["static"]["filename"]


def triple_checksum(binary: Binary, triple: str) -> str:
    return APPSIGNAL_CONFIG[binary]["triples"][triple]["static"]["checksum"]


def triple_urls(binary: Binary, triple: str) -> list[str]:
    mirrors = APPSIGNAL_CONFIG[binary]["mirrors"]
    version = APPSIGNAL_CONFIG[binary]["version"]
    filename = triple_filename(binary, triple)

    return [f"{mirror}/{version}/{filename}" for mirror in mirrors]

def binary_version(binary: Binary) -> str:
    return APPSIGNAL_CONFIG[binary]["version"]

def binary_enabled(binary: Binary) -> bool:
    return os.environ.get(
        binary_enabled_env_var(binary),
        str(DEFAULT_ENABLED[binary])
    ).lower() not in ["0", "no", "false"]

def rm(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def should_download(binary: Binary, binary_path: str, version_path: str) -> bool:
    if not os.path.exists(binary_path):
        return True

    if not os.path.exists(version_path):
        return True

    with open(version_path) as version:
        return version.read() != APPSIGNAL_CONFIG[binary]["version"]


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
    def initialize(self, _version: str, build_data: dict[str, Any]) -> None:
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

        binary_filenames = {
            "agent": "appsignal-agent",
            "collector": "appsignal-collector",
        }

        agent_path = os.path.join(self.root, "src", "appsignal", binary_filenames["agent"])
        collector_path = os.path.join(self.root, "src", "appsignal", binary_filenames["collector"])

        binary_paths: dict[Binary, str] = {
            "agent": agent_path,
            "collector": collector_path,
        }

        binary_path_env_vars: dict[Binary, str] = {
            "agent": "_APPSIGNAL_BUILD_AGENT_PATH",
            "collector": "_APPSIGNAL_BUILD_COLLECTOR_PATH",
        }

        binary_path_keep_flags: dict[Binary, str] = {
            "agent": "--keep-agent",
            "collector": "--keep-collector",
        }

        platform_path = os.path.join(
            self.root, "src", "appsignal", "_appsignal_platform"
        )

        for binary in BINARIES:
            if not binary_enabled(binary):
                print(f"Skipping {binary} binary download; set {binary_enabled_env_var(binary)}=1 to enable")
                continue

            binary_filename = binary_filenames[binary]
            binary_path = binary_paths[binary]
            binary_path_env_var = binary_path_env_vars[binary]
            binary_path_keep_flag = binary_path_keep_flags[binary]

            if os.environ.get(binary_path_env_var, "").strip() == binary_path_keep_flag:
                if os.path.isfile(binary_path):
                    print(f"Using existing {binary} binary at {binary_path}")
                    return
                else:
                    print(
                        f"{binary_path_keep_flag} specified but no {binary} binary found at {binary_path}; exiting..."
                    )
                    exit(1)
        
            rm(binary_path)

            with open(platform_path, "w") as platform:
                platform.write(triple)

            if triple == "any":
                print(f"Skipping {binary} binary download for `any` triple")
                return

            tempdir_path = os.path.join(self.root, "tmp", triple)
            os.makedirs(tempdir_path, exist_ok=True)

            tempbinary_path = os.path.join(tempdir_path, binary_filename)
            tempversion_path = os.path.join(tempdir_path, f"{binary}-version")

            if os.environ.get(binary_path_env_var, "").strip() != "":
                tempbinary_path = os.path.abspath(
                    os.environ[binary_path_env_var].strip()
                )

                if not os.path.isfile(tempbinary_path):
                    print(
                        f"Custom {binary} binary at {tempbinary_path} is not a file; exiting..."
                    )
                    exit(1)

                print(f"Using custom {binary} binary at {tempbinary_path}")
            elif should_download(binary, tempbinary_path, tempversion_path):
                temptar_path = os.path.join(tempdir_path, triple_filename(binary, triple))

                rm(tempbinary_path)
                rm(tempversion_path)
                rm(temptar_path)

                with open(temptar_path, "wb") as temptar:
                    for url in triple_urls(binary, triple):
                        try:
                            r = requests.get(url, allow_redirects=True)
                            if r.status_code != 200:
                                raise DownloadError(f"Status code is not 200: {r.status_code} {r.reason}")

                            if hashlib.sha256(r.content).hexdigest() != triple_checksum(binary, triple):
                                raise DownloadError("Checksum does not match")

                            temptar.write(r.content)
                        except DownloadError as e:
                            print(f"Something went wrong downloading {binary} binary from `{url}`: {e}")
                        else:
                            break
                    else:
                        print(f"Failed to download {binary} binary from any mirrors; exiting...")
                        rm(temptar_path)
                        exit(1)

                print(f"Downloaded {binary} tarball for {triple}")

                with tarfile.open(temptar_path, "r:*") as tar:
                    with open(tempbinary_path, "wb") as binary_file:
                        tar_binary = tar.extractfile(binary_filename)
                        if tar_binary is not None:
                            binary_file.write(tar_binary.read())
                        else:
                            print(f"Failed to extract {binary} binary; exiting...")
                            exit(1)

                with open(tempversion_path, "w") as version:
                    version.write(binary_version(binary))

                print(f"Extracted {binary} binary to {tempbinary_path}")
                rm(temptar_path)
            else:
                print(f"Using cached {binary} binary at {tempbinary_path}")

            shutil.copy(tempbinary_path, binary_path)
            os.chmod(binary_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

            print(f"Copied {binary} binary to {binary_path}")
