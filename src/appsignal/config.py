from typing import TypedDict


class Options(TypedDict, total=False):
    name: str
    environment: str
    push_api_key: str
