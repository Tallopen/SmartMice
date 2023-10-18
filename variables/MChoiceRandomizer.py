# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com
import os
import random
import threading
import time
from pathlib import Path
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import winsound
import numpy as np


class ChoiceRandomizerEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(ChoiceRandomizerEditor, self).__init__()

        # below creates UI:
        self.resize(460, 420)
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.label = QLabel(self)

        self.horizontalLayout.addWidget(self.label)

        self.ItemNumberSpin = QSpinBox(self)
        self.ItemNumberSpin.setMinimum(1)
        self.ItemNumberSpin.setMaximum(100)

        self.horizontalLayout.addWidget(self.ItemNumberSpin)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.label_2 = QLabel(self)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.ProbabilisticRadio = QRadioButton(self)

        self.horizontalLayout_2.addWidget(self.ProbabilisticRadio)

        self.DeterministicRadio = QRadioButton(self)
        self.DeterministicRadio.setChecked(True)

        self.horizontalLayout_2.addWidget(self.DeterministicRadio)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.label_3 = QLabel(self)

        self.horizontalLayout_3.addWidget(self.label_3)

        self.SeriesLength = QLineEdit(self)

        self.horizontalLayout_3.addWidget(self.SeriesLength)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.tableView = QTableWidget(self)
        self.tableView.setColumnCount(2)
        self.tableView.setHorizontalHeaderLabels(["Number", "Probability"])

        self.verticalLayout.addWidget(self.tableView)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(u"Dialog")
        self.label.setText(u"Item Number:")
        self.label_2.setText(u"Randomizer Type:")
        self.ProbabilisticRadio.setText(u"Probabilistic")
        self.DeterministicRadio.setText(u"Deterministic")
        self.label_3.setText(u"Randomizer Series Length:")

        self.ProbabilisticRadio.clicked.connect(self.probabilisticToggle)
        self.DeterministicRadio.clicked.connect(self.probabilisticToggle)

        self.value = value
        self.SeriesLength.setText(str(self.value["series length"]))
        self.probabilistic = self.value["probabilistic"]
        self.indexNumber = self.value["index number"]
        self.ItemNumberSpin.setValue(self.indexNumber)
        self.ItemNumberSpin.valueChanged.connect(self.toggleIndexNumber)
        if self.probabilistic:
            for _i in range(self.indexNumber):
                self.tableView.insertRow(_i)
                self.tableView.setItem(_i, 0, QTableWidgetItem("0"))
                self.tableView.setItem(_i, 1, QTableWidgetItem(str(self.value["control list"][_i])))
        else:
            for _i in range(self.indexNumber):
                self.tableView.insertRow(_i)
                self.tableView.setItem(_i, 0, QTableWidgetItem(str(int(self.value["control list"][_i]))))
                self.tableView.setItem(_i, 1, QTableWidgetItem("0"))

        self.ProbabilisticRadio.setChecked(self.probabilistic)
        self.DeterministicRadio.setChecked(not self.probabilistic)
        self.setProbabilistic()

    def probabilisticToggle(self):
        self.probabilistic = self.ProbabilisticRadio.isChecked()
        self.setProbabilistic()

    def setProbabilistic(self):
        qbg = QBrush(QColor(220, 220, 220))
        qbw = QBrush(QColor(255, 255, 255))

        column_to_disable = 0 if self.probabilistic else 1
        column_to_enable = 1 if self.probabilistic else 0

        for row in range(self.tableView.rowCount()):
            self.tableView.item(row, column_to_disable).setFlags(self.tableView.item(row, column_to_disable).flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableView.item(row, column_to_disable).setBackground(qbg)
            self.tableView.item(row, column_to_enable).setFlags(self.tableView.item(row, column_to_enable).flags() | Qt.ItemFlag.ItemIsEditable)
            self.tableView.item(row, column_to_enable).setBackground(qbw)

        if self.probabilistic:
            self.SeriesLength.setEnabled(True)
        else:
            self.SeriesLength.setEnabled(False)

    def updateControlList(self):
        new_ls = []
        if self.probabilistic:
            for row in range(self.tableView.rowCount()):
                new_ls.append(int(self.tableView.item(row, 1).text()))
        else:
            for row in range(self.tableView.rowCount()):
                new_ls.append(int(self.tableView.item(row, 0).text()))
        self.value["control list"] = new_ls

    def toggleIndexNumber(self):
        self.updateControlList()

        for row_id in range(self.tableView.rowCount())[::-1]:
            self.tableView.removeRow(row_id)

        self.indexNumber = self.ItemNumberSpin.value()
        if self.indexNumber <= len(self.value["control list"]):
            self.value["control list"] = self.value["control list"][:self.indexNumber]
        else:
            while self.indexNumber > len(self.value["control list"]):
                self.value["control list"].append(0)

        if self.probabilistic:
            for _i in range(self.indexNumber):
                self.tableView.insertRow(_i)
                self.tableView.setItem(_i, 0, QTableWidgetItem("0"))
                self.tableView.setItem(_i, 1, QTableWidgetItem(str(self.value["control list"][_i])))
        else:
            for _i in range(self.indexNumber):
                self.tableView.insertRow(_i)
                self.tableView.setItem(_i, 0, QTableWidgetItem(str(int(self.value["control list"][_i]))))
                self.tableView.setItem(_i, 1, QTableWidgetItem("0"))

        self.setProbabilistic()

    def exec(self):
        _v = super(ChoiceRandomizerEditor, self).exec()

        try:
            self.updateControlList()
            value = {
                "index number": int(self.ItemNumberSpin.value()),
                "probabilistic": self.probabilistic,
                "control list": self.value["control list"],
                "series length": int(self.SeriesLength.text())
            }
            if self.probabilistic:
                assert value["series length"], "Series length should > 0"
            else:
                assert sum(value["control list"]) > 0, "Series length should > 0"

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Not a valid input! {e.args}")
            return None, _v

        if _v:
            return value, _v
        return None, _v


class MChoiceRandomizer:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = ChoiceRandomizerEditor
    filter_func = dict

    gui_param = {
        "menu_name": "Choice Randomizer",
        "group": "Math"
    }
    template_dict = {
        "type": "MChoiceRandomizer",

        "name": None,
        "value": {
            "index number": 1,
            "probabilistic": False,
            "control list": [0],
            "series length": 0
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None

        self._player = None

        self.series = []
        self.initialize_series()
        self._acc = 0

    def initialize_series(self):
        self.series = []
        if self._value["probabilistic"]:
            # calculate accumulated probability
            acc_prob = []
            acc_sum = sum(self._value["control list"])
            acc_term = 0
            for _i in range(len(self._value["control list"])):
                acc_term += self._value["control list"][_i]
                acc_prob.append(acc_term / acc_sum)

            # generate sequence
            for _i in range(self._value["series length"]):
                _id = 0
                _r = random.random()
                while acc_prob[_id] < _r:
                    _id += 1
                self.series.append(_id)
        else:
            # generate the sequence
            for _i in range(len(self._value["control list"])):
                self.series += [_i for _j in range(self._value["control list"][_i])]

            # shuffle the sequence
            random.shuffle(self.series)

    def get_value(self):
        if self._acc == len(self.series):
            return None
        else:
            self._acc += 1
            return self.series[self._acc-1]

    def set_record(self, _record):
        self._record = _record
