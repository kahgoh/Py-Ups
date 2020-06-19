from collections import Counter
import logging
from pathlib import Path
import pytest
from pyups.state.store import StateStore
from pyups.state.repository import StateRepository, Change

"""
This describes the initial content that will be set up for the tests. The keys
are the names of the file or directory. If the value, is a `str`, then it is
file with the content set to the value. If the value is `dict`, then it is a
directory whose contents are described by the sub-dictionary.
"""
CONTENT = {
    "document": 
"""tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
    Creates a temporary directory in the most secure
    manner possible. There are no race conditions in
    the directory’s creation. The directory is 
    readable, writable, and searchable only by the
    creating user ID.""",
    "story.doc": 
"""Once upon a time there were three bears who lived in a
house in the forest. Therewas a great big father bear, a 
middle-sized mother bear and a tiny baby bear. One 
morning, their breakfast porridge was too hot to eat, so
they decided to go for a walk in the forest.""",
    "names.txt": "Adam Eve Jack Jill Hansel Gretel",
    "reports/scores.csv": 
"""1, 2, 3
4, 5, 6
"""
}

@pytest.fixture
def repository_path(tmp_path) -> Path:
    """
    Prepares content for change detection tests.

    Parameters
    ----------
    tmp_path
        Temmporary directory where the content will be placed. The tests will be
        able to use this location as repository of files.
    """

    for (name, entry) in CONTENT.items():
        file_path = tmp_path.joinpath(name)
        parent_path = file_path.parent
        if not parent_path.exists():
            parent_path.mkdir(parents=True)

        with file_path.open(mode="w") as file:
            file.write(entry)

    logging.info(f"Sample content created in: {tmp_path}")

    return tmp_path

def test_changes_before_commits(repository_path: Path) -> None:
    expected = [Path(x) for x in CONTENT.keys() ]

    repository = StateRepository(root_path=repository_path)
    actual = [c.item for c in repository.changes()]

    assert Counter(expected) == Counter(actual)

def test_previous_state_before_commits(repository_path: Path) -> None:
    expected = [Path(x) for x in CONTENT.keys() ]
    repository = StateRepository(root_path=repository_path)

    none_previous_state = [c.item for c in repository.changes() if c.previous_state == None ]

    assert Counter(expected) == Counter(none_previous_state)

def test_no_changes_after_commit(repository_path: Path) -> None:
    repository = StateRepository(root_path=repository_path)
    for c in repository.changes():
        c.commit()

    changes_after_commit = [c.item for c in repository.changes()]

    assert len(changes_after_commit) == 0

@pytest.mark.parametrize("item", CONTENT.keys())
def test_changes_after_commit(repository_path: Path, item: str) -> None:
    repository = StateRepository(root_path=repository_path)
    for c in repository.changes():
        c.commit()

    item_path = repository_path.joinpath(item)
    with item_path.open(mode="a") as f:
        f.write("new content")

    changes = [c.item for c in repository.changes()]

    assert [Path(item)] == changes 

@pytest.mark.parametrize("to_delete", CONTENT.keys())
def test_delete_after_commit(repository_path: Path, to_delete: str) -> None:
    repository = StateRepository(root_path=repository_path)
    for c in repository.changes():
        c.commit()

    to_delete_path = repository_path.joinpath(to_delete)
    to_delete_path.unlink()

    changes = [c for c in repository.changes()]
    changed_items = [c.item for c in changes]

    # Only one change to represent the deleted item.
    assert [Path(to_delete)] == changed_items

    # The change should represent a delete.
    assert changes[0].previous_state != None and changes[0].new_state == None

@pytest.mark.parametrize("to_delete", CONTENT.keys())
def test_changes_after_delete_commit(repository_path: Path, to_delete: str) -> None:
    repository = StateRepository(root_path=repository_path)
    for c in repository.changes():
        c.commit()

    to_delete_path = repository_path.joinpath(to_delete)
    to_delete_path.unlink()

    for c in repository.changes():
        # The change should just be a delete.
        assert c.new_state == None
        c.commit()

    # After committing the deletes, there should be no more changes.
    assert [c for c in repository.changes()] == []