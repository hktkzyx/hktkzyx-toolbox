import numpy as np
import pytest

from hktkzyx_toolbox import electronics


@pytest.fixture
def led():
    voltages = np.array([0.0, 1.0, 2.0, 5.0])
    currents = 0.2 * np.array([0.0, 1.0, 2.0, 5.0]) + 1
    return electronics.LED('test', (voltages, currents))


def test_LED_get_variables(led):
    assert led.get_name() == 'test'
    assert led.get_id() is None


def test_LED_cal_voltage(led):
    voltages = led.cal_voltage([0, 1.5, 3])
    assert np.array_equal(voltages, [np.nan, 2.5, np.nan], equal_nan=True)


def test_LED_cal_current(led):
    currents = led.cal_current([-3, 2.5, 10])
    assert np.array_equal(currents, [np.nan, 1.5, np.nan], equal_nan=True)


def test_LED_cal_current_multiple_dimension_ndarray(led):
    currents = led.cal_current([[-3, 2.5, 10], [1, 2, 3]])
    assert np.isnan(currents[0, 0])
    assert np.isnan(currents[0, 2])
    currents = np.nan_to_num(currents)
    expected_currents = np.array([[0, 1.5, 0], [1.2, 1.4, 1.6]])
    assert np.amax(np.abs(currents - expected_currents)) < 1e-5


def test_LED_is_voltage_valid(led):
    is_valid = led.is_voltage_valid([-3, 2.5, 10])
    assert np.array_equal(is_valid, [False, True, False])


def test_LED_is_current_valid(led):
    is_valid = led.is_current_valid([0, 1.5, 10])
    assert np.array_equal(is_valid, [False, True, False])


def test_LED_is_power_voltage_enough(led):
    is_enough = led.is_power_voltage_enough([-3, 2.5, 10])
    assert np.array_equal(is_enough, [False, True, True])


def test_LED_validate_power_voltage(led):
    with pytest.raises(ValueError):
        led.validate_power_voltage(-3)


def test_LED_cal_work_current_range(led):
    with pytest.raises(ValueError):
        led.cal_work_current_range_if_power_supplied(-3)
    (current_lb,
     current_ub) = led.cal_work_current_range_if_power_supplied([2.5, 10])
    expected_lb = np.array([1, 1])
    expected_ub = np.array([1.5, 2])
    assert np.amax(np.abs(current_lb - expected_lb)) < 1e-5
    assert np.amax(np.abs(current_ub - expected_ub)) < 1e-5


def test_LED_cal_divider_resistance_range(led):
    with pytest.raises(ValueError):
        led.cal_divider_resistance_range_if_power_supplied(-3)
    (lb, ub) = led.cal_divider_resistance_range_if_power_supplied([2.5, 10])
    expected_lb = np.array([0, 2.5])
    expected_ub = np.array([2.5, 10])
    assert np.amax(np.abs(lb - expected_lb)) < 1e-5
    assert np.amax(np.abs(ub - expected_ub)) < 1e-5


def test_LED_cal_divider_resistance_infinite_upper_bound():
    led = electronics.LED('test', ([0, 5], [0, 1]))
    assert led.cal_divider_resistance_range_if_power_supplied(10) == (5,
                                                                      np.inf)


def test_LED_cal_divider_resistance(led):
    resistances = led.cal_divider_resistance(10, [1, 1.5, 2])
    expected_resistances = np.array([10, 5, 2.5])
    assert np.amax(np.abs(resistances - expected_resistances)) < 1e-5


def test_LED_cal_divider_resistance_current_out_of_range(led):
    with pytest.raises(ValueError):
        led.cal_divider_resistance(10, 0.2)
    with pytest.raises(ValueError):
        led.cal_divider_resistance(10, 100)
    with pytest.raises(ValueError):
        led.cal_divider_resistance(2.5, 2)


def test_LED_cal_work_current_resistance_out_of_range(led):
    with pytest.raises(ValueError):
        led.cal_work_current(10, 1)
    with pytest.raises(ValueError):
        led.cal_work_current(10, 100)


def test_ESeriesValue_to_scalar():
    series_value = electronics.ESeriesValue(12, 24, 3, False)
    assert series_value.to_scalar() == -3.3e3


def test_ESeriesValue_series_size_verify():
    with pytest.raises(ValueError):
        electronics.ESeriesValue(12, 2, 3, False)


def test_ESeriesValue_create():
    series_value = electronics.ESeriesValue.create(-3.5e3, 'E24')
    assert series_value.series == 'E24'
    assert series_value.series_size == 24
    assert series_value.series_exponent == 13
    assert series_value.exponent == 3
    assert not series_value.is_positive
    assert series_value.preferred_number == 3.6


def test_ESeriesValue_create_ceil():
    series_value = electronics.ESeriesValue.create(-3.32e3, 'E24', 'ceil')
    assert series_value.series == 'E24'
    assert series_value.series_size == 24
    assert series_value.series_exponent == 13
    assert series_value.exponent == 3
    assert not series_value.is_positive
    assert series_value.preferred_number == 3.6


def test_ESeriesValue_create_floor():
    series_value = electronics.ESeriesValue.create(-3.5e3, 'E24', 'floor')
    assert series_value.series == 'E24'
    assert series_value.series_size == 24
    assert series_value.series_exponent == 12
    assert series_value.exponent == 3
    assert not series_value.is_positive
    assert series_value.preferred_number == 3.3
