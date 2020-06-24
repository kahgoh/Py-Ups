import logging
from pyups.state.model import State, calculate_state
from pytest import fixture
from pathlib import Path

def write_content(path: Path, content: str) -> None:
    logging.info(f"Writing content to: {path}")
    with path.open(mode="w") as file:
        file.write(content)
 
def test_no_change(tmp_path) -> None:
    """
    Test that `State.has_changed` returns `False` if the content has not changed.
    """
    path = tmp_path.joinpath("content")
    write_content(path, "Initial content")

    state = calculate_state(path)
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == False

def test_changed_different_content(tmp_path) -> None:
    """
    Test that `State.has_changed` returns `True` if the content has changed.
    """
    path = tmp_path.joinpath("content")
    write_content(path, "Initial content")
    state = calculate_state(path)

    write_content(path, "New content")
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == True

def test_changed_content_rewritten(tmp_path) -> None:
    """
    Test that `State.has_changed` returns `False` if the file has been modified,
    even when the actual contents has not (e.g it has been re-written with the
    exact same content).
    """
    path = tmp_path.joinpath("content")
    content = "This is the content of this file."
    write_content(path, content)
    state = calculate_state(path)

    # Write the same content to the file.
    write_content(path, content)
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == False

def test_changed_content_same_length(tmp_path) -> None:
    """
    Test that `State.has_changed` is able to detect changes when the new content
    is of the same length as the original content.
    """
    path = tmp_path.joinpath("content")
    write_content(path, "abcdef")
    state = calculate_state(path)

    write_content(path, "abcdeg")
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == True
