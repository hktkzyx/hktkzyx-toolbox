import numpy as np
import pytest
from hktkzyx_toolbox.electronics import (LED,
                                         get_human_format_resistance,
                                         get_standard_resistance)


def test_get_human_format_resistance():
    with pytest.raises(ValueError):
        get_human_format_resistance(1e9)
    assert get_human_format_resistance(1e3) == '1.0K'
    assert get_human_format_resistance(1e3, 4) == '1.0000K'


def test_get_standard_resistance():
    input_values = (0.2, 1.0, 301, 101e3, 10e6)
    expected_values = (1.0, 1.0, 300, 100e3, 9.1e6)
    for i, e in zip(input_values, expected_values):
        assert get_standard_resistance(i) == e

    expected_values = ('1.0', '1.0', '300.0', '100.0K', '9.1M')
    for i, e in zip(input_values, expected_values):
        assert get_standard_resistance(i, human_format=True) == e

    expected_values = (None, '1.0', '300.0', '100.0K', '9.1M')
    for i, e in zip(input_values, expected_values):
        assert get_standard_resistance(i, kind='down', human_format=True) == e

    expected_values = ('1.0', '1.0', '330.0', '110.0K', None)
    for i, e in zip(input_values, expected_values):
        assert get_standard_resistance(i, kind='up', human_format=True) == e

    with pytest.raises(ValueError):
        get_standard_resistance(98, 'round')


@pytest.fixture
def led():
    voltage_array = np.array([0.0, 1.0, 2.0, 5.0])
    current_array = 0.2 * np.array([0.0, 1.0, 2.0, 5.0])
    return LED('test',
               voltage_array=voltage_array,
               current_array=current_array)


def test_LED_set_voltage_current_relation(led):
    voltage_array = np.array([0.0, 1.0, 2.0, 5.0])
    current_array = 0.5 * np.array([0.0, 1.0, 2.0, 5.0])
    func = led.set_voltage_current_relation(voltage_array, current_array)
    assert led.name == 'test'
    assert abs(func(0.5) - 1.0) < 1e-5


def test_LED_get_current_and_resistance(led):
    with pytest.raises(ValueError):
        led.get_current_and_resistance(5.0)

    _, resistance = led.get_current_and_resistance(5.0, current=0.2)
    assert abs(resistance - 20) < 1e-5
    current, _ = led.get_current_and_resistance(5.0, resistance=20.0)
    assert abs(current - 0.2) < 1e-5


def test_get_divider_resistance(led):
    with pytest.raises(ValueError):
        led.get_divider_resistance(5.0, 10.0)
    with pytest.raises(ValueError):
        led.get_divider_resistance(5.0, 0)
    resistance = led.get_divider_resistance(5.0, 0.2)
    assert abs(resistance - 20) < 1e-5


def test_get_work_current(led):
    with pytest.raises(ValueError):
        led.get_work_current(500.0, 1.0)
    with pytest.raises(ValueError):
        led.get_work_current(5.0, 0)
    current = led.get_work_current(5.0, 20.0)
    assert abs(current - 0.2) < 1e-5
