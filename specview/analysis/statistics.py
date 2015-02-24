import numpy as np

from specview.core import SpectrumData
from proto.model_manager import test_data


def extract(spectrum_data, range):
    x = spectrum_data.x.data
    y = spectrum_data.y.data

    index1 = x >= range[0]
    x1 = x[index1]
    y1 = y[index1]
    index2 = x1 < range[1]
    x2 = x1[index2]
    y2 = y1[index2]

    result = SpectrumData()
    result.set_x(x2, unit=spectrum_data.x.unit)
    result.set_y(y2, unit=spectrum_data.y.unit)

    return result


def stats(spectrum_data):
    flux = spectrum_data.y.data
    return {'mean':    np.mean(flux),
            'median':  np.median(flux),
            'stddev':  np.std(flux),
            'total':   np.trapz(flux),
            'npoints': len(flux)
            }


def eq_width(cont1_stats, cont2_stats, line):
    ''' Computes an equivalent width given stats for two continuum
    regions, and a SpectrumData instance with the extracted
    spectral line region.

    Paramaters
    ----------
    cont1_stats: dict
      This is returned by the stats() function
    cont2_stats: dict
      This is returned by the stats() function
    line: SpectrumData
      This is returned by the extract() function

    Returns
    -------
    equivalent width: float

    '''
    # average of 2 continuum regions.
    avg_cont = (cont1_stats['mean'] + cont2_stats['mean']) / 2.0

    # average dispersion in the line region.
    avg_dx = np.mean(line.x.data[1:] - line.x.data[:-1])

    #  EW = Sum( (Fc-Fl)/Fc * dw
    return np.sum((avg_cont - line.y.data) / avg_cont * avg_dx)


def test1():

    # real emission line from UV spectrum of NGC3516
    x,y,e = test_data.get_data()

    sp_data = SpectrumData()
    sp_data.set_x(x, unit="Angstrom")
    sp_data.set_y(y, unit="erg.s-1.cm**-2.Angstrom-1")

    range_c1 = (1160., 1190.)
    range_c2 = (1281., 1305.)
    range_li = (1190., 1280.)

    cont1 = extract(sp_data, range_c1)
    cont2 = extract(sp_data, range_c2)
    line  = extract(sp_data, range_li)

    cont1_stats = stats(cont1)
    cont2_stats = stats(cont2)
    line_stats  = stats(line)

    print '@@@@@@     line: 57  - ', cont1_stats
    print '@@@@@@     line: 58  - ', cont2_stats
    print '@@@@@@     line: 59  - ', line_stats

    ew = eq_width(cont1_stats, cont2_stats, line)

    print '@@@@@@     line: 90  - ', ew


if __name__ == "__main__":
    test1()
  