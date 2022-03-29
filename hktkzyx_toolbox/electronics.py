from __future__ import annotations

from typing import Optional, Union

import numpy as np
from scipy import interpolate
from scipy import optimize


def get_e_series_preferred_number(resistance, kind='nearest', series='E96'):
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
        Preferred number.
    array_like of int
        Scale power.

    Examples
    --------
    >>> get_e_series_preferred_number(3000)
    (3.01, 3)
    >>> get_e_series_preferred_number(3100,series='E24')
    (array(3.3), 3)
    >>> get_e_series_preferred_number([2.01, 2.67, 8.0],series='E24')
    (array([2. , 2.7, 8.2]), array([0, 0, 0]))
    >>> get_e_series_preferred_number([2.01, 2.70, 7.0],series='E6')
    (array([2.2, 3.3, 6.8]), array([0, 0, 0]))
    """
    series_group = {
        'E6': 6, 'E12': 12, 'E24': 24, 'E48': 48, 'E96': 96, 'E192': 192
    }
    series_significant_figures = {
        'E6': 2, 'E12': 2, 'E24': 2, 'E48': 3, 'E96': 3, 'E192': 3
    }
    group = series_group.get(series, 96)
    decimal = series_significant_figures.get(series, 3) - 1
    power_int = np.floor(np.log10(resistance)).astype(int)
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

    return preferred_number, power_int


class LED:
    """The LED electronic component.

    Parameters
    ----------
    name : str
        Name of the LED.
    no : str or int, optional
        No. in LCSC_. By default ``None``.
    voltage_array, current_array : array_like of float, optional
        The array of voltage or current. By default ``None``.

    .. _LCSC: https://www.szlcsc.com/
    """

    def __init__(self,
                 name: str,
                 no: Optional[Union[str, int]] = None,
                 voltage_array=None,
                 current_array=None):
        self.name = name
        self.no = no
        self._voltage_limit = None
        self._current_limit = None
        self._voltage_current_relation = None
        if voltage_array is not None and current_array is not None:
            self.set_voltage_current_relation(voltage_array, current_array)

    def set_voltage_current_relation(self, voltage_array, current_array):
        """Set the function of voltage and current relation.

        Parameters
        ----------
        voltage_array, current_array : array_like of float
            Voltage or current array.
        """
        voltage_array = np.asarray(voltage_array)
        current_array = np.asarray(current_array)
        self._voltage_limit = (np.amin(voltage_array), np.amax(voltage_array))
        self._current_limit = (np.amin(current_array), np.amax(current_array))
        self._voltage_current_relation = interpolate.CubicSpline(
            current_array, voltage_array, extrapolate=False)

    def get_divider_resistance_limit(self, voltage):
        """Return divider resistance limit at given voltage.

        Parameters
        ----------
        voltage : array_like of float
            Power voltage.

        Returns
        -------
        np.ndarray
            Divider resistance lower bound.
        np.ndarray
            Divider resistance upper bound.
        """
        voltage = np.asarray(voltage)
        if self._voltage_limit is None or self._current_limit is None:
            raise ValueError('Voltage-current relation is not set.')
        resistance_max = ((voltage - self._voltage_limit[0])
                          / self._current_limit[0])
        resistance_min = ((voltage - self._voltage_limit[1])
                          / self._current_limit[1])
        resistance_min = np.where(resistance_min < 0, 0, resistance_min)
        return resistance_min, resistance_max

    def _get_current(self, voltage: float):
        """Return corresponding current."""
        if voltage > self._voltage_limit[1] or voltage < self._voltage_limit[0]:
            raise ValueError(
                f'Voltage {voltage} outside voltage range {self._voltage_limit}'
            )
        return optimize.bisect(self._voltage_current_relation,
                               self._current_limit[0],
                               self._current_limit[1])

    def get_work_current_limit(self, voltage):
        """Return working current limit at given voltage.

        Parameters
        ----------
        voltage : array_like of float
            Power voltage.

        Returns
        -------
        np.ndarray
            Working current lower bound.
        np.ndarray
            Working current upper bound.
        """
        voltage = np.asarray(voltage)
        if self._voltage_limit is None or self._current_limit is None:
            raise ValueError('Voltage-current relation is not set.')
        current_max = np.where(voltage >= self._voltage_limit[1],
                               self._current_limit[1],
                               np.nan)
        indices = np.argwhere(np.isnan(current_max))
        for index in indices:
            current_max[index] = self._get_current(voltage[index])
        return self._current_limit[0] * np.ones_like(current_max), current_max

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
