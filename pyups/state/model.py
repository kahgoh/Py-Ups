import hashlib
import logging
from pathlib import Path
from os import stat_result


class State:
    """
    Represents the state of an item or file at a point in time. 
    """
    def __init__(self, size: int, content_hash: str):
        self.__size = size
        self.__content_hash = content_hash

    @property
    def size(self) -> int:
        """
        Returns
        -------
        The size of the file in bytes.
        """
        return self.__size

    @property
    def content_hash(self) -> str:
        """
        Returns
        -------
        The hash of the file's contents.
        """
        return self.__content_hash

    def has_changed(self, other) -> bool:
        """
        Compares this `State` against another an instance to determine whether
        an item has changed or not. The state is considered to have changed if

        
        Parameters
        ----------
        other
            The other `State` object that this one will be compared against.

        Returns
        -------
        `True` if the states are different. Otherwise, `False` if there are all
        still the same.
        """
        if other == None:
            return True

        return (self.__size != other.size
                or self.__content_hash != other.content_hash)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return (self.size == other.size
                    and self.content_hash == other.content_hash)
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.size, self.content_hash))

    def __str__(self) -> str:
        return f"State(size={self.size}, content_hash='{self.content_hash}')"


class Builder:
    """
    This a builder implementation for building a `State` instance, which is supposed to be immutable.
    """
    def __init__(self):
        self.size = None
        self.content_hash = None

    """
    Builds an instance of the `State` object based on the values currently 
    stored. All values must have been set and supplied prior to calling 
    this.

    Returns
    -------
    The `State` instance that was built.
    """

    def build(self) -> State:
        assert self.size is not None and type(self.size) is int
        assert self.content_hash is not None and type(self.content_hash) is str

        return State(size=self.size, content_hash=self.content_hash)


READ_SIZE = 65536 * 8


def __calculate_hash(path: Path) -> str:
    calculator = hashlib.sha3_256()
    with path.open('rb') as content:
        chunk = content.read(READ_SIZE)
        while chunk:
            calculator.update(chunk)
            chunk = content.read(READ_SIZE)

    return calculator.hexdigest()


def calculate_state(path: Path) -> State:
    """
    Calculates the current state of the file at a given path.

    Parameters
    ----------
    path
        The state will be calculated for this file.

    Returns
    -------
    The `State` information for the `path`.
    """
    stats = path.stat()
    file_hash = __calculate_hash(path)
    logging.info(f"{path}, Size={stats.st_size}, Hash={file_hash}")
    return State(stats.st_size, file_hash)
