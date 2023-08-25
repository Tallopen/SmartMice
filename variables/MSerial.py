# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import serial

from serial.tools import list_ports


class MySerial:

    def __init__(self, com_name, baudrate):

        self.connected = False
        self.com_name = com_name

        # try connecting to the port
        self._p = serial.Serial(com_name, baudrate=baudrate)
        self.baudrate = baudrate
        if self._p.isOpen():
            self.connected = True

    def port_disconnect(self):
        try:
            self._p.close()
        except:
            pass
        self.connected = False

    def write(self, content: bytes):
        try:
            self._p.write(content)
            return
        except Exception as e:
            self.port_disconnect()

            try:
                self._p = serial.Serial(self.com_name, baudrate=self.baudrate)
                if self._p.isOpen():
                    self.connected = True
                    self.write(content)
            except:
                pass

    def wait_and_read(self) -> bytes:
        try:
            if self._p.in_waiting:
                self._p.read(self._p.in_waiting)

            while not self._p.in_waiting:
                pass

            return self._p.read(self._p.in_waiting)
        except Exception as e:
            self.port_disconnect()

            try:
                self._p = serial.Serial(self.com_name, baudrate=self.baudrate)
                if self._p.isOpen():
                    self.connected = True
                    self.wait_and_read()
            except:
                pass


class SerialEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(SerialEditor, self).__init__()

        self._value = value
        self._port_name_list = []

        # below are gui setups
        self.resize(261, 394)
        self.verticalLayout_3 = QVBoxLayout(self)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.BaudRateList = QComboBox(self)
        self.BaudRateList.addItem("4800")
        self.BaudRateList.addItem("9600")
        self.BaudRateList.addItem("115200")
        self.BaudRateList.addItem("230400")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BaudRateList.sizePolicy().hasHeightForWidth())
        self.BaudRateList.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.BaudRateList)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.label_2 = QLabel(self)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.COMNameList = QComboBox(self)
        sizePolicy.setHeightForWidth(self.COMNameList.sizePolicy().hasHeightForWidth())
        self.COMNameList.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.COMNameList)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.ScanButton = QPushButton(self)

        self.horizontalLayout_4.addWidget(self.ScanButton)

        self.ConnectButton = QPushButton(self)
        self.ConnectButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.ConnectButton)

        self.DisconnectButton = QPushButton(self)
        self.DisconnectButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.DisconnectButton)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.ReadButton = QPushButton(self)
        self.ReadButton.setEnabled(False)

        self.verticalLayout.addWidget(self.ReadButton)

        self.horizontalLayout_5 = QHBoxLayout()
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.lineEdit)

        self.WriteButton = QPushButton(self)
        self.WriteButton.setObjectName(u"WriteButton")
        self.WriteButton.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.WriteButton)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.line_2 = QFrame(self)
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.label_3 = QLabel(self)

        self.verticalLayout.addWidget(self.label_3)

        self.textEdit = QTextEdit(self)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout.addWidget(self.textEdit)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_3.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.BaudRateList.setCurrentText(str(self._value["baud-rate"]))

        self.setWindowTitle(f"Configure Serial: {var_name}")
        self.label.setText(u"Baud Rate:")

        self.label_2.setText(u"COM Name:")
        self.ScanButton.setText(u"Scan")
        self.ConnectButton.setText(u"Connect")
        self.DisconnectButton.setText(u"Disconnect")
        self.ReadButton.setText(u"Wait And Read")
        self.WriteButton.setText(u"Write")
        self.label_3.setText(u"Message:")

        # other definition and preparation
        self.ScanButton.clicked.connect(self.scan)
        self.ConnectButton.clicked.connect(self.connect)
        self.DisconnectButton.clicked.connect(self.port_disconnect)
        self.ReadButton.clicked.connect(self.wait_and_read)
        self.WriteButton.clicked.connect(self.write)

        self.scan()

        if self._value["COM"] in self._port_name_list:
            self.COMNameList.setCurrentText(self._value["COM"])

    def scan(self):
        _ports = list_ports.comports()
        self._port_name_list = []
        for _port in _ports:
            self._port_name_list.append(_port.name)

        self.COMNameList.clear()

        if len(_ports):
            self.COMNameList.addItems(self._port_name_list)
            self.ConnectButton.setEnabled(True)
        else:
            self.ConnectButton.setEnabled(False)

    def connect(self):
        try:
            self.serial = MySerial(self.COMNameList.currentText(), int(self.BaudRateList.currentText()))
            if self.serial.connected:
                self._value["COM"] = self.COMNameList.currentText()
                self._value["baud-rate"] = int(self.BaudRateList.currentText())

                self.ScanButton.setEnabled(False)
                self.ConnectButton.setEnabled(False)
                self.DisconnectButton.setEnabled(True)
                self.ReadButton.setEnabled(True)
                self.WriteButton.setEnabled(True)
                self.lineEdit.setEnabled(True)

                self.print(f"[MESSAGE] Port {self._value['COM']} connected.")
            else:
                self.print("[Error] Connection failure! Your device is probably occupied by another program. Try terminate them all.")
        except:
            self.print("[Error] Connection failure! Possibly a hardware problem, try re-plugging your device.")

    def port_disconnect(self):
        self.serial.port_disconnect()
        self.ScanButton.setEnabled(True)
        self.scan()
        self.DisconnectButton.setEnabled(False)
        self.ReadButton.setEnabled(False)
        self.WriteButton.setEnabled(False)
        self.lineEdit.setEnabled(False)

        self.print(f"[MESSAGE] Port {self._value['COM']} disconnected.")

    def wait_and_read(self):
        self.print(f"[MESSAGE] Bytes read: {self.serial.wait_and_read()}")

    def write(self):
        _bytes = bytes(self.lineEdit.text(), "utf8")
        self.serial.write(_bytes)
        self.print(f"[MESSAGE] Bytes written: {_bytes}")
        self.lineEdit.clear()

    def print(self, content):
        self.textEdit.append(content)

    def exec(self):
        super(SerialEditor, self).exec()

        return self._value, True


class MSerial:

    requirements = {
        "variable": False,
        "runner": False,
        "interface": False
    }
    value_editor = SerialEditor
    filter_func = dict

    gui_param = {
        "menu_name": "Serial",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MSerial",

        "name": None,
        "value": {
            "COM": "",
            "baud-rate": 230400
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.variable = dict()

        self.serial = MySerial(value["COM"], value["baud-rate"])

    def write(self, value):
        self.serial.write(value)

    def wait_and_read(self):
        return self.serial.wait_and_read()

    def disconnect(self):
        self.serial.port_disconnect()

    def set_record(self, _record):
        self._record = _record
