from __future__ import annotations


TRIPLE_PLATFORM_TAG = {
    # MacOS builds
    "x86_64-darwin": "macosx_10_9_x86_64",
    # Apple Silicon (and Apple Silicon w/ Intel emulation)
    "aarch64-darwin": "macosx_10_9_universal2.macosx_12_3_arm64",
    # Glibc Linux builds
    # manylinux2014 is a legacy tag defined as glibc >= 2.17,
    # we actually support glibc >= 2.15
    # https://peps.python.org/pep-0600/#legacy-manylinux-tags
    "aarch64-linux": "manylinux2014_aarch64.manylinux_2_15_aarch64",
    "x86_64-linux": "manylinux2014_x86_64.manylinux_2_15_x86_64",
    "i686-linux": "manylinux2014_i686.manylinux_2_15_i686",
    # MUSL Linux builds
    # our docs say we support v1.1.16 or above, but we can't
    # specify the patch
    # https://peps.python.org/pep-0656/
    "aarch64-linux-musl": "musllinux_1_1_aarch64",
    "x86_64-linux-musl": "musllinux_1_1_x86_64",
    "any": "any",
}
