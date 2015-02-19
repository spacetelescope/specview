import numpy as np
from astropy.nddata import NDData


def extract(nddata, range, axes=(0, 1)):
    """Extracts a region out of an n-dimensional NDData object.

    Parameters
    ----------
    nddata : NDData
        Source data object.
    range : List
        A list of tuples containing the extraction region for the axis.
        Cannot be larger than len(nddata.shape).
    axes : tuple
        A tuple of axis indices.

    Returns
    -------
    out: NDData
        Extracted data object.
    """
    shape = []

    for m in nddata.shape:
        shape.append(slice(0, m))

    for i, axis in enumerate(axes):
        shape[axis] = slice(range[i][0], range[i][1])

    return nddata[shape]