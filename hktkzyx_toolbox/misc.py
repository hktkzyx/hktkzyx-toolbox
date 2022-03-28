import math
from typing import Union


def si_prefix_selector(
        value: Union[float, int]) -> tuple[Union[float, int], str, str]:
    """Return scaled value, SI symbol, and prefix.

    Parameters
    ----------
    value : float or int
        Value.

    Returns
    -------
    float or int
        Scaled value.
    str or None
        SI symbol.
    str or None
        SI prefix.

    Examples
    --------
    >>> si_prefix_selector(2.1)
    (2.1, None, None)
    >>> si_prefix_selector(2.1e4)
    (21.0, 'k', 'kilo')
    >>> si_prefix_selector(2.13e-4)
    (213.0, 'μ', 'micro')
    >>> si_prefix_selector(-2.1e4)
    (-21.0, 'k', 'kilo')
    >>> si_prefix_selector(-2.13e-4)
    (-213.0, 'μ', 'micro')
    """
    prefixes = {
        24: {
            'prefix': 'yotta', 'symbol': 'Y', 'scale': 10**24
        },
        21: {
            'prefix': 'zetta', 'symbol': 'Z', 'scale': 10**21
        },
        18: {
            'prefix': 'exa', 'symbol': 'E', 'scale': 10**18
        },
        15: {
            'prefix': 'peta', 'symbol': 'P', 'scale': 10**15
        },
        12: {
            'prefix': 'tera', 'symbol': 'T', 'scale': 10**12
        },
        9: {
            'prefix': 'giga', 'symbol': 'G', 'scale': 10**9
        },
        6: {
            'prefix': 'mega', 'symbol': 'M', 'scale': 10**6
        },
        3: {
            'prefix': 'kilo', 'symbol': 'k', 'scale': 10**3
        },
        -3: {
            'prefix': 'milli', 'symbol': 'm', 'scale': 10**-3
        },
        -6: {
            'prefix': 'micro', 'symbol': 'μ', 'scale': 10**-6
        },
        -9: {
            'prefix': 'nano', 'symbol': 'n', 'scale': 10**-9
        },
        -12: {
            'prefix': 'pico', 'symbol': 'p', 'scale': 10**-12
        },
        -15: {
            'prefix': 'femto', 'symbol': 'f', 'scale': 10**-15
        },
        -18: {
            'prefix': 'atto', 'symbol': 'a', 'scale': 10**-18
        },
        -21: {
            'prefix': 'zepto', 'symbol': 'z', 'scale': 10**-21
        },
        -24: {
            'prefix': 'yocto', 'symbol': 'y', 'scale': 10**-24
        },
    }
    prefix_power = math.floor(math.log10(abs(value)) / 3.0) * 3
    prefix_info = prefixes.get(prefix_power, None)
    if prefix_info is None:
        return value, None, None
    (prefix, symbol, scale) = (prefix_info['prefix'],
                               prefix_info['symbol'],
                               prefix_info['scale'])
    return value / scale, symbol, prefix


def si_formatter(value: Union[float, int],
                 significant_figures=4,
                 unit: str = None):
    """Return value with SI prefix.

    Parameters
    ----------
    value : float or int
        Value.
    significant_figures : int, optional
        Significant figures of output, by default 4
    unit : str, optional
        Unit of the value, by default None

    Returns
    -------
    str

    Examples
    --------
    >>> si_formatter(2100, unit='Hz')
    '2.100 kHz'
    >>> si_formatter(2.13e4, unit='Hz')
    '21.30 kHz'
    >>> si_formatter(2.13e4)
    '21.30 k'
    >>> si_formatter(2.134)
    '2.134'
    """
    scaled_value, symbol, _ = si_prefix_selector(value)
    if abs(scaled_value) >= 100:
        digits = significant_figures - 3
    elif abs(scaled_value) >= 10:
        digits = significant_figures - 2
    else:
        digits = significant_figures - 1
    if symbol is None and unit is None:
        return f'{scaled_value:.{digits}f}'
    else:
        return f'{scaled_value:.{digits}f} {symbol or ""}{unit or ""}'
