from __future__ import annotations

from bisect import bisect_left
from typing import Union

import numpy as np

standard_resistance_base = np.array([
    1.0,
    1.1,
    1.2,
    1.3,
    1.5,
    1.6,
    1.8,
    2.0,
    2.2,
    2.4,
    2.7,
    3.0,
    3.3,
    3.6,
    3.9,
    4.3,
    4.7,
    5.1,
    5.6,
    6.2,
    6.8,
    7.5,
    8.2,
    9.1
])
magnitude = (1, 10, 100, 1e3, 10e3, 100e3, 1e6)
standard_resistance = [mag * standard_resistance_base for mag in magnitude]
standard_resistance = np.sort(np.concatenate(tuple(standard_resistance)),
                              axis=None)


def get_standard_resistance(resistance: float,
                            human_format: bool = False) -> Union[float, str]:
    """Return closest standard resistance.

    Parameters
    ----------
    resistance : float
        The value of resistance with unit Ω.
    human_format : bool, optional
        Whether to return human readable format of resistance,
        by default ``False``.

    Returns
    -------
    float or str
        If `human_format` is ``True``, return str, else return float.
    """
    if not human_format:
        return _get_standard_resistance(resistance)
    else:
        result = _get_standard_resistance(resistance)
        units = ('', 'K', 'M')
        for unit in units:
            if abs(result) < 1000:
                return f'{result:.1f}{unit}'
            else:
                result = result / 1000
        else:
            result = _get_standard_resistance(resistance)
            raise ValueError(f'No unit for {result:E}.')


def _get_standard_resistance(resistance: float) -> float:
    pos = bisect_left(standard_resistance, resistance)
    if pos == 0:
        result = standard_resistance[0]
    elif pos == standard_resistance.size:
        result = standard_resistance[-1]
    else:
        left = standard_resistance[pos - 1]
        right = standard_resistance[pos]
        if resistance - left <= right - resistance:
            result = left
        else:
            result = right
    return result
