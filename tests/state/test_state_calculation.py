import base64
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from pyups.state import model as state

# Tests for the `calculate_state` method from `pyups.state`.

CONTENT = {
    "document": {
        "content":
        "dGVtcGZpbGUubWtkdGVtcChzdWZmaXg9Tm9uZSwgcHJlZml4PU5vbmUsIGRpcj1Ob25lKQogICAgQ3JlYXRlcyBhIHRlbXBvcmFyeSBkaXJlY3RvcnkgaW4gdGhlIG1vc3Qgc2VjdXJlCiAgICBtYW5uZXIgcG9zc2libGUuIFRoZXJlIGFyZSBubyByYWNlIGNvbmRpdGlvbnMgaW4KICAgIHRoZSBkaXJlY3RvcnnigJlzIGNyZWF0aW9uLiBUaGUgZGlyZWN0b3J5IGlzIAogICAgcmVhZGFibGUsIHdyaXRhYmxlLCBhbmQgc2VhcmNoYWJsZSBvbmx5IGJ5IHRoZQogICAgY3JlYXRpbmcgdXNlciBJRC4="
        # tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        #    Creates a temporary directory in the most secure
        #    manner possible. There are no race conditions in
        #    the directory’s creation. The directory is
        #    readable, writable, and searchable only by the
        #    creating user ID.
        ,
        "size":
        281,
        "hash":
        "3e5fed0da2457a5c47df03691f94e9d3d27d00f60bcd0c188007a14c4aab01dc"
    },
    "story": {
        "content":
        "T25jZSB1cG9uIGEgdGltZSB0aGVyZSB3ZXJlIHRocmVlIGJlYXJzIHdobyBsaXZlZCBpbiBhCmhvdXNlIGluIHRoZSBmb3Jlc3QuIFRoZXJld2FzIGEgZ3JlYXQgYmlnIGZhdGhlciBiZWFyLCBhIAptaWRkbGUtc2l6ZWQgbW90aGVyIGJlYXIgYW5kIGEgdGlueSBiYWJ5IGJlYXIuIE9uZSAKbW9ybmluZywgdGhlaXIgYnJlYWtmYXN0IHBvcnJpZGdlIHdhcyB0b28gaG90IHRvIGVhdCwgc28KdGhleSBkZWNpZGVkIHRvIGdvIGZvciBhIHdhbGsgaW4gdGhlIGZvcmVzdC4="
        # Once upon a time there were three bears who lived in a
        # house in the forest. Therewas a great big father bear, a
        # middle-sized mother bear and a tiny baby bear. One
        # morning, their breakfast porridge was too hot to eat, so
        # they decided to go for a walk in the forest.
        ,
        "size":
        266,
        "hash":
        "3907c0ff5efe64a96a6fe8aa01186f57bde6fd8c196b74967fb274683020032a"
    },
    "names": {
        "content": "QWRhbSBFdmUgSmFjayBKaWxsIEhhbnNlbCBHcmV0ZWw=",
        "size": 32,
        "hash":
        "394de74a5476b3b245f1e4938daa68825a9a57f27074bdd67bfe2936f7dcefb0"
    }
}


@pytest.fixture(params=CONTENT)
def sample(request, tmp_path) -> dict:
    """
    Prepares a temporary directory with the sample data for the tests.
    """
    content = dict(CONTENT[request.param])
    path = tmp_path.joinpath(request.param)

    # Store the path so that the tests know where to find it.
    content["path"] = path

    decodedBytes = base64.standard_b64decode(content["content"])
    path.write_bytes(decodedBytes)

    logging.info(f"Sample data stored in: {path}")

    return content


def test_calculate_state(sample) -> None:
    calculated = state.calculate_state(path=sample["path"])

    # We can only safely verify the size and hash values.
    expected = {"size": sample["size"], "hash": sample["hash"]}

    actual = {"size": calculated.size, "hash": calculated.content_hash}

    assert actual == expected
