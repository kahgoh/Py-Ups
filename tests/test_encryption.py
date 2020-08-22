from pathlib import Path
import pytest
from pyups import encryption

TEST_CONTENT = "A historical way to create temporary files was to..."

@pytest.fixture
def sample_path(tmp_path) -> Path:
    """
    Sets up a file with content for the testing the encryption.

    Parameters
    ----------
    tmp_path
        Temporary directory fixture from `pytest`. The sample file will be
        placed in this directory.

    Return
    ------
    The path where the sample file was created.
    """
    sample_file = tmp_path / "test_content"
    sample_file.write_text(TEST_CONTENT)

    return sample_file

def test_encrypted_content(sample_path):
    """
    Tests that the content of the file provided by `encryption.encrypted_file`
    is encrypted (or the contents is the **different** to the file that was
    provided to it).
    """
    (result_path, cleanup) = encryption.encrypted_file(sample_path, "abcdef")
    try:
        with result_path.open(mode="rb") as file:
            content = file.read(1024)

        assert content != bytearray(TEST_CONTENT, "utf8")
    finally:
        cleanup()

def test_encrypted_cleanup(sample_path):
    """
    Tests that the clean up function provided by `encryption.encrypted_file`
    deletes **ONLY** the encrypted file that it provided.
    """
    (encrypted_file, cleanup) = encryption.encrypted_file(sample_path, "abcdef")
    cleanup()

    assert sample_path.exists()
    assert not encrypted_file.exists()