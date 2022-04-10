# 金融工具箱

金融工具箱目前可以测算城镇居民养老保险的待遇。

查看命令帮助

```bash
hktkzyx-finance --help
```

## 基础养老金

基础养老金是根据社会平均工资、缴费指数和缴费年限决定的。
可以直接使用下面的命令，根据提示进行计算。

```bash
hktkzyx-finance social-fundamental-pension
```

也可以直接通过命令计算。例如，社会平均工资是 1000 元， 缴费指数是 1.2， 缴费年限是 20 年。
应该运行下面的命令。

```bash
hktkzyx-finance social-fundamental-pension -s 1000 -f 1.2 -y 20
```

## 个人养老金

个人养老金是根据个人账户的余额和退休年龄决定的。
不同的退休年龄计发月份不同。
使用下面的命令，根据提示计算个人养老金。

```bash
hktkzyx-finance social-personal-pension
```

注意默认的退休年龄是 60 岁。
如果要更改退休年龄，添加`-a`或者`--retire-age`选项。
例如，65 岁退休

```bash
hktkzyx-finance social-personal-pension -a 65
```

直接传递个人账户余额使用`-b`或者`--balance`选项。

## 养老金待遇测算

养老金待遇测算需要测算未来的基础养老金和个人养老金。
基础养老金测算需要预测未来的社平工资和缴费指数。
因此，需要知道社平工资的涨幅、缴费基数的涨幅。
个人养老金测算需要预测未来的缴费基数变化和账户利率。
使用下列命令查看说明：

```bash
hktkzyx-finance social-pension-predict --help
```

如果某人上年末 25 岁，预计 65 岁退休。
上年末缴费月缴费基数是 1,000 元，平均缴费指数是 1.2，已经缴费了 3 年。
上年末个人账户余额是 10,000 元。
运行下面的命令：

```bash
hktkzyx-finance social-pension-predict -a 25 -t 65 --salary 1000 -f 1.2 -y 3 -b 10000
```

并根据提示，补全其他参数。
注意，**缴费基数涨幅**， **个人账户记账利率**和**社会平均工资涨幅**均是指年度涨幅。
如果年度涨幅是 1% 就输入 0.01。
