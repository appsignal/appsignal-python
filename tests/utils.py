import time
from typing import Callable


def wait_until(
    predicate: Callable[[], bool],
    message: str = "The predicate was not met",
    timeout: float = 1.0,
) -> None:
    start = time.time()

    while not predicate():
        if time.time() - start > timeout:
            raise TimeoutError(message + f"(after {timeout} seconds)")

        time.sleep(0.1)
