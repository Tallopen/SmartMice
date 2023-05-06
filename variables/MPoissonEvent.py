# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com
import os
import threading
import time
from pathlib import Path
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import winsound
import numpy as np


class PoissonEventEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(PoissonEventEditor, self).__init__()

        self.value = value

        self.resize(388, 147)
        self.setWindowTitle(u"Poisson Triggered Audio Player")

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_4 = QLabel(self)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setText(str(value["expectation"]))

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.lineEdit_2 = QLineEdit(self)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setText(str(value["lower bound"]))

        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.lineEdit_3 = QLineEdit(self)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setText(str(value["upper bound"]))

        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label.setText("Set interval distribution between two play events, unit is microsecond:")
        self.label_2.setText("Expectation:       ")
        self.label_3.setText("Lower bound:")
        self.label_4.setText("Upper bound:")

    def exec(self):
        _v = super(PoissonEventEditor, self).exec()

        try:
            value = {
                "expectation": float(self.lineEdit.text()),
                "lower bound": float(self.lineEdit_2.text()),
                "upper bound": float(self.lineEdit_3.text()),
            }
            value["expectation"] = self.value["expectation"] if value["expectation"] <= 1e-1 else value["expectation"]
            value["lower bound"] = self.value["lower bound"] if value["lower bound"] <= 1e-1 else value["lower bound"]
            value["upper bound"] = abs(value["lower bound"])+1 if value["upper bound"] <= value["lower bound"]+1e-1 else value["upper bound"]
        except Exception:
            QMessageBox.critical(self, "Error", "Not a valid input!")
            return None, _v

        if _v:
            return value, _v
        return None, _v


class PoissonTrigger:

    def __init__(self, poisson, my_func):

        self.running = True
        self.last_time = time.time()
        self.await_time = 20
        self.poisson = poisson
        self._func = my_func

    def _run_func(self):
        self.last_time = time.time()
        self.generate_await_time()
        while self.running:
            if (time.time() - self.last_time) * 1000 > self.await_time:
                self._func()
                self.last_time = time.time()
                self.generate_await_time()
            else:
                time.sleep(0.02)

    def generate_await_time(self):
        self.await_time = -1
        while not (self.poisson["lower bound"] <= self.await_time <= self.poisson["upper bound"]):
            self.await_time = np.random.normal(self.poisson["expectation"], self.poisson["expectation"]/3)

    def run(self):
        self.running = True
        t = threading.Thread(target=self._run_func)
        t.start()

    def stop(self):
        self.running = False


class MPoissonEvent:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = PoissonEventEditor
    filter_func = dict

    gui_param = {
        "menu_name": "Poisson Trigger",
        "group": "Math"
    }
    template_dict = {
        "type": "MPoissonEvent",

        "name": None,
        "value": {
            "expectation": 10,
            "lower bound": 6,
            "upper bound": 20
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None

        self._player = None

    def run(self, my_func):
        self._player = PoissonTrigger(self._value, my_func)
        self._player.run()

    def stop(self):
        if self._player:
            self._player.stop()

    def set_record(self, _record):
        self._record = _record
