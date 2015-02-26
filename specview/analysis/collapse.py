import numpy as np
from astropy.units import Unit

from specview.core import CubeData, ImageArray


def collapse(cube_data, method='average', axis=0):

    if method == 'average':
        new_data = np.nanmean(cube_data.data, axis=axis)
    elif method == 'median':
        new_data = np.nanmedian(cube_data.data, axis=axis)

    return ImageArray(new_data, wcs=cube_data.wcs, unit=cube_data.units[1])


if __name__ == '__main__':
    cd = CubeData(np.random.normal(size=(10,10,10)))
    cd.set_unit(0, Unit('micron'))
    cd.set_unit(1, Unit('arcsec'))
    cd.set_unit(2, Unit('arcsec'))

    print(cd)

    ia = collapse(cd)
    print(type(ia))
    print(ia)
    print(ia.unit)