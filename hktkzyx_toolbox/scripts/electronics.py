import click
import numpy as np

from ..electronics import TYPICAL_LED
from ..electronics import TYPICAL_LED_RED


@click.group()
@click.version_option(package_name='hktkzyx-toolbox')
def hktkzyx_electronics():
    """电子工具箱"""
    pass


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
def led_divider_resistance_limit(voltage, kind):
    """LED 分压电阻范围"""
    if kind == 'r':
        led = TYPICAL_LED_RED
    else:
        led = TYPICAL_LED
    if np.any(voltage < led.get_voltage_lower_bound()):
        click.echo(f'电压应不小于 {led.get_voltage_lower_bound()} V')
        return
    lower_bound, upper_bound = led.get_divider_resistance_limit(voltage)
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
def led_work_current_limit(voltage, kind):
    """LED 分压电阻范围"""
    if kind == 'r':
        led = TYPICAL_LED_RED
    else:
        led = TYPICAL_LED
    if np.any(voltage < led.get_voltage_lower_bound()):
        click.echo(f'电压应不小于 {led.get_voltage_lower_bound()} V')
        return
    lower_bound, upper_bound = led.get_work_current_limit(voltage)
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
    if kind == 'r':
        led = TYPICAL_LED_RED
    else:
        led = TYPICAL_LED
    if voltage < led.get_voltage_lower_bound():
        click.echo(f'电压应不小于 {led.get_voltage_lower_bound()} V')
        return
    current = current * 1e-3
    (current_lower_bound,
     current_upper_bound) = led.get_work_current_limit(voltage)
    if current < current_lower_bound or current > current_upper_bound:
        click.echo('电流超出范围')
        click.echo("请使用 'hktkzyx-electronics led-work-current-limit' "
                   "查看电流范围")
        return
    resistance = led.get_divider_resistance(voltage, current)
    click.echo(f'{resistance:.0f} Ω')
