PLATFORM_TAG_TRIPLE = {
    # MacOS builds
    "macosx_10_9_x86_64": "x86_64-darwin",
    "macosx_12_3_arm64": "arm64-darwin",
    # Intel w/ PowerPC emulation
    "macosx_10_9_universal": "x86_64-darwin",
    # Apple Silicon w/ Intel emulation
    "macosx_10_9_universal2": "x86_64-darwin",
    # Glibc Linux builds
    # manylinux2014 is a legacy tag defined as glibc >= 2.17
    # https://peps.python.org/pep-0600/#legacy-manylinux-tags
    "manylinux2014_aarch64": "aarch64-linux",
    "manylinux2014_x86_64": "x86_64-linux",
    "manylinux2014_i686": "i686-linux",
    # we actually support glibc >= 2.15, so these would be best
    "manylinux_2_15_aarch64": "aarch64-linux",
    "manylinux_2_15_x86_64": "x86_64-linux",
    "manylinux_2_15_i686": "i686-linux",
    # MUSL Linux builds
    # our docs say we support v1.1.16 or above, but we can't
    # specify the patch
    # https://peps.python.org/pep-0656/
    "musllinux_1_1_aarch64": "aarch64-linux-musl",
    "musllinux_1_1_x86_64": "x86_64-linux-musl",
    # FreeBSD builds
    # TODO: i made the platform tag up, check that it is correct
    "freebsd_x86_64": "x86_64-freebsd",
}
