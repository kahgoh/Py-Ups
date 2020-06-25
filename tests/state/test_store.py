from pathlib import Path
from pyups.state.model import State
from pyups.state.store import StateStore

def test_empty_store(tmp_path: Path) -> None:
    store = StateStore(store_root=tmp_path)
    assert [x for x in store.stored_items()] == []

def test_store_item(tmp_path: Path) -> None:
    item = Path("sample_item")
    store = StateStore(store_root=tmp_path)
    state = State(size=147, hash="acef468")
    store.store_state(item=item, state=state)

    assert [x for x in store.stored_items()] == [item]

def test_get_item(tmp_path: Path) -> None:
    item = Path("sample_item")
    store = StateStore(store_root=tmp_path)
    state = State(size=147, hash="acef468")
    store.store_state(item=item, state=state)

    assert store.get_state(item) == State(size=147, hash="acef468")
