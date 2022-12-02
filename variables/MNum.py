# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com


class MNum:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = None
    filter_func = float

    gui_param = {
        "menu_name": "Real Number",
        "group": "Basic"
    }
    template_dict = {
        "type": "MNum",

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

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def set_record(self, _record):
        self._record = _record
