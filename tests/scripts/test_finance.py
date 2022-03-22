from click import testing

from hktkzyx_toolbox.scripts import finance


def test_social_fundamental_pension():
    runner = testing.CliRunner()
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
