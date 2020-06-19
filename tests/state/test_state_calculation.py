import logging
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from pyups.state import model as state

# Tests for the `calculate_state` method from `pyups.state`.

CONTENT = {
    "document": {
        "content": 
"""tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
    Creates a temporary directory in the most secure
    manner possible. There are no race conditions in
    the directory’s creation. The directory is 
    readable, writable, and searchable only by the
    creating user ID.""",
        "size": 284,
        "hash": "eaf3f759ab59919ee454f1fc176cb8b17f828296"
    }, 
    "story": {
        "content":
"""Once upon a time there were three bears who lived in a
house in the forest. Therewas a great big father bear, a 
middle-sized mother bear and a tiny baby bear. One 
morning, their breakfast porridge was too hot to eat, so
they decided to go for a walk in the forest.""",
        "size": 270,
        "hash": "4a13688a37665c912d3f982e6304692f7bee66e1"
    }, 
    "names": {
        "content": "Adam Eve Jack Jill Hansel Gretel",
        "size": 32,
        "hash": "31222fa4058e916488289a3c41e0a75a57fc6947"
    }
}

@pytest.fixture(params=CONTENT)
def sample(request) -> dict:
    """
    Prepares a temporary directory with the sample data for the tests.
    """
    content = dict(CONTENT[request.param])
    temporary_directory = TemporaryDirectory()
    path = Path(temporary_directory.name).joinpath(request.param)

    # Store the temporary directory context to ensure that the files hang 
    # around for the tests.
    content["temporary_directory"] = temporary_directory
    content["path"] = path

    with path.open(mode="w") as file:
        file.write(content["content"])

    logging.info(f"Sample data stored in: {path}")

    return content

def test_calculate_state(sample) -> None:
    calculated = state.calculate_state(path=sample["path"])
    
    # We can only safely verify the size and hash values.
    expected = {
        "size": sample["size"],
        "hash": sample["hash"]
    }

    actual = {
        "size": calculated.size,
        "hash": calculated.hash
    }

    assert actual == expected

        
        
