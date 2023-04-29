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


class PoissonAudioEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(PoissonAudioEditor, self).__init__()

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
        _v = super(PoissonAudioEditor, self).exec()

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


class PoissonPlayer:

    def __init__(self, poisson, play_list_directory, mexp_var):

        self.mexp_var = mexp_var     # activated when it's true
        self.playlist = []

        for filename in Path(play_list_directory).iterdir():
            if filename.suffix == ".wav":
                self.playlist.append(os.path.join(play_list_directory, filename.name))

        self.running = True
        self.last_time = time.time()
        self.await_time = 20
        self.poisson = poisson

    def _play_func(self):
        self.last_time = time.time()
        self.generate_await_time()
        while self.running:
            if self.mexp_var.evaluate():
                if (time.time() - self.last_time) * 1000 > self.await_time:
                    sound_id = np.random.randint(len(self.playlist))
                    winsound.PlaySound(self.playlist[sound_id], winsound.SND_FILENAME)
                    self.last_time = time.time()
                    self.generate_await_time()
            else:
                self.last_time = time.time()
            time.sleep(0.02)

    def generate_await_time(self):
        self.await_time = -1
        while not (self.poisson["lower bound"] <= self.await_time <= self.poisson["upper bound"]):
            self.await_time = np.random.poisson(self.poisson["expectation"])

    def run(self):
        self.running = True
        t = threading.Thread(target=self._play_func)
        t.start()

    def stop(self):
        self.running = False


class MPoissonAudio:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = PoissonAudioEditor
    filter_func = dict

    gui_param = {
        "menu_name": "Poisson Triggered Audio Player",
        "group": "Math"
    }
    template_dict = {
        "type": "MPoissonAudio",

        "name": None,
        "value": {
            "expectation": 50,
            "lower bound": 10,
            "upper bound": 200
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None

        self._player = None

    def run(self, play_list_directory, mexp_var):
        self._player = PoissonPlayer(self._value, play_list_directory, mexp_var)
        self._player.run()

    def stop(self):
        if self._player:
            self._player.stop()

    def set_record(self, _record):
        self._record = _record
