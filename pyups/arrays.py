def partition(array: [], max_length: int) -> []:
    """
    Partitions an array or list into smaller arrays or lists and yields them.
    The length or size of each partition will be no greater than a given size.

    Parameters
    ----------
    array
        The array or list that will be partitioned.

    max_length
        The maximum length of each partition. The length of each partition will
        not exceed this length.
    
    Yields
    ------
    Each partition.
    """
    for i in range(0, len(array), max_length):
        end = min(i + max_length, len(array))
        yield array[i:end]