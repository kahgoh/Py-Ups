from pathlib import Path
from pyups.state.model import State
import pyups.state.model as state
import logging
import os

class StateStore:
    """
    Provides facilities for storing information about the state of files.
    """
    __STATE_STORE_PATH = Path("state")

    __PARSERS = {
        "size": int,
        "created": float,
        "modified": float,
        "hash": lambda x: x
    }

    def __init__(self, store_root: Path):
        """
        Parameters
        ----------
        store_root
            The root directory where the states will be stored in the filesystem.
        """
        self.__store_path = store_root.joinpath(StateStore.__STATE_STORE_PATH)

    def store_state(self, item: Path, state: State) -> None:
        """
        Stores the state of an item in the store.
    
        Parameters
        ----------
        path
            The file's path within the repository. This should be relative to the
            repository's root.

        state
            The state of the file. Set this to `None` if the entry should be
            deleted from the store instead.
        """

        state_file = self.__store_path.joinpath(item)
        if state:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            with state_file.open(mode="wb") as entry:
                content = [StateStore.__contentAsBytes(state, attribute) for attribute in StateStore.__PARSERS]
                entry.writelines(content)
        else:
            logging.debug(f"Clearing state for {item}.")
            if state_file.exists():
                state_file.unlink()

  
    def stored_items(self) -> Path:
        for item in self.__stored_items(self, from_item=Path(".")):
            yield item

    @staticmethod
    def __stored_items(self, from_item: Path) -> Path:
        """
        Yields items in the store.

        Parameters
        ----------
        item
            The search for items in the store will begin from this `item`. May 
            be set to `None` if the entire store should be searched. If given,
            the item is expected to be a directory.
        
        Yields
        ------
        Items that have been previously stored in the store.
        """
        path_in_store = self.__store_path.joinpath(from_item)
        
        if path_in_store.exists() and path_in_store.is_dir():
            for candidate in path_in_store.iterdir():
                child_item = candidate.relative_to(self.__store_path)
                if candidate.is_dir() and not (candidate.name == ".pyups"):
                    for item in self.__stored_items(self=self, from_item=child_item):
                        yield item
                elif candidate.is_file():
                    yield child_item
        else:
            logging.debug(f"Store path {path_in_store} does not exist. Nothing to yield.")

    @staticmethod
    def __contentAsBytes(source, attribute) -> bytes:
        value = getattr(source, attribute)
        return bytes(f"{attribute}: {value}{os.linesep}", "utf-8")

    def get_state(self, path: Path) -> State:
        """
        Obtains the stored state of a file.

        Parameters
        ----------
        path
            The file's path.

        Returns
        -------
        The state stored that was stored for the given `path` or `None` if there is no state stored.
        """
        state_file = self.__store_path.joinpath(path)

        result = None
        if state_file.exists() and state_file.is_file():
            with state_file.open(mode="rt") as entry:
                builder = state.Builder()
                for line in entry:
                    key, value = [word.strip() for word in line.split(sep=":", maxsplit=1)]
                    parser = StateStore.__PARSERS[key]
                    setattr(builder, key, parser(value))    
            result = builder.build()
            logging.debug(f"Stored: {path}, Size={result.size}, Created={result.created}, Modified={result.modified}, Hash={result.hash}");
        else:
            logging.debug(f"No state stored yet for {path}")

        return result
