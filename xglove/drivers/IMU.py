from __future__ import annotations
from typing import List
import time
import smbus2
import math

class IMU(object):
    def __init__(self,
                 bus: smbus2.SMBus,
                 mpu_address: int = 0x68,
                 accel_xout_high_reg: int = 0x3B,
                 gyro_xout_high_reg: int = 0x43,
                 power_mgmt_1_reg: int = 0x6B,
                 accel_config_reg: int = 0x1C
                 ):
        self._bus = bus
        self._mpu_address = mpu_address
        self._accel_xout_high_reg = accel_xout_high_reg
        self._gyro_xout_high_reg = gyro_xout_high_reg
        self._power_mgmt_1_reg = power_mgmt_1_reg
        self._accel_config_reg = accel_config_reg

        for name, val in (("mpu_address", self._mpu_address),
                          ("accel_xout_high_reg", self._accel_xout_high_reg),
                          ("gyro_xout_high_reg", self._gyro_xout_high_reg),
                          ("power_mgmt_1_reg", self._power_mgmt_1_reg),
                          ("accel_config_reg", self._accel_config_reg)):
            if not (0x00 <= val <= 0xFF):
                raise ValueError(f"{name} must be a byte value between 0x00 and 0xFF, got {val}")


        self._last_time = time.time()
        self._bus.write_byte_data(self._mpu_address, self._power_mgmt_1_reg, 0)
        self._bus.write_byte_data(self._mpu_address, self._accel_config_reg, 0)

        self._ax, self._ay, self._az = self.__get_accel_rates()
        self._gx, self._gy, self._gz = self.__get_gyro_rates()
        self._roll = math.degrees(math.atan2(self._ay, self._az))
        self._pitch = math.degrees(math.atan2(-self._ax, self._az))
        self._yaw = 0

    def get_angle(self, *angles) -> List[float]:
        angles_map = {
            "roll": self._roll, "x": self._roll % 360,
            "pitch": self._pitch, "y": self._pitch % 360,
            "yaw": self._yaw, "z": self._yaw % 360
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

    def _update_data(self):
        self._ax, self._ay, self._az = self.__get_accel_rates()
        self._gx, self._gy, self._gz = self.__get_gyro_rates()

        current_time = time.time()
        dt = current_time - self._last_time
        self._last_time = current_time

        accel_roll = math.degrees(math.atan2(self._ay, self._az))
        accel_pitch = math.degrees(math.atan2(-self._ax, self._az))

        self._roll = self.__complementary_filter(self._roll, accel_roll, self._gx, dt, 0.95)
        self._pitch = self.__complementary_filter(self._pitch, accel_pitch, self._gy, dt, 0.95)

        if abs(self._gz) > 3:
            self._yaw += self._gz * dt
            self._yaw = (self._yaw + 180) % 360 - 180


    def __read_word(self, reg):
        high = self._bus.read_byte_data(self._mpu_address, reg)
        low = self._bus.read_byte_data(self._mpu_address, reg + 1)

        value = (high << 8) + low
        if value >= 0x8000:
            value -= 0x10000

        return value

    def __get_accel_rates(self):
        reg = self._accel_xout_high_reg

        ax = self.__read_word(reg) / 16384.0
        ay = self.__read_word(reg + 2) / 16384.0
        az = self.__read_word(reg + 4) / 16384.0

        return ax, ay, az

    def __get_gyro_rates(self):
        reg = self._gyro_xout_high_reg
        gx = self.__read_word(reg) / 131.0
        gy = self.__read_word(reg + 2) / 131.0
        gz = self.__read_word(reg + 4) / 131.0

        return gx, gy, gz

    @staticmethod
    def __complementary_filter(prev_angle, accel_angle, gyro_rate, dt, k):
        angle = k * (prev_angle + gyro_rate * dt) + (1 - k) * accel_angle
        return (angle + 180) % 360 - 180
