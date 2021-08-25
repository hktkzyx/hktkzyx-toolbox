from hktkzyx_toolbox.electronics import get_standard_resistance


def test_get_standard_resistance():
    input_values = (0.2, 1.0, 301, 101e3, 10e6)
    expected_values = (1.0, 1.0, 300, 100e3, 9.1e6)
    for i, e in zip(input_values, expected_values):
        assert get_standard_resistance(i) == e

    input_values = (0.2, 1.0, 301, 101e3, 10e6)
    expected_values = ('1.0', '1.0', '300.0', '100.0K', '9.1M')
    for i, e in zip(input_values, expected_values):
        assert get_standard_resistance(i, human_format=True) == e
