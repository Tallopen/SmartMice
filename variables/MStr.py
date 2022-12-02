# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com


class MStr:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = None
    filter_func = str

    gui_param = {
        "menu_name": "String",
        "group": "Basic"
    }
    template_dict = {
        "type": "MStr",

        "name": None,
        "value": "",

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.variable = dict()

    def set_value(self, value):
        self._value = str(value)

    def get_value(self):
        return self._value

    def set_record(self, _record):
        self._record = _record
