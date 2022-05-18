from typing import List

import click
import numpy as np

from hktkzyx_toolbox import electronics
from hktkzyx_toolbox import misc
from hktkzyx_toolbox.electronics import LED
from hktkzyx_toolbox.electronics import TYPICAL_LED
from hktkzyx_toolbox.electronics import TYPICAL_LED_RED


@click.group()
@click.version_option(package_name='hktkzyx-toolbox')
def hktkzyx_electronics():
    """电子工具箱"""
    pass


def is_led_power_voltage_enough(led: LED, voltages: List[float]):
    if np.all(led.is_power_voltage_enough(voltages)):
        return True
    click.echo(f'电压应不小于 {led.query_least_power_voltage()} V')
    return False


@hktkzyx_electronics.command()
@click.option('--voltage',
              '-v',
              multiple=True,
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              help='电压(V)')
@click.option('--kind',
              '-k',
              type=click.Choice(['r', 'g', 'b', 'w', 'o'],
                                case_sensitive=False),
              default='o',
              help=("LED 种类 'r': 红色, 'g': 绿色, 'b': 蓝色, "
                    "'w': 白色, 'o': 其它"))
def led_divider_resistance_range(voltage, kind):
    """LED 分压电阻范围"""
    led = TYPICAL_LED_RED if kind == 'r' else TYPICAL_LED
    if is_led_power_voltage_enough(led, voltage):
        (lower_bound, upper_bound
         ) = led.cal_divider_resistance_range_if_power_supplied(voltage)
        lower_bound = np.ceil(lower_bound)
        upper_bound = np.floor(upper_bound)
        for v, lower, upper in zip(voltage, lower_bound, upper_bound):
            click.echo(f'{v} V: {lower:.0f} Ω to {upper:.0f} Ω')


@hktkzyx_electronics.command()
@click.option('--voltage',
              '-v',
              multiple=True,
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              help='电压(V)')
@click.option('--kind',
              '-k',
              type=click.Choice(['r', 'g', 'b', 'w', 'o'],
                                case_sensitive=False),
              default='o',
              help=("LED 种类 'r': 红色, 'g': 绿色, 'b': 蓝色, "
                    "'w': 白色, 'o': 其它"))
def led_work_current_range(voltage, kind):
    """LED 分压电阻范围"""
    led = TYPICAL_LED_RED if kind == 'r' else TYPICAL_LED
    if is_led_power_voltage_enough(led, voltage):
        (lower_bound,
         upper_bound) = led.cal_work_current_range_if_power_supplied(voltage)
        lower_bound = np.ceil(10000 * lower_bound) / 10
        upper_bound = np.floor(10000 * upper_bound) / 10
        for v, lower, upper in zip(voltage, lower_bound, upper_bound):
            click.echo(f'{v} V: {lower:.1f} mA to {upper:.1f} mA')


@hktkzyx_electronics.command()
@click.option('--voltage',
              '-v',
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              prompt='电压(V)',
              help='电压(V)')
@click.option('--current',
              '-c',
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              prompt='电流(mA)',
              help='电流(V)')
@click.option('--kind',
              '-k',
              type=click.Choice(['r', 'g', 'b', 'w', 'o'],
                                case_sensitive=False),
              default='o',
              help=("LED 种类 'r': 红色, 'g': 绿色, 'b': 蓝色, "
                    "'w': 白色, 'o': 其它"))
def led_divider_resistance(voltage, current, kind):
    """LED 分压电阻"""
    led = TYPICAL_LED_RED if kind == 'r' else TYPICAL_LED
    if not is_led_power_voltage_enough(led, voltage):
        return
    current_in_amps = current * 1e-3
    if not is_led_work_current_in_range(led, voltage, current_in_amps):
        return
    resistance = led.cal_divider_resistance(voltage, current_in_amps)
    click.echo(f'{resistance:.0f} Ω')


def is_led_work_current_in_range(led: LED, voltage: float, current: float):
    """Return whether work current is in range.

    led : LED
        LED.
    voltage : float
        Voltage in volts.
    current : float
        Current in amps.
    """
    (current_lower_bound, current_upper_bound
     ) = led.cal_work_current_range_if_power_supplied(voltage)
    if current >= current_lower_bound and current <= current_upper_bound:
        return True
    click.echo('电流超出范围')
    click.echo("请使用 'hktkzyx-electronics led-work-current-range' "
               "查看电流范围")
    return False


@hktkzyx_electronics.command()
@click.option('--voltage',
              '-v',
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              prompt='电压(V)',
              help='电压(V)')
@click.option('--resistance',
              '-r',
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              prompt='分压电阻(Ω)',
              help='分压电阻(Ω)')
@click.option('--kind',
              '-k',
              type=click.Choice(['r', 'g', 'b', 'w', 'o'],
                                case_sensitive=False),
              default='o',
              help=("LED 种类 'r': 红色, 'g': 绿色, 'b': 蓝色, "
                    "'w': 白色, 'o': 其它"))
def led_work_current(voltage, resistance, kind):
    """LED 工作电流"""
    led = TYPICAL_LED_RED if kind == 'r' else TYPICAL_LED
    if is_led_power_voltage_enough(led, voltage):
        (lower_bound, upper_bound
         ) = led.cal_divider_resistance_range_if_power_supplied(voltage)
        if resistance < lower_bound or resistance > upper_bound:
            click.echo('分压电阻超出范围')
            click.echo(
                "请使用 'hktkzyx-electronics led-divider-resistance-range' "
                "查看分压电阻范围")
            return
        current = led.cal_work_current(voltage, resistance)
        click.echo(f'{1000*current:.1f} mA')


@hktkzyx_electronics.command()
@click.argument('resistance', type=click.FloatRange(min=0, clamp=True))
@click.option('--series',
              '-s',
              type=click.Choice(
                  ['E3', 'E6', 'E12', 'E24', 'E48', 'E96', 'E192']),
              default='E24',
              help='标准电阻系列')
@click.option('--mode',
              '-m',
              type=click.Choice(['nearest', 'floor', 'ceil']),
              default='nearest',
              help='近似模式')
def standard_resistance(resistance, series, mode):
    """查询标准电阻

    RESISTANCE 是要查询的电阻值
    """
    standard_resistance = electronics.ESeriesValue.create(
        resistance, series, mode)
    result = misc.si_formatter(standard_resistance.to_scalar(),
                               significant_figures=3,
                               unit='Ω')
    click.echo(result)
