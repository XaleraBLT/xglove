import json
import threading
from ...glove import Glove
import serial
import struct
import socket

__all__ = ["Serial_connector", "Socket_connector"]


class Glove_data:
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.fingers_percent = None
        self.fingers_voltage = None


class Serial_connector(Glove_data):
    def __init__(self, port: str, baudrate: int = 115200):
        super().__init__()

        self._baudrate = baudrate
        self._port = port
        thread = threading.Thread(target=self.__setup, daemon=True)
        thread.start()

    def __setup(self):
        ser = serial.Serial(self._port, 115200)

        while True:
            raw_length = ser.read(4)
            if len(raw_length) < 4:
                break
            if not raw_length:
                break

            msg_length = struct.unpack('!I', raw_length)[0]
            data_bytes = b''
            while len(data_bytes) < msg_length:
                more = ser.read(msg_length - len(data_bytes))
                if not more:
                    break
                data_bytes = (data_bytes + more)[-msg_length:]

            encoded_data = data_bytes.decode()

            data_dict = dict(json.loads(encoded_data))

            self.x, self.y, self.z = tuple(data_dict["angles"].values())
            self.fingers_percent = data_dict["fingers_percent"]
            self.fingers_voltage = data_dict["fingers_voltage"]


class Socket_connector(Glove_data):
    def __init__(self, host: str = "192.168.4.1", port: int = 8000):
        super().__init__()

        self._host = host
        self._port = port
        thread = threading.Thread(target=self.__setup, daemon=True)
        thread.start()

    def __setup(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self._host, self._port))

                while True:
                    try:
                        raw_length = s.recv(4)
                    except ConnectionResetError:
                        break
                    if len(raw_length) < 4:
                        break
                    if not raw_length:
                        break

                    msg_length = struct.unpack('!I', raw_length)[0]
                    data_bytes = b''
                    while len(data_bytes) < msg_length:
                        more = s.recv(msg_length - len(data_bytes))
                        if not more:
                            break
                        data_bytes = (data_bytes + more)[-msg_length:]

                    encoded_data = data_bytes.decode()

                    data_dict = dict(json.loads(encoded_data))

                    self.x, self.y, self.z = tuple(data_dict["angles"].values())
                    self.fingers_percent = data_dict["fingers_percent"]
                    self.fingers_voltage = data_dict["fingers_voltage"]
                    self.fingers_raw = data_dict["fingers_raw"]
