from __future__ import annotations

import bisect
from typing import Optional, Union

import numpy as np
import numpy.typing as npt
from scipy import interpolate
from scipy import optimize

PREFERRED_NUMBER_E24 = [
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
]
PREFERRED_NUMBER_E192 = [
    1.00,
    1.01,
    1.02,
    1.04,
    1.05,
    1.06,
    1.07,
    1.09,
    1.10,
    1.11,
    1.13,
    1.14,
    1.15,
    1.17,
    1.18,
    1.20,
    1.21,
    1.23,
    1.24,
    1.26,
    1.27,
    1.29,
    1.30,
    1.32,
    1.33,
    1.35,
    1.37,
    1.38,
    1.40,
    1.42,
    1.43,
    1.45,
    1.47,
    1.49,
    1.50,
    1.52,
    1.54,
    1.56,
    1.58,
    1.60,
    1.62,
    1.64,
    1.65,
    1.67,
    1.69,
    1.72,
    1.74,
    1.76,
    1.78,
    1.80,
    1.82,
    1.84,
    1.87,
    1.89,
    1.91,
    1.93,
    1.96,
    1.98,
    2.00,
    2.03,
    2.05,
    2.08,
    2.10,
    2.13,
    2.15,
    2.18,
    2.21,
    2.23,
    2.26,
    2.29,
    2.32,
    2.34,
    2.37,
    2.40,
    2.43,
    2.46,
    2.49,
    2.52,
    2.55,
    2.58,
    2.61,
    2.64,
    2.67,
    2.71,
    2.74,
    2.77,
    2.80,
    2.84,
    2.87,
    2.91,
    2.94,
    2.98,
    3.01,
    3.05,
    3.09,
    3.12,
    3.16,
    3.20,
    3.24,
    3.28,
    3.32,
    3.36,
    3.40,
    3.44,
    3.48,
    3.52,
    3.57,
    3.61,
    3.65,
    3.70,
    3.74,
    3.79,
    3.83,
    3.88,
    3.92,
    3.97,
    4.02,
    4.07,
    4.12,
    4.17,
    4.22,
    4.27,
    4.32,
    4.37,
    4.42,
    4.48,
    4.53,
    4.59,
    4.64,
    4.70,
    4.75,
    4.81,
    4.87,
    4.93,
    4.99,
    5.05,
    5.11,
    5.17,
    5.23,
    5.30,
    5.36,
    5.42,
    5.49,
    5.56,
    5.62,
    5.69,
    5.76,
    5.83,
    5.90,
    5.97,
    6.04,
    6.12,
    6.19,
    6.26,
    6.34,
    6.42,
    6.49,
    6.57,
    6.65,
    6.73,
    6.81,
    6.90,
    6.98,
    7.06,
    7.15,
    7.23,
    7.32,
    7.41,
    7.50,
    7.59,
    7.68,
    7.77,
    7.87,
    7.96,
    8.06,
    8.16,
    8.25,
    8.35,
    8.45,
    8.56,
    8.66,
    8.76,
    8.87,
    8.98,
    9.09,
    9.20,
    9.31,
    9.42,
    9.53,
    9.65,
    9.76,
    9.88
]


class ESeriesValue:
    """E series preferred value.

    Follow the standard IEC 60063:2015.
    The preferred number is rounded by the following equation:

    .. math::

        V_n=10^{n/m}

    where ``n`` is the series exponent, ``m`` is the series group size.

    Parameters
    ----------
    series_exponent : int
        Series exponent.
    series_size : int
        Series size.
    exponent : int
        Exponent base on 10.
    positive : bool, optional
        Non-negetive or not, by default ``True``.
    """

    def __init__(self,
                 series_exponent: int,
                 series_size: int,
                 exponent: int,
                 positive: bool = True):
        _launch_e_series_size_verify(series_size)
        self.preferred_number = None
        self.series = None
        self.significant_figures = None
        self.series_exponent: int = series_exponent
        self.series_size: int = series_size
        self.exponent: int = exponent
        self.is_positive: bool = positive
        self._cal_related_variables()

    def _cal_related_variables(self):
        """Calculate related variables."""
        self.series = f'E{self.series_size:d}'
        if self.series_size >= 48:
            self.significant_figures = 3
        else:
            self.significant_figures = 2
        self._query_preferred_number()

    def _query_preferred_number(self):
        """Return preferred number."""
        if self.series_size <= 24:
            self.preferred_number = PREFERRED_NUMBER_E24[24 // self.series_size
                                                         *
                                                         self.series_exponent]
        else:
            self.preferred_number = PREFERRED_NUMBER_E192[192
                                                          // self.series_size *
                                                          self.series_exponent]

    def to_scalar(self):
        """Convert to scalar value."""
        if self.is_positive:
            return self.preferred_number * 10**self.exponent
        else:
            return -self.preferred_number * 10**self.exponent

    @classmethod
    def create(cls, value: float, series: str = 'E96',
               round: str = 'nearest') -> ESeriesValue:
        """Create a instance from float."""
        _launch_e_series_verify(series)
        series_size = _query_series_size(series)
        available_preferred_numbers = _query_available_preferred_numbers(
            series_size)
        significand, exponent = cal_significand_and_exponent(value)
        series_exponent = _query_rounded_value_index(
            significand, available_preferred_numbers, round)
        is_positive = True if significand >= 0 else False
        return cls(series_exponent, series_size, exponent, is_positive)


def _launch_e_series_size_verify(series_size: int):
    valid_series_size = [3, 6, 12, 24, 48, 96, 192]
    if series_size not in valid_series_size:
        raise ValueError(f"series_size not in {valid_series_size}.")


def _launch_e_series_verify(series: str):
    valid_series = ['E3', 'E6', 'E12', 'E24', 'E48', 'E96', 'E192']
    if series not in valid_series:
        raise ValueError(f'series {series} not in {valid_series}.')


def _query_series_size(series: str) -> int:
    """Return series size.

    Examples
    --------
    >>> _query_series_size('E3')
    3
    >>> _query_series_size('E192')
    192
    """
    _launch_e_series_verify(series)
    series_size_mapper = {
        'E3': 3,
        'E6': 6,
        'E12': 12,
        'E24': 24,
        'E48': 48,
        'E96': 96,
        'E192': 192
    }
    return series_size_mapper[series]


def _query_available_preferred_numbers(series_size: int) -> list[float]:
    """Return available preferred numbers.

    Examples
    --------
    >>> _query_available_preferred_numbers(3)
    [1.0, 2.2, 4.7]
    """
    _launch_e_series_size_verify(series_size)
    if series_size <= 24:
        return PREFERRED_NUMBER_E24[::24 // series_size]
    else:
        return PREFERRED_NUMBER_E192[::192 // series_size]


def _cal_significand_and_exponent(value: float) -> tuple[float, int]:
    """Return significand and exponent of the value.

    Examples
    --------
    >>> _cal_significand_and_exponent(3.3e9)
    (3.3, 9)
    >>> _cal_significand_and_exponent(0)
    (0, 0)
    >>> _cal_significand_and_exponent(-3.8e3)
    (-3.8, 3)
    """
    if value == 0:
        return 0, 0
    exponent = 0
    while abs(value) >= 10:
        value = value / 10
        exponent = exponent + 1
    while abs(value) < 1:
        value = value * 10
        exponent = exponent - 1
    return value, exponent


def cal_significand_and_exponent(value: npt.ArrayLike):
    """Return significand and exponent of the value.

    Examples
    --------
    >>> cal_significand_and_exponent(3.3e9)
    (array(3.3), array(9))
    >>> cal_significand_and_exponent([0, 2e4, -3.8e3])
    (array([ 0. ,  2. , -3.8]), array([0, 4, 3]))
    """
    return np.vectorize(_cal_significand_and_exponent, otypes=[float,
                                                               int])(value)


def _query_rounded_value_index(value: float,
                               available_values: list[float],
                               round: str = 'nearest'):
    """Return rounded value index in the list.

    Examples
    --------
    >>> _query_rounded_value_index(1.6, [1, 2.2, 4.7])
    0
    >>> _query_rounded_value_index(1.0, [1, 2.2, 4.7])
    0
    >>> _query_rounded_value_index(-1.8, [1, 2.2, 4.7])
    1
    >>> _query_rounded_value_index(10, [1, 2.2, 4.7])
    2
    """
    if value == 0:
        return 0
    if value < 0:
        value = -value
    ceil_index = bisect.bisect(available_values, value)
    floor_index = ceil_index - 1
    if ceil_index >= len(available_values):
        ceil_index = ceil_index - 1
    floor_value = available_values[floor_index]
    ceil_value = available_values[ceil_index]
    if round == 'floor':
        return floor_index
    elif round == 'ceil':
        return ceil_index
    else:
        return (floor_index
                if 2 * value <= floor_value + ceil_value else ceil_index)


class LED:
    """The LED electronic component.

    Parameters
    ----------
    name : str
        Name of the LED.
    id : str or int, optional
        ID in LCSC_. By default ``None``.
    voltage_current_relation : tuple of array_like of float
        The voltage current relation of LED.
        (voltages, currents) where `voltages` is the array_like of float
        and `currents` is the corresponding array_like of float.

    .. _LCSC: https://www.szlcsc.com/
    """

    def __init__(self,
                 name: str,
                 voltage_current_relation: tuple[npt.ArrayLike, npt.ArrayLike],
                 id: Optional[Union[str, int]] = None):
        self._name = name
        self._d = id
        voltages, currents = voltage_current_relation
        self._voltage_limit = (np.amin(voltages), np.amax(voltages))
        self._current_limit = (np.amin(currents), np.amax(currents))
        self._cal_voltage = interpolate.CubicSpline(currents,
                                                    voltages,
                                                    extrapolate=False)

    def get_name(self):
        """Return LED name."""
        return self._name

    def get_id(self):
        """Return store number."""
        return self._d

    def cal_voltage(self, current: npt.ArrayLike) -> np.ndarray:
        """Return LED corresponding voltage at given current.

        Parameters
        ----------
        current : array_like of float

        Returns
        -------
        np.ndarray
            Return ``np.nan`` if `current` out of range.
        """
        current = np.asarray(current)
        return self._cal_voltage(current)

    def _cal_current(self, voltage: float):

        def _eq_solve_current(current: float, voltage: float):
            return self._cal_voltage(current) - voltage

        if not self.is_voltage_valid(voltage):
            return np.nan
        else:
            return optimize.bisect(_eq_solve_current,
                                   self._current_limit[0],
                                   self._current_limit[1],
                                   args=(voltage, ))

    def cal_current(self, voltage: npt.ArrayLike) -> np.ndarray:
        """Return current at given voltage.

        Parameters
        ----------
        voltage : array_like of float
        Returns
        -------
        np.ndarray
            Return ``np.nan`` if `voltage` out of range.
        """
        return np.vectorize(self._cal_current)(voltage)

    def is_voltage_valid(self, voltage: npt.ArrayLike) -> np.ndarray:
        """Return whether voltage is valid."""
        voltage = np.asarray(voltage)
        condition = ((self._voltage_limit[0] < voltage) &
                     (voltage < self._voltage_limit[1]))
        return np.where(condition, True, False)

    def is_current_valid(self, current: npt.ArrayLike) -> np.ndarray:
        """Return whether current is valid."""
        current = np.asarray(current)
        condition = ((self._current_limit[0] < current) &
                     (current < self._current_limit[1]))
        return np.where(condition, True, False)

    def is_power_voltage_enough(self,
                                power_voltage: npt.ArrayLike) -> np.ndarray:
        """Return whether power voltage is large enough."""
        power_voltage = np.asarray(power_voltage)
        return np.where(power_voltage > self._voltage_limit[0], True, False)

    def validate_power_voltage(self, power_voltage: npt.ArrayLike):
        """Validate power voltage."""
        if not np.all(self.is_power_voltage_enough(power_voltage)):
            raise ValueError(f'Power voltage should be greater than '
                             f'{self._voltage_limit[0]} V.')

    # def get_voltage_lower_bound(self):
    #     """Return voltage lower bound."""
    #     return self._voltage_limit[0]
    #
    # def get_divider_resistance_limit(self, voltage):
    #     """Return divider resistance limit at given voltage.
    #
    #     Parameters
    #     ----------
    #     voltage : array_like of float
    #         Power voltage.
    #
    #     Returns
    #     -------
    #     np.ndarray
    #         Divider resistance lower bound.
    #     np.ndarray
    #         Divider resistance upper bound.
    #         If ``None``, infinite upper bound.
    #     """
    #     voltage = np.asarray(voltage)
    #     if np.any(voltage < self._voltage_limit[0]):
    #         raise ValueError(f'Supplied voltage smaller than '
    #                          f'lower bound {self._voltage_limit[0]} V')
    #     resistance_min = ((voltage - self._voltage_limit[1])
    #                       / self._current_limit[1])
    #     resistance_min = np.where(resistance_min < 0, 0, resistance_min)
    #     if self._current_limit[0] == 0:
    #         resistance_max = np.inf * np.ones_like(resistance_min)
    #     else:
    #         resistance_max = ((voltage - self._voltage_limit[0])
    #                           / self._current_limit[0])
    #     return resistance_min, resistance_max
    #
    # def _get_current(self, voltage):
    #     """Return corresponding current.
    #
    #     Parameters
    #     ----------
    #     voltage : array_like of float
    #         Voltage.
    #     """
    #     if np.any(voltage > self._voltage_limit[1]) or np.any(
    #             voltage < self._voltage_limit[0]):
    #         raise ValueError(
    #             f'Voltage outside voltage range {self._voltage_limit}')
    #
    #     current = []
    #     for v in voltage.flat:
    #
    #         def _equation(x):
    #             return self._voltage_current_relation(x) - v
    #
    #         res = optimize.bisect(_equation,
    #                               self._current_limit[0],
    #                               self._current_limit[1])
    #         current.append(res)
    #     return np.asarray(current) if len(current) > 1 else current[0]
    #
    # def get_work_current_limit(self, voltage):
    #     """Return working current limit at given voltage.
    #
    #     Parameters
    #     ----------
    #     voltage : array_like of float
    #         Power voltage.
    #
    #     Returns
    #     -------
    #     np.ndarray
    #         Working current lower bound.
    #     np.ndarray
    #         Working current upper bound.
    #     """
    #     if self._voltage_limit is None or self._current_limit is None:
    #         raise ValueError('Voltage-current relation is not set.')
    #     voltage = np.asarray(voltage)
    #     if np.any(voltage < self._voltage_limit[0]):
    #         raise ValueError(f'Supplied voltage smaller than '
    #                          f'lower bound {self._voltage_limit[0]} V')
    #     if voltage.ndim == 0:
    #         current_max = (self._current_limit[1]
    #                        if voltage > self._voltage_limit[1] else
    #                        self._get_current(voltage))
    #     else:
    #         current_max = np.where(voltage >= self._voltage_limit[1],
    #                                self._current_limit[1],
    #                                np.nan)
    #         indices = np.argwhere(np.isnan(current_max))
    #         for index in indices:
    #             current_max[index] = self._get_current(voltage[index])
    #     return self._current_limit[0] * np.ones_like(current_max), current_max
    #
    # def get_divider_resistance(self, voltage, current):
    #     """Return divider resistance.
    #
    #     Parameters
    #     ----------
    #     voltage : array_like of float
    #         Voltage supplied. Unit ``V``.
    #     current : array_like of float
    #         Working current. Unit ``A``.
    #
    #     Returns
    #     -------
    #     array_like of float
    #         Divider resistance. Unit ``Ω ``.
    #     """
    #     voltage = np.asarray(voltage)
    #     if np.any(voltage < self._voltage_limit[0]):
    #         raise ValueError(f'Supplied voltage smaller than '
    #                          f'lower bound {self._voltage_limit[0]} V')
    #     current = np.asarray(current)
    #     (current_lower_bound,
    #      current_upper_bound) = self.get_work_current_limit(voltage)
    #     if np.any(current < current_lower_bound) or np.any(
    #             current > current_upper_bound):
    #         raise ValueError('current out of range.')
    #     resistance = (voltage
    #                   - self._voltage_current_relation(current)) / current
    #     return resistance
    #
    # def get_work_current(self, voltage, divider_resistance):
    #     """Return work current.
    #
    #     Parameters
    #     ----------
    #     voltage : array_like of float
    #         Voltage supplied. Unit ``V``.
    #     divider_resistance : array_like of float
    #         Divider resistance. Unit ``Ω``.
    #
    #     Returns
    #     -------
    #     array_like of float
    #         Current. Unit ``A ``.
    #     """
    #     voltage = np.asarray(voltage)
    #     if np.any(voltage < self._voltage_limit[0]):
    #         raise ValueError(f'Supplied voltage smaller than '
    #                          f'lower bound {self._voltage_limit[0]} V')
    #     divider_resistance = np.asarray(divider_resistance)
    #     (resistance_lower_bound,
    #      resistance_upper_bound) = self.get_divider_resistance_limit(voltage)
    #     if np.any(divider_resistance < resistance_lower_bound) or np.any(
    #             divider_resistance > resistance_upper_bound):
    #         raise ValueError('divider resistance out of range.')
    #     current = []
    #     for v, r in np.nditer([voltage, divider_resistance]):
    #
    #         def _equation(x):
    #             return ((v - self._voltage_current_relation(x)) / r - x)
    #
    #         result = optimize.bisect(_equation,
    #                                  self._current_limit[0],
    #                                  self._current_limit[1])
    #         current.append(result)
    #     return np.asarray(current)
    #


TYPICAL_LED = LED('typical LED',
                  ([2.7524, 2.8800, 3.0030, 3.1260, 3.2490, 3.3766],
                   [0.0, 4.772e-3, 9.76e-3, 14.748e-3, 19.735e-3, 24.605e-3]))

TYPICAL_LED_RED = LED('typical LED red',
                      ([1.7736, 1.82944, 1.88781, 1.94365, 2.0, 2.05533
                        ], [0.0, 5.0e-3, 10.0e-3, 15.0e-3, 20.0e-3, 25.0e-3]))
