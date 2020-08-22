import logging
from pyups.state.model import State, calculate_state
from pytest import fixture
from pathlib import Path
 
def test_no_change(tmp_path) -> None:
    """
    Test that `State.has_changed` returns `False` if the content has not changed.
    """
    path = tmp_path.joinpath("content")
    path.write_text("Initial content")

    state = calculate_state(path)
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == False

def test_changed_different_content(tmp_path) -> None:
    """
    Test that `State.has_changed` returns `True` if the content has changed.
    """
    path = tmp_path.joinpath("content")
    path.write_text("Initial content")
    state = calculate_state(path)

    path.write_text("New content")
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
    path.write_text(content)
    state = calculate_state(path)

    # Write the same content to the file.
    path.write_text(content)
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == False

def test_changed_content_same_length(tmp_path) -> None:
    """
    Test that `State.has_changed` is able to detect changes when the new content
    is of the same length as the original content.
    """
    path = tmp_path.joinpath("content")
    path.write_text("abcdef")
    state = calculate_state(path)

    path.write_text("abcdeg")
    updated_state = calculate_state(path)
    assert state.has_changed(updated_state) == True
