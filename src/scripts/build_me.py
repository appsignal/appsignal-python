import os
import sysconfig
import subprocess
from runpy import run_path


def run_relative(filename):
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


def this_triple():
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


TRIPLE_PLATFORM_TAG = run_relative("platform.py")["TRIPLE_PLATFORM_TAG"]

platform = TRIPLE_PLATFORM_TAG[this_triple()]
result = os.system(f"_APPSIGNAL_BUILD_PLATFORM={platform} hatch build -t wheel")
exit(result)
