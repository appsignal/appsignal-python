import os
from runpy import run_path


def run_relative(filename):
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


PLATFORM_TAG_TRIPLE = run_relative("platform.py")["PLATFORM_TAG_TRIPLE"]

for platform in PLATFORM_TAG_TRIPLE.keys():
    result = os.system(f"_APPSIGNAL_BUILD_PLATFORM={platform} hatch build -t wheel")
    if result != 0:
        break
