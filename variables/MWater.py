# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com
import os.path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import serial

from serial.tools import list_ports


class WaterFeeder:

    def __init__(self, com_name):

        self.connected = False
        self.com_name = com_name

        # try connecting to the port
        self._p = serial.Serial(com_name, baudrate=230400)
        if self._p.isOpen():
            self.connected = True

    def port_disconnect(self):
        try:
            self._p.close()
        except:
            pass
        self.connected = False

    def give_water(self):
        try:
            self._p.write(b'w')
            return
        except Exception as e:
            self.port_disconnect()

        try:
            self._p = serial.Serial(self.com_name, baudrate=230400)
            if self._p.isOpen():
                self.connected = True
        except:
            pass


class LickValueEditor(QDialog):

    def __init__(self, var_name, value: str, ass: dict, *args):
        super(LickValueEditor, self).__init__()
        self._value = value

        self.resize(174, 212)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(174, 212))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.comboBox = QComboBox(self)
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout.addWidget(self.comboBox)

        self.scanButton = QPushButton(self)
        self.scanButton.setObjectName(u"scanButton")

        self.verticalLayout.addWidget(self.scanButton)

        self.connectButton = QPushButton(self)
        self.connectButton.setObjectName(u"connectButton")
        self.connectButton.setEnabled(False)

        self.verticalLayout.addWidget(self.connectButton)

        self.disconnectButton = QPushButton(self)
        self.disconnectButton.setObjectName(u"disconnectButton")
        self.disconnectButton.setEnabled(False)

        self.verticalLayout.addWidget(self.disconnectButton)

        self.SendWater = QPushButton(self)
        self.SendWater.setObjectName(u"SendWater")
        self.SendWater.setEnabled(False)

        self.verticalLayout.addWidget(self.SendWater)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Lick")
        self.label.setText("Choose port:")
        self.scanButton.setText("Scan")
        self.connectButton.setText("Connect")
        self.disconnectButton.setText("Disconnect")
        self.SendWater.setText("Send Water")

        self.scanButton.clicked.connect(self.scan)
        self.connectButton.clicked.connect(self.connect)
        self.disconnectButton.clicked.connect(self.port_disconnect)

        self.lick = None

        self._port_name_list = []
        self.scan()
        if self._value in self._port_name_list:
            self.comboBox.setCurrentText(self._value)

    def scan(self):
        _ports = list_ports.comports()
        self._port_name_list = []
        for _port in _ports:
            self._port_name_list.append(_port.name)

        self.comboBox.clear()

        if len(_ports):
            self.comboBox.addItems(self._port_name_list)
            self.connectButton.setEnabled(True)
        else:
            self.connectButton.setEnabled(False)

    def connect(self):
        try:
            self.SendWater.clicked.disconnect()
        except:
            pass

        try:
            self.lick = WaterFeeder(self.comboBox.currentText())
            if self.lick.connected:
                self._value = self.comboBox.currentText()
                self.scanButton.setEnabled(False)
                self.connectButton.setEnabled(False)
                self.disconnectButton.setEnabled(True)
                self.SendWater.setEnabled(True)
                self.SendWater.clicked.connect(self.lick.give_water)
            else:
                QMessageBox.critical(self, "Lickometer Error", "Connection failure!")
        except:
            QMessageBox.critical(self, "Lickometer Error", "Connection failure! Try re-plug your device.")

    def port_disconnect(self):
        self.lick.port_disconnect()
        self.scanButton.setEnabled(True)
        self.scan()
        self.disconnectButton.setEnabled(False)
        self.SendWater.setEnabled(False)

    def exec(self):
        super(LickValueEditor, self).exec()

        return self._value, True


class MWater:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": True
    }
    value_editor = LickValueEditor
    filter_func = str

    gui_param = {
        "menu_name": "Lickometer Interface",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MWater",

        "name": None,
        "value": "",

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.interface = None
        self.variable = dict()

        self.lick = WaterFeeder(value)

    def give_water(self):
        self.lick.give_water()
        self._record.log("Variable", self._name, "Give Water")

    def disconnect(self):
        self.lick.port_disconnect()

    def set_record(self, _record):
        self._record = _record
        self.interface.run_end.connect(self.disconnect)
