# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com


import re
from math import *


class MExp:

    requirements = {
        "variable": True,
        "runner": False,
        "interface": False
    }
    value_editor = None
    filter_func = str

    gui_param = {
        "menu_name": "Expression",
        "group": "Basic"
    }
    template_dict = {
        "type": "MExp",

        "name": None,
        "value": "0",

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value.replace(" ", "")
        self._name = _name
        self._record = None
        self.variable = dict()

    def evaluate(self):
        _related_var = set()
        for matched_variables in re.finditer(r"{([a-zA-Z][a-zA-Z0-9]*(?:_[a-zA-Z0-9]+)*)}", self._value):
            _related_var.add(matched_variables.group(1))

        _expression = self._value
        for _related_var_name in _related_var:
            if _related_var_name in self.variable:
                _expression = re.sub(r"{" + _related_var_name + "}", str(self.variable[_related_var_name].get_value()), _expression)
            else:
                raise Exception("illegal expression")

        return eval(_expression)

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def set_record(self, _record):
        self._record = _record
