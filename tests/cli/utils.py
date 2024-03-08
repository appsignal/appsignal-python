from __future__ import annotations

from contextlib import contextmanager


@contextmanager
def mock_input(mocker, *pairs: tuple[str, str | None]):
    expected_unanswered = pairs[-1][1] is None

    prompt_calls = [mocker.call(prompt) for (prompt, _) in pairs]
    answers = [answer for (_, answer) in pairs if answer is not None]
    mock = mocker.patch("builtins.input", side_effect=answers)
    try:
        yield
    except StopIteration as e:
        if not expected_unanswered:
            raise e
    finally:
        assert prompt_calls == mock.mock_calls
