import base64
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from pyups.state import model as state

# Tests for the `calculate_state` method from `pyups.state`.

CONTENT = {
    "document": {
        "content": "dGVtcGZpbGUubWtkdGVtcChzdWZmaXg9Tm9uZSwgcHJlZml4PU5vbmUsIGRpcj1Ob25lKQogICAgQ3JlYXRlcyBhIHRlbXBvcmFyeSBkaXJlY3RvcnkgaW4gdGhlIG1vc3Qgc2VjdXJlCiAgICBtYW5uZXIgcG9zc2libGUuIFRoZXJlIGFyZSBubyByYWNlIGNvbmRpdGlvbnMgaW4KICAgIHRoZSBkaXJlY3RvcnnigJlzIGNyZWF0aW9uLiBUaGUgZGlyZWN0b3J5IGlzIAogICAgcmVhZGFibGUsIHdyaXRhYmxlLCBhbmQgc2VhcmNoYWJsZSBvbmx5IGJ5IHRoZQogICAgY3JlYXRpbmcgdXNlciBJRC4="
            # tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
            #    Creates a temporary directory in the most secure
            #    manner possible. There are no race conditions in
            #    the directory’s creation. The directory is 
            #    readable, writable, and searchable only by the
            #    creating user ID.
        , "size": 281
        , "hash": "ba67180097e58a2b2037f66e60d7620cebb7fa4a"
    }, 
    "story": {
        "content": "T25jZSB1cG9uIGEgdGltZSB0aGVyZSB3ZXJlIHRocmVlIGJlYXJzIHdobyBsaXZlZCBpbiBhCmhvdXNlIGluIHRoZSBmb3Jlc3QuIFRoZXJld2FzIGEgZ3JlYXQgYmlnIGZhdGhlciBiZWFyLCBhIAptaWRkbGUtc2l6ZWQgbW90aGVyIGJlYXIgYW5kIGEgdGlueSBiYWJ5IGJlYXIuIE9uZSAKbW9ybmluZywgdGhlaXIgYnJlYWtmYXN0IHBvcnJpZGdlIHdhcyB0b28gaG90IHRvIGVhdCwgc28KdGhleSBkZWNpZGVkIHRvIGdvIGZvciBhIHdhbGsgaW4gdGhlIGZvcmVzdC4="
            # Once upon a time there were three bears who lived in a
            # house in the forest. Therewas a great big father bear, a 
            # middle-sized mother bear and a tiny baby bear. One 
            # morning, their breakfast porridge was too hot to eat, so
            # they decided to go for a walk in the forest.
        , "size": 266
        , "hash": "6274c99919fa355879cfc43838c718cf231356ed"
    }, 
    "names": {
        "content": "QWRhbSBFdmUgSmFjayBKaWxsIEhhbnNlbCBHcmV0ZWw="
        , "size": 32
        , "hash": "31222fa4058e916488289a3c41e0a75a57fc6947"
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

    with path.open(mode="wb") as file:
        decodedBytes = base64.standard_b64decode(content["content"])
        file.write(decodedBytes)

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

        
        
