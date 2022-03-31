import numpy as np
import pytest

from hktkzyx_toolbox import electronics


@pytest.fixture
def led():
    voltage_array = np.array([0.0, 1.0, 2.0, 5.0])
    current_array = 0.2 * np.array([0.0, 1.0, 2.0, 5.0]) + 1
    return electronics.LED('test',
                           voltage_array=voltage_array,
                           current_array=current_array)


def test_LED_set_voltage_current_relation(led):
    voltage_array = np.array([0.0, 1.0, 2.0, 5.0])
    current_array = 0.5 * np.array([0.0, 1.0, 2.0, 5.0])
    led.set_voltage_current_relation(voltage_array, current_array)
    func = led._voltage_current_relation
    assert led.name == 'test'
    assert np.amax(np.abs(func(current_array) - voltage_array)) < 1e-5


def test_LED_get_divider_resistance_limit(led):
    expect_min, expect_max = led.get_divider_resistance_limit([10.0, 2.5])
    assert np.amax(np.abs(expect_min - np.array([2.5, 0]))) < 1e-5
    assert np.amax(np.abs(expect_max - np.array([10.0, 2.5]))) < 1e-5


def test_LED_get_divider_resistance_limit_inf_upper_bound(led):
    led.set_voltage_current_relation([0, 10], [0, 2])
    _, upper = led.get_divider_resistance_limit([3, 9])
    assert np.all(np.isinf(upper))


def test_LED_get_work_current_limit(led):
    expect_min, expect_max = led.get_work_current_limit([10.0, 2.5])
    assert np.amax(np.abs(expect_min - np.array([1.0, 1.0]))) < 1e-5
    assert np.amax(np.abs(expect_max - np.array([2.0, 1.5]))) < 1e-5


def test_LED_get_divider_resistance(led):
    with pytest.raises(ValueError):
        led.get_divider_resistance(10.0, 10.0)
    with pytest.raises(ValueError):
        led.get_divider_resistance(10.0, 0)
    resistance = led.get_divider_resistance(10.0, [1.5, 1.2])
    assert np.amax(np.abs(resistance - np.array([5, 7.5]))) < 1e-5


def test_LED_get_work_current(led):
    with pytest.raises(ValueError):
        led.get_work_current(500.0, 1.0)
    with pytest.raises(ValueError):
        led.get_work_current(5.0, 100)
    current = led.get_work_current(10.0, [5, 7.5])
    assert np.amax(np.abs(current - np.array([1.5, 1.2]))) < 1e-5
