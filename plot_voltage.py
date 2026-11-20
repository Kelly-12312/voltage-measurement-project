#!/usr/bin/env python3
"""
Plot ESP32 voltage readings.

Two modes:
  Live   : read the ESP32 over serial, plot in real time and log to CSV
           python plot_voltage.py --port /dev/cu.usbserial-0001
  Offline: plot a CSV you recorded earlier
           python plot_voltage.py --file voltage_log.csv

The ESP32 sketch prints lines like:  time_ms,raw_adc,adc_mv,voltage_v
"""

import argparse
import csv
import sys
from collections import deque
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def parse_line(line):
    """Return (t_seconds, voltage) or None for headers/comments/garbage."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("time_ms"):
        return None
    parts = line.split(",")
    if len(parts) < 4:
        return None
    try:
        return int(float(parts[0])) / 1000.0, float(parts[3])
    except ValueError:
        return None


def style_axes(ax, title):
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True, alpha=0.3)


def plot_file(path, save=None):
    times, volts = [], []
    with open(path, newline="") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                times.append(parsed[0])
                volts.append(parsed[1])

    if not volts:
        sys.exit(f"No voltage data found in {path}")

    t0 = times[0]
    times = [t - t0 for t in times]
    avg = sum(volts) / len(volts)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(times, volts, lw=1.5, label="Voltage")
    ax.axhline(avg, ls="--", lw=1, color="gray", label=f"Mean {avg:.3f} V")
    style_axes(ax, f"ESP32 voltage  (min {min(volts):.3f} V, max {max(volts):.3f} V, n={len(volts)})")
    ax.legend()
    fig.tight_layout()

    if save:
        fig.savefig(save, dpi=150)
        print(f"Saved plot to {save}")
    plt.show()


def plot_live(port, baud, window, logfile):
    try:
        import serial  # pyserial
    except ImportError:
        sys.exit("pyserial is required for live mode: pip install pyserial")

    ser = serial.Serial(port, baud, timeout=0.1)
    ser.reset_input_buffer()

    log = open(logfile, "w", newline="")
    writer = csv.writer(log)
    writer.writerow(["time_ms", "voltage_v"])
    print(f"Logging to {logfile}  (close the plot window to stop)")

    times = deque(maxlen=window)
    volts = deque(maxlen=window)
    t0 = [None]

    fig, ax = plt.subplots(figsize=(10, 5))
    (line,) = ax.plot([], [], lw=1.5)
    style_axes(ax, f"ESP32 voltage - live ({port})")
    text = ax.text(0.01, 0.97, "", transform=ax.transAxes, va="top", family="monospace")

    def update(_):
        while ser.in_waiting:
            raw = ser.readline().decode("utf-8", errors="ignore")
            parsed = parse_line(raw)
            if not parsed:
                continue
            t, v = parsed
            if t0[0] is None:
                t0[0] = t
            times.append(t - t0[0])
            volts.append(v)
            writer.writerow([int(t * 1000), v])
        log.flush()

        if volts:
            line.set_data(times, volts)
            ax.set_xlim(times[0], max(times[-1], times[0] + 1))
            lo, hi = min(volts), max(volts)
            pad = max((hi - lo) * 0.2, 0.05)
            ax.set_ylim(lo - pad, hi + pad)
            text.set_text(f"now {volts[-1]:.3f} V   min {lo:.3f}   max {hi:.3f}")
        return line, text

    anim = FuncAnimation(fig, update, interval=200, cache_frame_data=False)  # noqa: F841
    try:
        plt.show()
    finally:
        ser.close()
        log.close()
        print(f"Saved data to {logfile}")


def main():
    p = argparse.ArgumentParser(description="Plot ESP32 voltage readings")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--port", help="Serial port, e.g. COM3 or /dev/cu.usbserial-0001")
    src.add_argument("--file", help="CSV file to plot")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--window", type=int, default=600, help="points shown in live mode")
    p.add_argument("--log", default=None, help="CSV log file for live mode")
    p.add_argument("--save", default=None, help="save the offline plot as an image")
    args = p.parse_args()

    if args.file:
        plot_file(args.file, args.save)
    else:
        logfile = args.log or datetime.now().strftime("voltage_%Y%m%d_%H%M%S.csv")
        plot_live(args.port, args.baud, args.window, logfile)


if __name__ == "__main__":
    main()
