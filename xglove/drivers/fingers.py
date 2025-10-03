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
    def __init__(self, device: ads.ADS1115, poly_voltages: Dict[Dict[str, List[Union[float, int]]]],
                 calib_voltages: Dict[Dict[str, List[List]]]):
        self._device_ads = device
        self._calib_voltages = calib_voltages
        self._poly_voltages = poly_voltages

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

        v_current = self.get_finger_voltage(finger_num)
        key = str(finger_num)

        poly_coeffs = self._poly_voltages.get(key)
        calib_points = self._calib_voltages.get(key)

        voltages = [float(v) for v, _ in calib_points]

        v_min = min(voltages)
        v_max = max(voltages)
        if v_max == v_min:
            return 0.0

        v = max(v_min, min(v_current, v_max))

        percent = float(np.polyval(poly_coeffs, v))
        p_at_min = float(np.polyval(poly_coeffs, v_min))
        p_at_max = float(np.polyval(poly_coeffs, v_max))
        low = min(p_at_min, p_at_max)
        high = max(p_at_min, p_at_max)
        percent = max(low, min(percent, high))

        percent = max(0.0, min(100.0, percent))
        return percent
