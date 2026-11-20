# Voltage Measurement Project

用 ESP32 的 ADC 测量电压，并用 Python 实时画出电压曲线。

## 文件

| 文件 | 说明 |
|---|---|
| `esp32_voltage_monitor/esp32_voltage_monitor.ino` | Arduino IDE 程序，每 0.5 秒通过串口输出一行 CSV：`time_ms,raw_adc,adc_mv,voltage_v` |
| `plot_voltage.py` | Python 画图脚本：实时串口画图并保存 CSV，或读取已有 CSV 画图 |
| `requirements.txt` | Python 依赖 |

## 接线

经典 ESP32 没有能直接读取 VDD 的内部 ADC 通道，所以用分压电阻把要测的电压（3V3 或电池）接到 ADC1 引脚：

```
3V3 / VBAT ── R1 (100k) ──┬── R2 (100k) ── GND
                          │
                       GPIO34
```

R1 = R2 时 `DIVIDER_RATIO = 2.0`。如果被测电压低于约 3.1 V，也可以直接接到 GPIO34，并把 `DIVIDER_RATIO` 改为 `1.0`。
用万用表测一次实际电压，再调整 `CAL_FACTOR` 可提高精度。

## 使用

1. Arduino IDE 中选择 ESP32 开发板，上传 `esp32_voltage_monitor.ino`。
2. **关闭 Arduino 串口监视器**（否则 Python 无法打开串口）。
3. 安装依赖并运行：

```bash
pip install -r requirements.txt
python plot_voltage.py --port /dev/cu.usbserial-0001   # Windows 用 COM3 之类
```

实时数据会保存为 `voltage_YYYYMMDD_HHMMSS.csv`。之后可以重新画图：

```bash
python plot_voltage.py --file voltage_20261120_120000.csv --save voltage.png
```
