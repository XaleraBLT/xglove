import threading
from typing import Dict
from pathlib import Path

__all__ = ["Glove"]

try:
    from .drivers.IMU import IMU
    from .drivers.interface import Interface
    from .drivers.fingers import Fingers
    from adafruit_ads1x15 import ads1115
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from PIL import ImageFont
    import smbus2
    import board
    import busio
    import json
    import time


    class Glove(Fingers, IMU, Interface):

        def __init__(self, calib_raw: Dict = None):
            i2c_adc = busio.I2C(board.SCL, board.SDA)
            ads_device = ads1115.ADS1115(i2c_adc)
            if calib_raw is None:
                calib_raw_path = Path(__file__).parent / "data" / "calib_raw.json"
                calib_raw = json.loads(open(calib_raw_path, "r").read())
            Fingers.__init__(self, device=ads_device, calib_raw=calib_raw)

            bus_IMU = smbus2.SMBus(3)
            IMU.__init__(self, bus=bus_IMU)

            serial_interface = i2c(port=2, address=0x3C)
            device_interface = ssd1306(serial_interface, width=128, height=64)
            font = ImageFont.load_default(10)
            Interface.__init__(self, device=device_interface, font=font)

            thread = threading.Thread(target=self.__load_IMU, daemon=True)
            thread.start()

        def __load_IMU(self):
            while True:
                self._update_data()
                time.sleep(0.005)

except ImportError:
    class Glove(object):
        def __init__(self, *args, **kwargs):
            raise AttributeError("Аппаратная часть XGlove не поддерживается на данном устройстве. Используется "
                                 "заглушка.")

        def __str__(self):
            return "Аппаратная часть XGlove не поддерживается на данном устройстве. Используется заглушка."
