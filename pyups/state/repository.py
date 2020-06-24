from pathlib import Path
import logging
from logging.config import fileConfig
import sys
import io
import hashlib
import pyups.configuration as configuration
from pyups.state.model import State, calculate_state
from pyups.state.store import StateStore

READ_SIZE = 65536 * 8

def calculate_hash(path: Path) -> str:
    """
    Calculates a hash of the contents of the file, which may be used to detect
    when the contents of the file has changed.

    Parameters
    ----------
    path
        The path to the file. The hash will be calcualted for this file.
    
    Returns
    -------
    The calculated hash of the file's contents.
    """

    calculator = hashlib.sha1()
    with path.open('rb') as content:
        chunk = content.read(READ_SIZE)
        while chunk:
            calculator.update(chunk)
            chunk = content.read(READ_SIZE)

    return calculator.hexdigest()


class Change:
    """
    Describes the difference in the `State` of an item in the `Repository`.
    """
    def __init__(self, 
        repository_root: Path, 
        item: Path, 
        previous_state: State,
        new_state: State, 
        state_store: StateStore):

        self.__repository_root = repository_root
        self.__item = item
        self.__previous_state = previous_state
        self.__new_state = new_state
        self.__state_store = state_store
    
    @property
    def item(self):
        """
        Returns
        -------
        The item in the repository that was changed. This is expressed as a 
        path, relative to the repository's root, to the changed file.
        """
        return self.__item

    @property
    def item_path(self):
        """
        Returns
        -------
        The path to the item on the file system.
        """
        return self.__repository_root.joinpath(self.__item)

    @property
    def previous_state(self):
        """
        Returns
        -------
        The state of item that was last committed or stored in the store.
        """
        return self.__previous_state

    @property
    def new_state(self):
        """
        Returns
        -------
        A representation of the item's new state. This is the state that will be
        stored into the state store when `commit` is invoked.
        """
        return self.__new_state

    def commit(self) -> None:
        """
        Commits the change represented in this `Change` to the repository. Once
        committed, the `Repository.changes()` will no longer provide the item
        as a `Change` unless another change is made to the item.
        """
        self.__state_store.store_state(item=self.__item, state=self.__new_state)

class StateRepository:
    """
    Representation of the state of files in a directory. Provides facilities to
    look for files that have changed since their state was last stored.
    """
    def __init__(self, root_path: Path, data_directory_name: str = configuration.DATA_PATH):
        self.__root_path = root_path
        self.__data_path = root_path.joinpath(data_directory_name)
        self.__state_store = StateStore(self.__data_path)

    @property
    def root_path(self) -> Path:
        """
        Returns
        -------
        The path on the filesystem to the root of the repository. Items in the
        repository are files in the repository, expressed as a file path 
        relative to this root.
        """
        return self.__root_path 

    def content_paths(self) -> Path:
        """
        Locates items in the repository. It searches for items in the 
        repository's base directory and recursively searches the directories
        within it.

        Yields
        ------
        A *full filesystem* path to an item in the repository.
        """
        for path in self.__content_paths(path=self.__root_path):
            yield path

    def __content_paths(self, path: Path) -> Path:
        if path:
            for entry in path.iterdir():
                if entry.is_dir() and not self.__is_data_path(test_path=entry):
                    for subentry in self.__content_paths(path=entry):
                        yield subentry
                elif entry.is_file():
                    yield entry

    def __is_data_path(self, test_path: Path) -> bool:
        result = False
        if self.__data_path.exists():
            result = test_path.samefile(self.__data_path)
        return result

    def changes(self) -> Change:
        """
        Finds items that have changed in the repository.

        Yields
        -----
        A `Change` in the repository.
        """
        for entry in self.content_paths():
            logging.debug(f"Checking path: {entry}")
            relativized = entry.relative_to(self.__root_path)
            stored_state = self.__state_store.get_state(relativized)
            state_on_system = calculate_state(path=entry)

            if stored_state is None:
                # The entry has not yet been stored in the state.
                logging.debug(f"No state available for path. {entry} is new.")
                yield Change(repository_root=self.__root_path, 
                    item=relativized,
                    previous_state=None, 
                    new_state=state_on_system,
                    state_store=self.__state_store)
            else:
                if stored_state.has_changed(other=state_on_system):
                    logging.debug(f"State of file {entry} has changed")
                    item_state = calculate_state(entry)
                    yield Change(repository_root=self.__root_path, 
                        item=relativized, 
                        previous_state=stored_state, 
                        new_state=item_state, 
                        state_store=self.__state_store)

        # Search for items in the store that have been deleted. Since the above
        # loop has handled the case where the item still exists but has been
        # modified, this only has to handle the case where items have been
        # deleted from the repository.
        for entry in self.__state_store.stored_items():
            item_path = self.__root_path.joinpath(entry)
            if not item_path.exists():
                stored_state = self.__state_store.get_state(entry)
                yield Change(repository_root=self.__root_path,
                    item=entry,
                    previous_state=stored_state,
                    new_state=None,
                    state_store=self.__state_store)

