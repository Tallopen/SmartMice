# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com
import os.path

from PyQt6.QtWidgets import QFileDialog


class FileValueEditor:

    def __init__(self, var_name, value: str, ass: dict, *args):
        self.value = value

    def exec(self):
        path, _ = QFileDialog.getOpenFileName(None, "Get existing file path", self.value)
        if os.path.isfile(path) and path != self.value:
            return path, True
        else:
            return None, False


class MFile:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = FileValueEditor
    filter_func = str

    gui_param = {
        "menu_name": "Existing File Path",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MFile",

        "name": None,
        "value": "",

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.variable = dict()

    def get_value(self):
        return self._value

    def set_record(self, _record):
        self._record = _record
