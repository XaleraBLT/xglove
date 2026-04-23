from __future__ import annotations

from typing import Dict, List, Union
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ads
import numpy as np


class Fingers(object):
    def __init__(self, device: ads.ADS1115, calib_raw: Dict[Dict[str, List[List]]]):
        self._device_ads = device
        self._calib_raw = calib_raw
        percentages = [0, 25, 50, 75, 100]

        self._polynomials = {}
        for finger_num, values in self._calib_raw.items():
            sorted_pairs = sorted(zip(values, percentages), reverse=True)
            x_sorted, y_sorted = zip(*sorted_pairs)
            self._polynomials[str(finger_num)] = np.poly1d(np.polyfit(x_sorted, y_sorted, 2))

    def get_finger_voltage(self, finger_num: int) -> float:
        if finger_num < 0 or finger_num > 3:
            raise ValueError("Finger number must be between 0 and 3 inclusive")

        channel = getattr(ads, f'P{finger_num}')

        try:
            chan = AnalogIn(self._device_ads, channel)
            return chan.voltage
        except OSError:
            return 0

    def get_finger_raw(self, finger_num: int) -> int:
        if finger_num < 0 or finger_num > 3:
            raise ValueError("Finger number must be between 0 and 3 inclusive")

        channel = getattr(ads, f'P{finger_num}')

        try:
            chan = AnalogIn(self._device_ads, channel)
            return chan.value & 0xFFFF
        except OSError:
            return -32768

    def get_finger_percent(self, finger_num: int) -> float:
        if finger_num < 0 or finger_num > 3:
            raise ValueError("Finger number must be between 0 and 3 inclusive")

        raw_value = self.get_finger_raw(finger_num)
        key = str(finger_num)

        x_vals = self._calib_raw[key]

        if raw_value >= max(x_vals):
            return 0.0
        if raw_value <= min(x_vals):
            return 100.0
        return max(0.0, min(100.0, self._polynomials[key](raw_value)))
