from __future__ import annotations

from typing import Dict, List, Union
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ads
import numpy as np


class Fingers(object):
    """
        Класс для работы с тензорезисторами, подключёнными к АЦП ADS1115, с поддержкой калибровки
        и преобразования напряжений в процент изгиба.

        Аргументы конструктора:
            device (ads.ADS1115): Экземпляр ADS1115 для чтения напряжений.
            poly_voltages (Dict[str, List[Union[float, int]]]):
                Словарь коэффициентов полиномиальной аппроксимации, где ключ — номер пальца от 0 до 3-х (строка),
                а значение — список коэффициентов, используемых в np.polyval для перевода напряжения в проценты.
            calib_voltages (Dict[str, List[List]]):
                Словарь с калибровочными точками для каждого пальца, где ключ — номер пальца от 0 до 3-х (строка),
                а значение — список точек [напряжение, процент], использованных при калибровке.
    """
    def __init__(self, device: ads.ADS1115, calib_raw: Dict[Dict[str, List[List]]]):
        self._device_ads = device
        self._calib_raw = calib_raw
        percentages = [0, 25, 50, 75, 100]

        self._polynomials = {}
        for finger_num, values in self._calib_raw.items():
            sorted_pairs = sorted(zip(values, percentages), reverse=True)
            x_sorted, y_sorted = zip(*sorted_pairs)
            self._polynomials[finger_num] = np.poly1d(np.polyfit(x_sorted, y_sorted, 2))

    def get_finger_voltage(self, finger_num: int) -> float:
        """
            Возвращает текущее напряжение (в вольтах) с датчика, привязанного к указанному пальцу.
            Параметр finger_num должен быть от 0 до 3 включительно.
        """

        if finger_num < 0 or finger_num > 3:
            raise ValueError("Finger number must be between 0 and 3 inclusive")

        channel = getattr(ads, f'P{finger_num}')
        chan = AnalogIn(self._device_ads, channel)
        return chan.voltage

    def get_finger_raw(self, finger_num: int) -> int:
        """
            Возвращает текущее значение (-32768 … +32767) с датчика, привязанного к указанному пальцу.
            Параметр finger_num должен быть от 0 до 3 включительно.
        """
        if finger_num < 0 or finger_num > 3:
            raise ValueError("Finger number must be between 0 and 3 inclusive")

        channel = getattr(ads, f'P{finger_num}')
        chan = AnalogIn(self._device_ads, channel)

        return chan.value & 0xFFFF

    def get_finger_percent(self, finger_num: int) -> float:
        """
            Преобразует текущее напряжение в процент изгиба пальца, используя полиномиальную аппроксимацию
            и ограничения, полученные при калибровке.
            Гарантирует, что результат всегда находится в диапазоне от 0.0 до 100.0 %.
        """
        if finger_num < 0 or finger_num > 3:
            raise ValueError("Finger number must be between 0 and 3 inclusive")

        raw_value = self.get_finger_raw(finger_num)
        key = str(finger_num)

        x_vals = self._calib_raw[key]

        if raw_value >= max(x_vals):
            return 0.0
        if raw_value <= min(x_vals):
            return 100.0
        return max(0.0, min(100.0, self._polynomials[finger_num](raw_value)))

        return percent
