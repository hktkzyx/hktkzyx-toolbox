from __future__ import annotations

import warnings
from bisect import bisect_left, bisect_right
from collections.abc import Callable, Iterable
from typing import Optional, Union

import numpy as np
from scipy import interpolate, optimize

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


def get_standard_resistance(
        resistance: float, kind: str = 'nearest',
        human_format: bool = False) -> Optional[Union[float, str]]:
    """Return closest standard resistance.

    Parameters
    ----------
    resistance : float
        The value of resistance with unit Ω.
    kind : str, optional
        Specify the kind of look up standard resistance.
        ``'nearest'`` rounds to nearest standard resistance,
        ``'up'`` rounds up to the standard resistance,
        and ``'down'`` rounds down to the standard resistance.
        By default ``'nearest``.
    human_format : bool, optional
        Whether to return human readable format of resistance,
        by default ``False``.

    Returns
    -------
    float, str or None
        If `human_format` is ``True``, return str, else return float.
        If not found, return ``None``.
    """
    if not human_format:
        return _get_standard_resistance(resistance, kind)
    else:
        result = _get_standard_resistance(resistance, kind)
        if result is None:
            return None
        units = ('', 'K', 'M')
        for unit in units:
            if abs(result) < 1000:
                return f'{result:.1f}{unit}'
            else:
                result = result / 1000
        else:
            result = _get_standard_resistance(resistance, kind)
            raise ValueError(f'No unit for {result:E}.')


def _get_standard_resistance(resistance: float, kind: str) -> float:
    kind = str.lower(kind)
    if kind == 'nearest':
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
    elif kind == 'down':
        pos = bisect_right(standard_resistance, resistance)
        if pos == 0:
            result = None
        else:
            result = standard_resistance[pos - 1]
    elif kind == 'up':
        pos = bisect_left(standard_resistance, resistance)
        if pos == standard_resistance.size:
            result = None
        else:
            result = standard_resistance[pos]
    else:
        raise ValueError(f'{kind} not found.')
    return result


class LED:
    """The LED electronic component.
    
    Parameters
    ----------
    name : str
        Name of the LED.
    no : str or int
        No. in LCSC_. By default ``None``.
    voltage_array, current_array : array_like of float
        The array of voltage or current.

    .. _LCSC: https://www.szlcsc.com/
    """
    def __init__(self,
                 name: str,
                 no: Optional[Union[str, int]] = None,
                 voltage_array: Optional[Iterable[float]] = None,
                 current_array: Optional[Iterable[float]] = None):
        self.name = name
        self.no = no
        self._max_voltage = 0.0
        self._max_current = 0.0

        if (voltage_array is None) or (current_array is None):
            self._voltage_current_relation = None
        else:
            self._voltage_current_relation = self.set_voltage_current_relation(
                voltage_array, current_array)

    def set_voltage_current_relation(
            self,
            voltage_array: Optional[Iterable[float]],
            current_array: Optional[Iterable[float]]) -> Callable:
        """Return a function of voltage and current relation.

        Parameters
        ----------
        voltage_array, current_array : array_like of float
            Voltage or current array.

        Returns
        -------
        callable
            Voltage value at given current.
        """
        voltage_array = np.asarray(voltage_array)
        current_array = np.asarray(current_array)
        self._max_voltage = np.amax(voltage_array)
        self._max_current = np.amax(current_array)
        return interpolate.interp1d(current_array,
                                    voltage_array,
                                    kind='cubic',
                                    bounds_error=True)

    def get_current_and_resistance(self,
                                   voltage: float,
                                   current: Optional[float] = None,
                                   resistance: Optional[float] = None):
        """Return working current and the needed resistance.

        Parameters
        ----------
        voltage : float
            Total voltage provided.
        current, resistance : float or ``None``
            Working current or needed resistance, by default ``None``.

        Returns
        -------
        float
            Current value.
        float
            Resistance value.
        """
        warnings.warn(('Separated by two functions,'
                       '`get_divider_resistance` and `get_work_current`.'
                       'Will be removed after 0.3.'),
                      DeprecationWarning)
        if current and 0 < current < self._max_current:
            resistance = (voltage
                          - self._voltage_current_relation(current)) / current
        elif (resistance and resistance > 0
              and (resistance >
                   (voltage - self._max_voltage) / self._max_current)):

            def equation(x):
                return (
                    (voltage - self._voltage_current_relation(x)) / resistance
                    - x)

            current = optimize.bisect(equation, 0, self._max_current)

        else:
            raise ValueError(
                'Either `current` or `resistance` should be greater than 0.'
                'Or `current` too large. Or `resistance` too small.')
        return current, resistance

    def get_divider_resistance(self, voltage: float, current: float) -> float:
        """Return divider resistance.

        Parameters
        ----------
        voltage : float
            Voltage supplied. Unit ``V``.
        current : float
            Working current. Unit ``A``.

        Returns
        -------
        float
            Divider resistance. Unit ``Ω ``.
        """
        if 0 < current <= self._max_current:
            resistance = (voltage
                          - self._voltage_current_relation(current)) / current
        elif current > self._max_current:
            raise ValueError(
                f'{current:.2f} is greater than max {self._max_current:.2f}.')
        else:
            raise ValueError('`current` has to be greater than 0.')
        return resistance

    def get_work_current(self, voltage: float,
                         divider_resistance: float) -> float:
        """Return work current.

        Parameters
        ----------
        voltage : float
            Voltage supplied. Unit ``V``.
        divider_resistance : float
            Divider resistance. Unit ``Ω``.

        Returns
        -------
        float
            Current. Unit ``A ``.
        """
        if divider_resistance >= (
                voltage - self._max_voltage
        ) / self._max_current and divider_resistance > 0:

            def equation(x):
                return ((voltage - self._voltage_current_relation(x))
                        / divider_resistance - x)

            current = optimize.bisect(equation, 0, self._max_current)
        else:
            raise ValueError(
                f'Divider resistance has to be greater than'
                f'{(voltage-self._max_voltage)/self._max_current:.2f} Ω'
                f'at {voltage:.2f} V.')
        return current


typical_led = LED(
    'typical LED',
    voltage_array=(2.7524, 2.8800, 3.0030, 3.1260, 3.2490, 3.3766),
    current_array=(-0.097e-3,
                   4.772e-3,
                   9.76e-3,
                   14.748e-3,
                   19.735e-3,
                   24.605e-3))
