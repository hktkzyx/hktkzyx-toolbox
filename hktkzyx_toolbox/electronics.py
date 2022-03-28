from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from typing import Optional, Union

import numpy as np
from scipy import interpolate
from scipy import optimize


def get_e_series_number(resistance, kind='nearest', series='E96'):
    """Return E series prefered number.

    Follow the standard IEC 60063:2015.

    Parameters
    ----------
    value : array_like of float or int
        Value.
    kind : str, optional
        Specify the kind of rounding.
        ``'nearest'`` rounds to nearest preferred number,
        ``'ceil'`` rounds up to the preferred number,
        and ``'floor'`` rounds down to the preferred number.
        By default ``'nearest``.
    series : str, optional
        Standard series. 'E6', 'E12', 'E24', 'E48', 'E96', 'E192' are allowed.
        By default 'E96'.

    Returns
    -------
    array_like of float

    Examples
    --------
    >>> get_e_series_number(3000)
    3010.0
    >>> get_e_series_number(3100, series='E24')
    3300.0
    >>> get_e_series_number([2.01, 2.67, 8.0], series='E24')
    array([2. , 2.7, 8.2])
    >>> get_e_series_number([2.01, 2.70, 7.0], series='E6')
    array([2.2, 3.3, 6.8])
    """
    series_group = {
        'E6': 6, 'E12': 12, 'E24': 24, 'E48': 48, 'E96': 96, 'E192': 192
    }
    series_significant_figures = {
        'E6': 2, 'E12': 2, 'E24': 2, 'E48': 3, 'E96': 3, 'E192': 3
    }
    group = series_group.get(series, 96)
    decimal = series_significant_figures.get(series, 3) - 1
    power_int = np.floor(np.log10(resistance))
    power_fraction = np.log10(resistance) - power_int
    group_index = power_fraction * group
    if kind == 'nearest':
        group_index = np.round(group_index)
    elif kind == 'floor':
        group_index = np.floor(group_index)
    elif kind == 'ceil':
        group_index = np.ceil(group_index)
    else:
        raise ValueError(f'`kind` {kind!r} not found, '
                         '\'nearest\', \'floor\', or \'ceil\' allowed.')
    preferred_number = np.round(10**(group_index / group), decimals=decimal)
    # Deal with eight older special values below E24 series.
    if series == 'E6':
        preferred_number = np.where(group_index == 3, 3.3, preferred_number)
        preferred_number = np.where(group_index == 4, 4.7, preferred_number)
    if series == 'E12':
        preferred_number = np.where(group_index == 5, 2.7, preferred_number)
        preferred_number = np.where(group_index == 6, 3.3, preferred_number)
        preferred_number = np.where(group_index == 7, 3.9, preferred_number)
        preferred_number = np.where(group_index == 8, 4.7, preferred_number)
        preferred_number = np.where(group_index == 11, 8.2, preferred_number)
    if series == 'E24':
        preferred_number = np.where(group_index == 10, 2.7, preferred_number)
        preferred_number = np.where(group_index == 11, 3.0, preferred_number)
        preferred_number = np.where(group_index == 12, 3.3, preferred_number)
        preferred_number = np.where(group_index == 13, 3.6, preferred_number)
        preferred_number = np.where(group_index == 14, 3.9, preferred_number)
        preferred_number = np.where(group_index == 15, 4.3, preferred_number)
        preferred_number = np.where(group_index == 16, 4.7, preferred_number)
        preferred_number = np.where(group_index == 22, 8.2, preferred_number)

    return preferred_number * 10**power_int


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

typical_led_red = LED(
    'typical LED red',
    voltage_array=(1.7736, 1.82944, 1.88781, 1.94365, 2.0, 2.05533),
    current_array=(0.0, 5.0, 10.0, 15.0, 20.0, 25.0))
