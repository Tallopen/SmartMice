# -*- coding: utf-8 -*-
# created at: 2023/5/9 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com

from PyQt6.QtCore import *
import socket

# note: you may want to check network configuration of your computer to ensure your local ip
LOCAL_IP = "192.168.137.1"


class UDPClient(QThread):

    def __init__(self, value):
        super(UDPClient, self).__init__()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind((LOCAL_IP, value))
        self.client_socket.settimeout(1)

        self.running = True
        self.data = []
        self._x = None
        self._y = None
        self._data_save_path = ""
        self._runner = None

        self._last_byte = b''

    def configure(self, _x, _y, _data_save_path, _runner):
        self._x = _x
        self._y = _y
        self._data_save_path = _data_save_path
        self._runner = _runner

    def run(self):
        try:
            while self.running:
                _bytes = self.client_socket.recv(1024)
                if _bytes != self._last_byte:
                    data = _bytes.decode(encoding="utf8").split()
                    data = ''.join(data).split(',')
                    self.data.append([self._runner.time()] + data)
                    self._x.set_value(data[0])
                    if len(data) > 1:
                        self._y.set_value(data[1])
                    self._last_byte = _bytes
        except socket.timeout:
            pass

    def stop(self):
        self.running = False

        data_string = ""
        for _data in self.data:
            if len(_data):
                piece_string = str(_data[0])
                if len(_data) > 1:
                    for piece in range(1, len(_data)):
                        piece_string += "," + str(_data[piece])
                data_string += piece_string + "\n"

        with open(self._data_save_path, "w") as f:
            f.write(data_string)


class MUdp:

    requirements = {
        "variable": True,
        "runner": True,
        "interface": False
    }
    value_editor = None
    filter_func = int

    gui_param = {
        "menu_name": "UDP Interface",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MUdp",

        "name": None,
        "value": 4515,

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.runner = None
        self.variable = dict()

        self.port = UDPClient(value)

    def start(self, coordinate_var, _path):
        count = 0
        _variable = []
        for _var_name, _ in coordinate_var:
            _variable.append(self.variable[_var_name])
            count += 1
            if count > 2:
                break

        self.port.configure(_variable[0], _variable[1], _path, self.runner)
        self.port.start()

    def stop(self):
        self.port.stop()

    def set_record(self, _record):
        self._record = _record
