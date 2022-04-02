import numpy as np
import pytest

from hktkzyx_toolbox import electronics


@pytest.fixture
def led():
    voltages = np.array([0.0, 1.0, 2.0, 5.0])
    currents = 0.2 * np.array([0.0, 1.0, 2.0, 5.0]) + 1
    return electronics.LED('test', (voltages, currents))


def test_led_get_variables(led):
    assert led.get_name() == 'test'
    assert led.get_id() is None


def test_led_cal_voltage(led):
    voltages = led.cal_voltage([0, 1.5, 3])
    assert np.array_equal(voltages, [np.nan, 2.5, np.nan], equal_nan=True)


def test_led_cal_current(led):
    currents = led.cal_current([-3, 2.5, 10])
    assert np.array_equal(currents, [np.nan, 1.5, np.nan], equal_nan=True)


def test_led_cal_current_multiple_dimension_ndarray(led):
    currents = led.cal_current([[-3, 2.5, 10], [1, 2, 3]])
    assert np.isnan(currents[0, 0])
    assert np.isnan(currents[0, 2])
    currents = np.nan_to_num(currents)
    expected_currents = np.array([[0, 1.5, 0], [1.2, 1.4, 1.6]])
    assert np.amax(np.abs(currents - expected_currents)) < 1e-5


def test_led_is_voltage_valid(led):
    is_valid = led.is_voltage_valid([-3, 2.5, 10])
    assert np.array_equal(is_valid, [False, True, False])


def test_led_is_current_valid(led):
    is_valid = led.is_current_valid([0, 1.5, 10])
    assert np.array_equal(is_valid, [False, True, False])


def test_led_is_power_voltage_enough(led):
    is_enough = led.is_power_voltage_enough([-3, 2.5, 10])
    assert np.array_equal(is_enough, [False, True, True])


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


#
# def test_LED_set_voltage_current_relation(led):
#     voltage_array = np.array([0.0, 1.0, 2.0, 5.0])
#     current_array = 0.5 * np.array([0.0, 1.0, 2.0, 5.0])
#     led.set_voltage_current_relation(voltage_array, current_array)
#     func = led._voltage_current_relation
#     assert led._name == 'test'
#     assert np.amax(np.abs(func(current_array) - voltage_array)) < 1e-5
#
#
# def test_LED_get_divider_resistance_limit(led):
#     expect_min, expect_max = led.get_divider_resistance_limit([10.0, 2.5])
#     assert np.amax(np.abs(expect_min - np.array([2.5, 0]))) < 1e-5
#     assert np.amax(np.abs(expect_max - np.array([10.0, 2.5]))) < 1e-5
#
#
# def test_LED_get_divider_resistance_limit_inf_upper_bound(led):
#     led.set_voltage_current_relation([0, 10], [0, 2])
#     _, upper = led.get_divider_resistance_limit([3, 9])
#     assert np.all(np.isinf(upper))
#
#
# def test_LED_get_work_current_limit(led):
#     expect_min, expect_max = led.get_work_current_limit([10.0, 2.5])
#     assert np.amax(np.abs(expect_min - np.array([1.0, 1.0]))) < 1e-5
#     assert np.amax(np.abs(expect_max - np.array([2.0, 1.5]))) < 1e-5
#
#
# def test_LED_get_divider_resistance(led):
#     with pytest.raises(ValueError):
#         led.get_divider_resistance(10.0, 10.0)
#     with pytest.raises(ValueError):
#         led.get_divider_resistance(10.0, 0)
#     resistance = led.get_divider_resistance(10.0, [1.5, 1.2])
#     assert np.amax(np.abs(resistance - np.array([5, 7.5]))) < 1e-5
#
#
# def test_LED_get_work_current(led):
#     with pytest.raises(ValueError):
#         led.get_work_current(500.0, 1.0)
#     with pytest.raises(ValueError):
#         led.get_work_current(5.0, 100)
#     current = led.get_work_current(10.0, [5, 7.5])
#     assert np.amax(np.abs(current - np.array([1.5, 1.2]))) < 1e-5
