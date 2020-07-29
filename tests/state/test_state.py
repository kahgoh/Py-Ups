from pyups.state.model import State

def test_equals() -> None:
    assert State(size=100, content_hash="abcdef") == State(size=100, content_hash="abcdef")

def test_equals_with_different_size() -> None:
    assert State(size=99, content_hash="abcdef") != State(size=100, content_hash="abcdef")

def test_equals_with_different_hash() -> None:
    assert State(size=100, content_hash="abcdeg") != State(size=100, content_hash="abcdef")

def test_equals_with_none() -> None:
    assert State(size=100, content_hash="abcdef") != None

def test_equals_with_other() -> None:
    assert State(size=100, content_hash="abcdef") != ""

