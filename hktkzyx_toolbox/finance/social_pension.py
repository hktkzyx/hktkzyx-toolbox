from typing import Optional

import numpy as np

COLLECTION_MONTHS = {
    40: 233,
    41: 230,
    42: 226,
    43: 223,
    44: 220,
    45: 216,
    46: 212,
    47: 208,
    48: 204,
    49: 199,
    50: 195,
    51: 190,
    52: 185,
    53: 180,
    54: 175,
    55: 170,
    56: 164,
    57: 158,
    58: 152,
    59: 145,
    60: 139,
    61: 132,
    62: 125,
    63: 117,
    64: 109,
    65: 101,
    66: 93,
    67: 84,
    68: 75,
    69: 65,
    70: 56,
}


def _query_collection_months(retire_age: int) -> int:
    if retire_age < 40:
        return COLLECTION_MONTHS[40]
    elif retire_age > 70:
        return COLLECTION_MONTHS[70]
    else:
        return COLLECTION_MONTHS[retire_age]


def query_collection_months(retire_age) -> np.ndarray:
    """获取计发月份

    Parameters
    ----------
    retire_age : array_like of int
        退休年龄

    Examples
    --------
    >>> query_collection_months(20)
    array(233)
    >>> query_collection_months(80)
    array(56)
    >>> query_collection_months(65)
    array(101)
    >>> query_collection_months([60, 65, 70])
    array([139, 101,  56])
    """
    return np.vectorize(_query_collection_months, otypes=['int'])(retire_age)


def cal_fundamental_pension(social_mean_salary,
                            salary_factor,
                            accumulated_years) -> np.ndarray:
    """计算基础养老金

    Parameters
    ----------
    social_mean_salary : array_like of float
        社会平均工资
    salary_factor : array_like of float
        缴费指数
    accumulated_years : array_like of int
        缴费年限

    Examples
    --------
    >>> cal_fundamental_pension(1000, 0.5, 40)
    320.0
    >>> cal_fundamental_pension(1000, 3.5, 50)
    1000.0
    >>> cal_fundamental_pension(1000, 2.2, 40)
    640.0
    >>> cal_fundamental_pension(1000, [2.2, 1.0, 2.6], 40)
    array([640., 400., 720.])
    """
    salary_factor = np.asarray(salary_factor)
    salary_factor = np.where(salary_factor < 0.6, 0.6, salary_factor)
    salary_factor = np.where(salary_factor > 3, 3.0, salary_factor)
    social_mean_salary = np.asarray(social_mean_salary)
    accumulated_years = np.asarray(accumulated_years)
    return (social_mean_salary *
            (1 + salary_factor) / 2 * accumulated_years * 0.01)


def cal_personal_pension(balance, retire_age) -> np.ndarray:
    """计算个人养老金

    Parameters
    ----------
    balance : array_like of float
        养老金个人账户余额
    retire_age : array_like of int
        退休年龄

    Examples
    --------
    >>> cal_personal_pension(1.39e3, 60)
    10.0
    >>> cal_personal_pension([139000, 101000], [60, 65])
    array([1000., 1000.])
    """
    return np.asarray(balance) / query_collection_months(retire_age)


def cal_predicted_personal_balance(current_balance: float,
                                   current_age: int,
                                   retire_age: int,
                                   payments,
                                   predicted_rates) -> float:
    """预测退休时个人账户余额

    Parameters
    ----------
    current_balance : float
        上年度末个人账户余额
    current_age : int
        上年度末年龄
    retire_age : int
        退休年龄
    payments : float or (N, ) array_like of float
        预期个人账户年缴费额。 N 等于 ``retire_age - current_age``。
    predicted_rates : float or (N, ) array_like of float
        预期个人账户记账利率。N 等于 ``retire_age - current_age``。

    Examples
    --------
    >>> cal_predicted_personal_balance(1000, 58, 60, 1000, 0.5)
    5427.083333333333
    >>> cal_predicted_personal_balance(1000, 58, 60, [1000, 2000], [0.5, 0.6])
    7083.333333333333
    """
    payments = np.asarray(payments)
    predicted_rates = np.asarray(predicted_rates)
    years_to_go = retire_age - current_age
    payments = np.broadcast_to(payments, years_to_go)
    predicted_rates = np.broadcast_to(predicted_rates, years_to_go)
    balance = current_balance
    for payment, rate in zip(payments, predicted_rates):
        balance = balance * (1 + rate) + payment * (1 + rate * 13 / 24)
    return balance


def get_predicted_salary_factor(
        current_salary_factor: float,
        current_accumulated_years: int,
        salaries,
        social_mean_salaries,
        predicted_years: Optional[int] = None) -> float:
    """预测退休时平均工资指数

    Parameters
    ----------
    current_salary_factor : float
        上年度末个人账户余额
    current_accumulated_years : int
        上年度末累计缴费年限
    salaries : float or (N, ) array_like of float
        预期个人账户缴费基数。
    social_mean_salaries : float or (N, ) array_like of float
        预期社会平均工资。
    predicted_years : int, optional
        预期还需缴费年数。

    Examples
    --------
    >>> get_predicted_salary_factor(1, 10, 3000, 1000, 10)
    2.0
    >>> get_predicted_salary_factor(1, 2, [3000, 4000], [1000, 2000])
    1.75
    """
    factors = np.asarray(salaries) / np.asarray(social_mean_salaries)
    years_to_go = factors.size if predicted_years is None else predicted_years
    return ((current_salary_factor * current_accumulated_years
             + np.mean(factors) * years_to_go) /
            (current_accumulated_years + years_to_go))
