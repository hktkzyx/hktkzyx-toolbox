# 电子工具箱

电子工具箱目前用于计算 LED 的分压电阻或工作电流的大小。
也可以查询标准电阻。使用下面的命令查询帮助：

```bash
hktkzyx-electronics --help
```

## 分压电阻计算

分压电阻计算需要给定供电电压、工作电流并选择 LED 的种类。
例如，红色 LED，供电电压 5 V，工作电流 1 mA：

```bash
hktkzyx-electronics led-divider-resistance -v 5 -c 1 -k r
```

## 工作电流计算

工作电流计算给定供电电压、分压电阻阻值和 LED 的种类。
例如，红色 LED，供电电压 5 V，分压电阻 5 kΩ：

```bash
hktkzyx-electronics led-work-current -v 5 -r 5000 -k r
```

## 查询标准电阻

E 系列标准电阻有 E3、E6、E12、E24、E48、E96 和 E192 七个系列。
默认的系列是 E24。要查询例如 3.1 kΩ 对应的标准电阻：

```bash
hktkzyx-electronics standard-resistance 3100
```

要查询其他系列：

```bash
hktkzyx-electronics standard-resistance -s E96 3100
```

查询标准电阻默认的近似模式是`nearest`，即阻值最接近的。
也可以使用`-m`/`--mode`选项选择`floor`向下舍入模式或`ceil`向上舍入模式。
