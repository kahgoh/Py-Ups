import hashlib
import logging
from pathlib import Path
from os import stat_result

class State:
    """
    Represents the state of an item or file at a point in time. 
    """

    def __init__(self, size: int, created: float, modified: float, hash: str):
        self.__size = size
        self.__created = created
        self.__modified = modified
        self.__hash = hash

    @property
    def size(self) -> int:
        """
        Returns
        -------
        The size of the file in bytes.
        """
        return self.__size

    @property
    def created(self) -> float:
        """
        Returns
        -------
        The time when the file was first created.
        """
        return self.__created

    @property
    def modified(self) -> float:
        """
        Returns
        -------
        The time when the file was last modified.
        """
        return self.__modified

    @property
    def hash(self) -> float:
        """
        Returns
        -------
        The hash of the file's contents.
        """
        return self.__hash

    def has_changed(self, stats: stat_result) -> bool :
        """Compares this `State` against those stored in a `state_result` (from 
        `Path.stat <https://docs.python.org/3/library/pathlib.html#pathlib.Path.stat>`)
        to determine whether the state has changed or not. It has considered to
        have changed if the either the size, modified or created times differ.
        
        Parameters
        ----------
        stats
            The `stat_result` for the file. The size, modified and created times
            will be compared against those stored in this instancee to determine
            if the file has changed.

        Returns
        -------
        `True` if either the size, modified or created times are different.
        Otherwise, `False` if there are all still the same.
        """

        return self.__size != stats.st_size or self.__created != stats.st_ctime or self.__modified != stats.st_mtime

class Builder:
    """
    This a builder implementation for building a `State` instance, which is supposed to be immutable.
    """
    def __init__(self):
        self.size = None
        self.created = None
        self.modified = None
        self.hash = None
    
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
        assert self.created is not None and type(self.created) is float
        assert self.modified is not None and type(self.modified) is float
        assert self.hash is not None and type(self.hash) is str

        return State(size=self.size, created=self.created, modified=self.modified, hash=self.hash)

READ_SIZE = 65536 * 8

def __calculate_hash(path: Path) -> str:
    calculator = hashlib.sha1()
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
    logging.info(f"{path}, Size={stats.st_size}, Created={stats.st_ctime}, Modified={stats.st_mtime}, Hash={file_hash}");
    return State(stats.st_size, stats.st_ctime, stats.st_mtime, file_hash)