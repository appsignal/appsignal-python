from appsignal.something import add


def test_something():
    # uncomment the following to trigger a type error:
    # assert add(2, 2) == 4
    assert add("foo", "bar") == "foobar"
