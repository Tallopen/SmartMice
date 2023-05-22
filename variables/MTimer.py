# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com


import time


class MTimer:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = None
    filter_func = float

    gui_param = {
        "menu_name": "Timer",
        "group": "Basic"
    }
    template_dict = {
        "type": "MTimer",

        "name": None,
        "value": 0,

        "quote": set()
    }

    def __init__(self, value, _name):

        if type(value) in [float, int]:
            self._value = float(value)
        else:
            raise Exception(f"{value}: not a number")
        self._name = _name
        self._record = None
        self.variable = dict()

        self._start_time = 0
        self._running = False

    def set_value(self, value):
        self._value = value

    def start(self):
        self._running = True
        self._start_time = time.time()

    def get_value(self):
        if self._running:
            return time.time() - self._start_time
        return self._value

    def stop(self):
        self._value = time.time() - self._start_time
        self._running = False

    def set_record(self, _record):
        self._record = _record
