# -*- coding: utf-8 -*-
# created at: 2023/5/9 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com

from PyQt6.QtCore import *
import socket

# note: you may want to check network configuration of your computer to ensure your local ip
LOCAL_IP = "192.168.137.1"


class VR(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, value):
        super(VR, self).__init__()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind((LOCAL_IP, value))
        self.client_socket.settimeout(1)

        self.running = True

    def run(self):
        while self.running:
            try:
                _bytes = self.client_socket.recv(1024)
                message = _bytes.decode(encoding="utf8")
                self.message_received.emit(message)
            except socket.timeout:
                pass

    def stop(self):
        self.running = False


class MVR(QObject):
    reward_taken = pyqtSignal()

    requirements = {
        "variable": True,
        "runner": True,
        "interface": False
    }
    value_editor = None
    filter_func = int

    gui_param = {
        "menu_name": "VR Interface",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MVR",

        "name": None,
        "value": 4516,    # ports are coupled; 4516 is server (listener), 4517 is client

        "quote": set()
    }

    def __init__(self, value, _name):
        super(MVR, self).__init__()

        self._value = value
        self._name = _name
        self._record = None
        self.runner = None
        self.variable = dict()

        self.vr = VR(value)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vr_socket = (LOCAL_IP, self._value+1)

        self.vr.message_received.connect(self._message_received)

        self._licko = None

    def write_message(self, _bytes):
        self.client_socket.sendto(_bytes.encode(encoding="utf8"), self.vr_socket)

    def start(self, _licko):
        self._licko = _licko
        self.vr.start()

    def stop(self):
        self.vr.stop()

    def set_record(self, _record):
        self._record = _record

    def _message_received(self, message):
        _p = message.split(",")
        if _p[0] == "r1":
            self._licko.give_water()

    def new_reward(self, _x, _y):
        self.write_message(f"R,{_x},{_y}")

    def new_reward_side(self, _side: int):
        self.write_message(f"WR,{_side}")

    def new_square_field_size(self, _size):
        self.write_message(f"SZ,{_size}")

    def cancel_last_reward(self):
        self.write_message(f"NR")
