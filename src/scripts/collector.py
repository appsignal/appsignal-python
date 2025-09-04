APPSIGNAL_COLLECTOR_CONFIG = {
    "version": "v0.7.1",
    "mirrors": [
        "https://github.com/appsignal/appsignal-collector/releases/download",
    ],
    "triples": {
        "x86_64-darwin": {
            "static": {
                "checksum": "a5813b5bbd15321de27d72c7d4e605fe3e11e636f60bcb155c27271bf98345aa",
                "filename": "appsignal-collector-x86_64-apple-darwin.tar.gz",
            },
        },
        "aarch64-darwin": {
            "static": {
                "checksum": "e33d5f270569ff386b2b3c418b2b77d4f7dbfd6c37ae78315a5912391db1ff01",
                "filename": "appsignal-collector-aarch64-apple-darwin.tar.gz",
            },
        },
        "aarch64-linux": {
            "static": {
                "checksum": "424533bb3b663f02bf1d82bc6e80923fb6ecdd9f98ba76c84faa0fb449b0b8b5",
                "filename": "appsignal-collector-aarch64-unknown-linux-gnu.tar.gz",
            },
        },
        "x86_64-linux": {
            "static": {
                "checksum": "105db60c8e9c5e6723e53ab70825d665c0f84599ac8043f84e62697f27eb8c74",
                "filename": "appsignal-collector-x86_64-unknown-linux-gnu.tar.gz",
            },
        },
        "aarch64-linux-musl": {
            "static": {
                "checksum": "67860b93a6fe9af085dadc919a8849305fc532da76aca8f04619b3f774090ba3",
                "filename": "appsignal-collector-aarch64-unknown-linux-musl.tar.gz",
            },
        },
        "x86_64-linux-musl": {
            "static": {
                "checksum": "e9468dcf082741c99ea67a0d08fbc56e0f35a21953726bfabfa4bde631f0ff33",
                "filename": "appsignal-collector-x86_64-unknown-linux-musl.tar.gz",
            },
        },
    },
}
