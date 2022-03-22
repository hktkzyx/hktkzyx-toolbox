import click

from ..finance import social_pension


@click.command()
@click.option('--social-mean-salary',
              '-s',
              'social_mean_salary',
              type=click.FloatRange(min=0, min_open=True),
              required=True,
              prompt='社会平均工资',
              help='社会平均工资')
@click.option('--salary-factor',
              '-f',
              'salary_factor',
              type=click.FloatRange(min=0.6, max=3.0, clamp=True),
              required=True,
              prompt='缴费指数',
              help='缴费指数')
@click.option('--years',
              '-y',
              type=click.IntRange(min=15, clamp=True),
              required=True,
              prompt='缴费年限',
              help='缴费年限')
def social_fundamental_pension(social_mean_salary, salary_factor, years):
    """基础养老金"""
    value = social_pension.get_fundamental_pension(
        social_mean_salary=social_mean_salary,
        salary_factor=salary_factor,
        accumulated_years=years)
    click.echo(f'{value:.2f}')
