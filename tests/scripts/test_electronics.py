from hktkzyx_toolbox.scripts import electronics


def test_led_divider_resistance_limit(runner):
    results = runner.invoke(electronics.led_divider_resistance_range, ['-v 2'])
    assert results.exit_code == 0
    assert results.output == '电压应不小于 2.7524 V\n'
    results = runner.invoke(electronics.led_divider_resistance_range,
                            ['-v 4', '-v 5'])
    assert results.exit_code == 0
    assert results.output == ('4.0 V: 26 Ω to inf Ω\n'
                              '5.0 V: 66 Ω to inf Ω\n')


def test_led_work_current_limit(runner):
    results = runner.invoke(electronics.led_work_current_range, ['-v 2'])
    assert results.exit_code == 0
    assert results.output == '电压应不小于 2.7524 V\n'
    results = runner.invoke(electronics.led_work_current_range,
                            ['-v 3', '-v 5'])
    assert results.exit_code == 0
    assert results.output == ('3.0 V: 0.0 mA to 9.6 mA\n'
                              '5.0 V: 0.0 mA to 24.6 mA\n')


def test_led_divider_resistance(runner):
    results = runner.invoke(electronics.led_divider_resistance,
                            ['-v 2', '-c 1'])
    assert results.exit_code == 0
    assert results.output == '电压应不小于 2.7524 V\n'
    results = runner.invoke(electronics.led_divider_resistance,
                            ['-v 5', '-c 100'])
    assert results.exit_code == 0
    assert results.output == ('电流超出范围\n'
                              "请使用 "
                              "'hktkzyx-electronics led-work-current-range' "
                              "查看电流范围\n")
    results = runner.invoke(electronics.led_divider_resistance,
                            ['-v 5', '-c 1'])
    assert results.exit_code == 0
    assert results.output == '2219 Ω\n'


def test_led_work_current(runner):
    results = runner.invoke(electronics.led_work_current, ['-v 2', '-r 1'])
    assert results.exit_code == 0
    assert results.output == '电压应不小于 2.7524 V\n'
    results = runner.invoke(electronics.led_work_current, ['-v 5', '-r 1'])
    assert results.exit_code == 0
    assert results.output == (
        '分压电阻超出范围\n'
        "请使用 "
        "'hktkzyx-electronics led-divider-resistance-range' "
        "查看分压电阻范围\n")
    results = runner.invoke(electronics.led_work_current, ['-v 5', '-r 1000'])
    assert results.exit_code == 0
    assert results.output == '2.2 mA\n'


def test_standard_resistance(runner):
    results = runner.invoke(electronics.standard_resistance, ['3200'])
    assert results.exit_code == 0
    assert results.output == '3.30 kΩ\n'
    results = runner.invoke(electronics.standard_resistance,
                            ['--mode', 'floor', '3200'])
    assert results.exit_code == 0
    assert results.output == '3.00 kΩ\n'
    results = runner.invoke(electronics.standard_resistance,
                            ['--mode', 'ceil', '3100'])
    assert results.exit_code == 0
    assert results.output == '3.30 kΩ\n'
