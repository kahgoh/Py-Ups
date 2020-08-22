from pathlib import Path
import os
import pyAesCrypt
import tempfile
from typing import Callable

BUFFER_SIZE = 65536 * 8

def encrypted_file(source: Path, password: str) -> (Path, Callable[[], None]):
    """
    Encrypts a file to a temporary file. The temporary file is also removed by
    the provided clean up function.

    Parameters
    ----------
    source
        The `Path` to the file that will be encrypted.

    password
        The password that the file will be encrypted with. It will need to be
        provided for the file to be decrypted again.

    Returns
    -------
    A tuple consisting of the `Path` to the encrypted file and a function that,
    when called, will remove the temporary file.
    """
    encrypted_file = tempfile.NamedTemporaryFile().name
    pyAesCrypt.encryptFile(
        infile = source.as_posix(),
        outfile = encrypted_file,
        passw = password,
        bufferSize = BUFFER_SIZE
    )

    encrypted_path = Path(encrypted_file)
    return (encrypted_path, encrypted_path.unlink)
