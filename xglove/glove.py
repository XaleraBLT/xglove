import threading
from typing import Dict
from pathlib import Path

__all__ = ["Glove"]

try:
    from .drivers.accelerometer import Accelerometer
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


    class Glove(Fingers, Accelerometer, Interface):
        """
            Класс Glove объединяет функционал работы с тензорезисторами, акселерометром и OLED-дисплеем
            в едином устройстве — перчатке-контроллере. Предназначен для считывания данных о жестах, углах
            ориентации руки и вывода информации на экран.

            Наследует:
                Fingers — обработка данных с тензорезисторов (измерение сгиба пальцев).
                Accelerometer — получение углов наклона (pitch, roll, yaw) с датчика GY-86/MPU.
                Interface — отображение данных на OLED-дисплее.

            Параметры: calib_voltages (Dict, optional) — словарь с калибровочными напряжениями для каждого пальца.
            poly_voltages (Dict, optional) — словарь с полиномиальными коэффициентами для пересчёта напряжений в
            проценты.

            Потоки:
                При инициализации создаётся фоновый поток для постоянного обновления данных акселерометра.

            Использование:
                glove = Glove()
                angles = glove.get_angle("pitch", "roll", "yaw")
                fingers = [glove.get_finger_percent(p) for p in range(4)]
                glove.render_data(angles, fingers, text_attributes=("Hello world!", font))
            """

        def __init__(self, calib_voltages: Dict = None, poly_voltages: Dict = None):
            i2c_adc = busio.I2C(board.SCL, board.SDA)
            ads_device = ads1115.ADS1115(i2c_adc)
            if calib_voltages is None:
                calib_voltages_path = Path(__file__).parent / "data" / "calib_voltages.json"
                calib_voltages = json.loads(open(calib_voltages_path, "r").read())
            if poly_voltages is None:
                poly_voltages_path = Path(__file__).parent / "data" / "poly_voltages.json"
                poly_voltages = json.loads(open(poly_voltages_path, "r").read())
            Fingers.__init__(self, device=ads_device, poly_voltages=poly_voltages, calib_voltages=calib_voltages)

            bus_accelerometer = smbus2.SMBus(3)
            Accelerometer.__init__(self, bus=bus_accelerometer)

            serial_interface = i2c(port=2, address=0x3C)
            device_interface = ssd1306(serial_interface, width=128, height=64)
            font_path = Path(__file__).parent / "fonts" / "font.ttf"
            font = ImageFont.truetype(font_path, 10)
            Interface.__init__(self, device=device_interface, font=font)

            thread = threading.Thread(target=self.__load_accelerometer, daemon=True)
            thread.start()

        def __load_accelerometer(self):
            while True:
                self._get_angles()
                time.sleep(0.01)

except ImportError:
    class Glove(object):
        def __init__(self, *args, **kwargs):
            raise AttributeError("Аппаратная часть XGlove не поддерживается на данном устройстве. Используется "
                                 "заглушка.")

        def __str__(self):
            return "Аппаратная часть XGlove не поддерживается на данном устройстве. Используется заглушка."
