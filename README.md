# ESP32 电压测量项目

用 ESP32 的模数转换器（ADC）测量电压，并用 Python 实时画出电压曲线。

## 文件说明

| 文件 | 说明 |
|---|---|
| `esp32_voltage_monitor/esp32_voltage_monitor.ino` | Arduino 程序：每 0.5 秒通过串口输出一行 CSV 数据，四列依次是：时间（毫秒）、ADC 原始值、ADC 毫伏、电压（伏） |
| `plot_voltage.py` | Python 画图脚本：从串口实时画图并保存 CSV，或读取已保存的 CSV 画图 |
| `requirements.txt` | Python 需要安装的库 |

## 接线

普通 ESP32 没有可以直接读取自身供电电压的内部通道，所以要用两个电阻分压，把被测电压（3.3V 或电池）接到 ADC1 的引脚上：

```
3.3V / 电池 ── R1 (100k) ──┬── R2 (100k) ── GND
                           │
                        GPIO34
```

- 两个电阻相等时，程序里的 `DIVIDER_RATIO`（分压比）设为 `2.0`。
- 如果被测电压低于约 3.1V，也可以不用电阻直接接到 GPIO34，把 `DIVIDER_RATIO` 改成 `1.0`。
- 用万用表测一次实际电压，再调整 `CAL_FACTOR`（校准系数），可以让读数更准。

## 使用方法

第一步：在 Arduino IDE 里选择 ESP32 开发板，上传 `esp32_voltage_monitor.ino`。

第二步：**关闭 Arduino 的串口监视器**，否则 Python 打不开串口。

第三步：安装依赖并运行（把串口名换成你自己的，Windows 一般是 `COM3` 这样的名字）：

```bash
pip install -r requirements.txt
python plot_voltage.py --port /dev/cu.usbserial-0001
```

关闭画图窗口后，数据会保存为 `voltage_年月日_时分秒.csv`。以后可以用这个文件重新画图，并保存成图片：

```bash
python plot_voltage.py --file voltage_20261120_120000.csv --save voltage.png
```
