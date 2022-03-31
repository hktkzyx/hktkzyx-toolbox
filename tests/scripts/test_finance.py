from hktkzyx_toolbox.scripts import finance


def test_social_fundamental_pension(runner):
    results = runner.invoke(finance.social_fundamental_pension,
                            ['-s 1000', '-f 1.5', '-y 40'])
    assert results.exit_code == 0
    assert results.output == '500.00\n'
    results = runner.invoke(finance.social_fundamental_pension,
                            input='1000\n1.5\n40\n')
    assert not results.exception
    assert results.output == ('社会平均工资: 1000\n'
                              '缴费指数: 1.5\n'
                              '缴费年限: 40\n'
                              '500.00\n')


def test_social_personal_pension(runner):
    results = runner.invoke(finance.social_personal_pension, ['-b 139000'])
    assert results.exit_code == 0
    assert results.output == '1000.00\n'
    results = runner.invoke(finance.social_personal_pension, input='139000\n')
    assert not results.exception
    assert results.output == ('个人账户余额: 139000\n'
                              '1000.00\n')
