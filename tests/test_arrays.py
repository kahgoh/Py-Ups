from pyups.arrays import partition

def test_partition_even_divisor() -> None:
    sample = [1, 2, 3, 4, 5, 6, 7, 8]
    divided = [i for i in partition(sample, 2)]
    assert divided == [[1, 2], [3, 4], [5, 6], [7, 8]]

def test_partition_odd_divisor() -> None:
    sample = [1, 2, 3, 4, 5, 6, 7, 8]
    divided = [i for i in partition(sample, 3)]
    assert divided == [[1, 2, 3], [4, 5, 6], [7, 8]]


def test_partition_empty_array() -> None:
    assert [i for i in partition([], 3)] == []