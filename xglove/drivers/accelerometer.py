from __future__ import annotations
from typing import List

import time
import smbus2
import math


class Accelerometer(object):
    """
    Класс для работы с акселерометром и гироскопом через I2C (smbus2).

    __init__(bus, mpu_address=None, accel_xout_high_reg=None, gyro_xout_high_reg=None, power_mgmt_1_reg=None)
        Инициализация акселерометра.
        Параметры:
            bus (smbus2.SMBus): объект шины I2C.
            mpu_address (int, optional): I2C-адрес устройства (по умолчанию 0x68).
            accel_xout_high_reg (int, optional): регистр акселерометра X high byte (по умолчанию 0x3B).
            gyro_xout_high_reg (int, optional): регистр гироскопа X high byte (по умолчанию 0x43).
            power_mgmt_1_reg (int, optional): регистр питания (по умолчанию 0x6B).

        Производит включение датчика и настройку начальных регистров.

    """
    def __init__(self,
                 bus: smbus2.SMBus,
                 mpu_address: int = None,
                 accel_xout_high_reg: int = None,
                 gyro_xout_high_reg: int = None,
                 power_mgmt_1_reg: int = None):
        self._bus = bus
        self._mpu_address = mpu_address if mpu_address is not None else 0x68
        self._accel_xout_high_reg = accel_xout_high_reg if accel_xout_high_reg is not None else 0x3B
        self._gyro_xout_high_reg = gyro_xout_high_reg if gyro_xout_high_reg is not None else 0x43
        self._power_mgmt_1_reg = power_mgmt_1_reg if power_mgmt_1_reg is not None else 0x6B

        for name, val in (("mpu_address", self._mpu_address),
                          ("accel_xout_high_reg", self._accel_xout_high_reg),
                          ("gyro_xout_high_reg", self._gyro_xout_high_reg),
                          ("power_mgmt_1_reg", self._power_mgmt_1_reg)):
            if not (0x00 <= val <= 0xFF):
                raise ValueError(f"{name} must be a byte value between 0x00 and 0xFF, got {val}")

        self._pitch = 0
        self._roll = 0
        self._yaw_threshold = 0.7
        self._yaw = 0
        self._last_time = time.time()
        self._bus.write_byte_data(self._mpu_address, self._power_mgmt_1_reg, 0)

    def get_angle(self, *angles) -> List[float]:

        """
        Получение текущих углов акселерометра и гироскопа.
        Параметры:
            angles (str): список имён углов, которые нужно получить. Допустимые значения:
                "pitch" или "x" – наклон вперёд/назад,
                "roll" или "y" – наклон влево/вправо,
                "yaw" или "z" – вращение вокруг вертикальной оси.
        Возвращает:
            Список float значений углов в градусах в том же порядке, что переданы параметры.
        Пример:
            accel.get_angle("pitch", "roll") -> [45.0, 10.5]
        """

        angles_map = {
            "pitch": self._pitch, "x": self._roll,
            "roll": self._roll, "y": self._pitch,
            "yaw": self._yaw, "z": self._yaw
        }

        results = []
        for a in angles:
            if not isinstance(a, str):
                raise TypeError(f"Angle name must be str, got {type(a).__name__}")
            key = a.lower()
            if key not in angles_map:
                raise ValueError(f"Unknown angle name: {a}")
            results.append(float(angles_map.get(key)))

        return results

    def _get_angles(self):

        """
        Обновляет внутренние значения углов (_pitch, _roll, _yaw) на основе показаний акселерометра и гироскопа.
        Этот метод вызывается для внутреннего пересчёта углов. Обычно не вызывается напрямую пользователем.
        """

        accel_pitch, accel_roll = self.__get_accel_angles()
        gx, gy, gz = self.__get_gyro_rates()

        current_time = time.time()
        dt = current_time - self._last_time
        self._last_time = current_time

        self._pitch = self.__complementary_filter(self._pitch, accel_pitch, gx, dt)
        self._roll = self.__complementary_filter(self._roll, accel_roll, gy, dt)

        self._yaw = (self._yaw + gz * dt) % 360

    def __read_word(self, reg):
        high = self._bus.read_byte_data(self._mpu_address, reg)
        low = self._bus.read_byte_data(self._mpu_address, reg + 1)

        value = (high << 8) + low
        if value >= 0x8000:
            value -= 0x10000

        return value

    def __get_accel_angles(self):
        reg = self._accel_xout_high_reg

        ax = self.__read_word(reg) / 16384.0
        ay = self.__read_word(reg + 2) / 16384.0
        az = self.__read_word(reg + 4) / 16384.0

        pitch = math.degrees(math.atan2(-ax, math.sqrt(ay ** 2 + az ** 2)))

        roll = math.degrees(math.atan2(ay, az))

        return pitch, roll

    def __get_gyro_rates(self):
        reg = self._gyro_xout_high_reg
        gx = self.__read_word(reg) / 131.0
        gy = self.__read_word(reg + 2) / 131.0
        gz = self.__read_word(reg + 4) / 131.0
        return gx, gy, gz

    @staticmethod
    def __complementary_filter(prev_angle, accel_angle, gyro_rate, dt, alpha=0.98):
        return alpha * (prev_angle + gyro_rate * dt) + (1 - alpha) * accel_angle
