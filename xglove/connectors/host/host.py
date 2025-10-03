import json
import struct
import threading
import time
import socket
import serial
from ...glove import Glove
from PIL import ImageFont

__all__ = ["Serial_connector", "Socket_connector"]


class Glove_data(object):
    def __init__(self, glove: Glove):
        self._glove = glove
        self._font = ImageFont.load_default()
        self.x = None
        self.y = None
        self.z = None
        self.fingers_percent = None
        self.fingers_voltage = None
        self.text = ""

        thread = threading.Thread(target=self.__main_loop, daemon=True)
        thread.start()

    def __main_loop(self):
        while True:
            self.x, self.y, self.z = self._glove.get_angle("x", "y", "z")
            self.fingers_percent = dict(zip(range(4),
                                            [self._glove.get_finger_percent(finger_num) for finger_num in range(4)]))
            self.fingers_voltage = dict(zip(range(4),
                                            [self._glove.get_finger_voltage(finger_num) for finger_num in range(4)]))
            self.fingers_raw = dict(zip(range(4),
                                            [self._glove.get_finger_raw(finger_num) for finger_num in range(4)]))

            self._glove.render_data(angles=(self.x, self.y, self.z), fingers=list(self.fingers_percent.values()),
                                    text_attributes=(self.text, self._font))
            time.sleep(0.02)

    def _pack_data(self) -> bytes:
        data_dict = {
            "angles": {"roll": self.x, "pitch": self.y, "yaw": self.z},
            "fingers_percent": self.fingers_percent,
            "fingers_voltage": self.fingers_voltage,
            "fingers_raw": self.fingers_raw
        }

        data_bytes = json.dumps(data_dict).encode()
        length = struct.pack('!I', len(data_bytes))

        return length + data_bytes


class Serial_connector(Glove_data):
    def __init__(self, glove: Glove, port: str = '/dev/ttyGS0', baudrate: int = 115200):
        super().__init__(glove)

        self._baudrate = baudrate
        self._port = port
        thread = threading.Thread(target=self.__setup, daemon=True)
        thread.start()

    def __setup(self):
        while True:
            try:
                serial_port = serial.Serial(self._port, self._baudrate)
                self.text = "Connected"
                while True:
                    data = self._pack_data()
                    serial_port.write(data)
                    time.sleep(0.05)
            except KeyboardInterrupt:
                self.text = "Waiting connection"


class Socket_connector(Glove_data):
    def __init__(self, glove: Glove, host: str = "192.168.4.1", port: int = 8000):
        super().__init__(glove)

        self._host = host
        self._port = port
        thread = threading.Thread(target=self.__setup, daemon=True)
        thread.start()

    def __setup(self):
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self._host, self._port))
                    s.listen()
                    self.text = "Waiting connection"
                    conn, addr = s.accept()
                    with conn:
                        self.text = f"Connected"
                        while True:
                            data = self._pack_data()
                            try:
                                conn.sendall(data)
                            except BrokenPipeError:
                                break
                            time.sleep(0.05)

            except ConnectionResetError:
                continue
