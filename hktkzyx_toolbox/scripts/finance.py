import click
import numpy as np

from ..finance import social_pension


@click.group()
@click.version_option(package_name='hktkzyx-toolbox')
def hktkzyx_finance():
    """金融工具箱"""
    pass


@hktkzyx_finance.command()
@click.option('--social-mean-salary',
              '-s',
              type=click.FloatRange(min=0, min_open=True),
              required=True,
              prompt='社会平均工资',
              help='社会平均工资')
@click.option('--salary-factor',
              '-f',
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
    value = social_pension.cal_fundamental_pension(
        social_mean_salary=social_mean_salary,
        salary_factor=salary_factor,
        accumulated_years=years)
    click.echo(f'{value:.2f}')


@hktkzyx_finance.command()
@click.option('--balance',
              '-b',
              type=click.FloatRange(min=0),
              required=True,
              prompt='个人账户余额',
              help='个人账户余额')
@click.option('--retire-age',
              '-a',
              type=click.IntRange(min=40, max=70, clamp=True),
              default=60,
              help='退休年龄')
def social_personal_pension(balance, retire_age):
    """个人养老金"""
    value = social_pension.cal_personal_pension(balance=balance,
                                                retire_age=retire_age)
    click.echo(f'{value:.2f}')


@hktkzyx_finance.command()
@click.option('--age',
              '-a',
              type=click.IntRange(min=0, clamp=True),
              required=True,
              prompt='上年末年龄',
              help='上年末年龄')
@click.option('--retire-age',
              '-t',
              type=click.IntRange(min=40, max=70, clamp=True),
              default=60,
              show_default=True,
              help='退休年龄')
@click.option('--balance',
              '-b',
              type=click.FloatRange(min=0, clamp=True),
              default=0,
              show_default=True,
              help='上年末个人账户余额')
@click.option('--accumulated-years',
              '-y',
              type=click.IntRange(min=0, clamp=True),
              default=0,
              show_default=True,
              help='已经缴费年限')
@click.option('--salary-factor',
              '-f',
              type=click.FloatRange(min=0.6, max=3, clamp=True),
              default=1,
              show_default=True,
              help='上年末平均缴费指数')
@click.option('--salary',
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              prompt='上年度月缴费基数',
              help='上年度月缴费基数')
@click.option('--salary-rate',
              type=float,
              required=True,
              prompt='缴费基数涨幅',
              help='缴费基数涨幅')
@click.option('--interest-rate',
              '-i',
              type=float,
              required=True,
              prompt='个人账户记账利率',
              help='个人账户记账利率')
@click.option('--social-mean-salary',
              type=click.FloatRange(min=0, clamp=True),
              required=True,
              prompt='上年度社会平均月工资',
              help='上年度社会平均月工资')
@click.option('--social-mean-salary-rate',
              type=float,
              required=True,
              prompt='社会平均工资涨幅',
              help='社会平均工资涨幅')
@click.option('--ratio',
              type=click.FloatRange(min=0, max=1, clamp=True),
              default=0.08,
              show_default=True,
              help='缴费比例')
def social_pension_predict(age,
                           retire_age,
                           balance,
                           accumulated_years,
                           salary_factor,
                           salary,
                           salary_rate,
                           interest_rate,
                           social_mean_salary,
                           social_mean_salary_rate,
                           ratio):
    """养老保险待遇测算"""
    years_to_go = retire_age - age
    predicted_salaries = (salary *
                          (1 + salary_rate)**np.arange(1, years_to_go + 1))
    predicted_social_mean_salary = (
        social_mean_salary *
        (1 + social_mean_salary_rate)**np.arange(1, years_to_go + 1))
    predicted_salary_factor = social_pension.get_predicted_salary_factor(
        current_salary_factor=salary_factor,
        current_accumulated_years=accumulated_years,
        salaries=predicted_salaries,
        social_mean_salaries=predicted_social_mean_salary)
    predicted_balance = social_pension.cal_predicted_personal_balance(
        current_balance=balance,
        current_age=age,
        retire_age=retire_age,
        payments=12 * predicted_salaries * ratio,
        predicted_rates=interest_rate)
    fundamental_pension = social_pension.cal_fundamental_pension(
        social_mean_salary=predicted_social_mean_salary[-1],
        salary_factor=predicted_salary_factor,
        accumulated_years=accumulated_years + years_to_go)
    personal_pension = social_pension.cal_personal_pension(
        balance=predicted_balance, retire_age=retire_age)
    click.echo(f'基础养老金每月: {fundamental_pension:.2f}')
    click.echo(f'个人养老金每月: {personal_pension:.2f}')
    click.echo(f'社保养老金每月: {fundamental_pension+personal_pension:.2f}')
