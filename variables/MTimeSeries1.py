# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import copy
import cv2
import numpy as np
import time
import serial

from serial.tools import list_ports


class MyTimeSeries(QThread):

    data_coming = pyqtSignal(float)
    data_flow_aborted = pyqtSignal()

    def __init__(self, com_name):
        super(MyTimeSeries, self).__init__()

        self.connected = False
        self.com_name = com_name

        # try connecting to the port
        self._p = serial.Serial(com_name, baudrate=230400)
        if self._p.isOpen():
            self.connected = True

    def run(self):
        try:
            while self._p.isOpen():
                while self._p.inWaiting():
                    _ndata = self._p.readline().decode("utf-8")
                    try:
                        _data = float(_ndata)
                        self.data_coming.emit(_data)
                    except ValueError:
                        pass
                time.sleep(0.0005)
        except Exception as e:
            self.data_flow_aborted.emit()

    def port_disconnect(self):
        self._p.close()


class Canvas(QGraphicsView):
    resized = pyqtSignal()

    def __init__(self, master, *args):
        super(Canvas, self).__init__(*args)

        self.master = master
        self.ready = False

        self.q_scene = QGraphicsScene()
        self.q_pix_item = QGraphicsPixmapItem()
        self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.q_scene.addItem(self.q_pix_item)
        self.setScene(self.q_scene)

        self.data = []
        self.shown_img = np.zeros([3, 3], dtype=np.uint8)

        self.pixmap = None

        self.ylim = 500
        self.xlim = 1000

        self._id = 0

    def reinitialize(self):
        self.ready = True
        self.shown_img = np.zeros([self.height()-2, self.width()-2, 3], dtype=np.uint8)
        self.data = []
        self.pixmap = QPixmap(QImage(self.shown_img.data, self.shown_img.shape[1], self.shown_img.shape[0], self.shown_img.shape[1]*self.shown_img.shape[2], QImage.Format.Format_RGB888)).scaled(self.width()-2, self.height()-2)
        self.draw_pixmap()

    def append(self, _y):
        self._id += 1
        if len(self.data):
            cv2.rectangle(self.shown_img, self.coor2pix(self._id - 1, self.ylim), self.coor2pix(self._id+20, 0), [0, 0, 0], 0)
            cv2.line(self.shown_img, self.coor2pix(self._id - 1, self.data[-1]), self.coor2pix(self._id, _y), [255, 255, 255], 2)

        self.data.append(_y)

        if len(self.data) > 1e6:
            self.data = self.data[500000:]

        if self._id > self.xlim:
            self._id = 0

        self.pixmap = QPixmap(QImage(self.shown_img.data, self.shown_img.shape[1], self.shown_img.shape[0], self.shown_img.shape[1]*self.shown_img.shape[2], QImage.Format.Format_RGB888)).scaled(self.width()-2, self.height()-2)
        self.draw_pixmap()

    def set_xlim(self, xlim):
        self.xlim = xlim
        self.reinitialize()

    def set_ylim(self, ylim):
        self.ylim = ylim
        self.reinitialize()

    def coor2pix(self, x, y):
        return [round(x/self.xlim*self.shown_img.shape[1]), round((self.ylim-y)/self.ylim*self.shown_img.shape[0])]

    def draw_pixmap(self):
        self.q_pix_item.setPixmap(self.pixmap)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self.ready:
            self.q_scene = QGraphicsScene()
            self.q_pix_item = QGraphicsPixmapItem()
            self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            if self.pixmap is not None:
                self.q_pix_item.setPixmap(self.pixmap.scaled(self.width()-2, self.height()-2))
            self.q_scene.addItem(self.q_pix_item)
            self.setScene(self.q_scene)
            self.resized.emit()
        return super(Canvas, self).resizeEvent(a0)


class TSEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(TSEditor, self).__init__(*args)

        self._value = value

        # create gui
        self.resize(736, 371)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(self)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.availablePortsComboBox = QComboBox(self.groupBox)
        self.availablePortsComboBox.setObjectName(u"availablePortsComboBox")

        self.verticalLayout_3.addWidget(self.availablePortsComboBox)

        self.scanButton = QPushButton(self.groupBox)
        self.scanButton.setObjectName(u"scanButton")

        self.verticalLayout_3.addWidget(self.scanButton)

        self.connectButton = QPushButton(self.groupBox)
        self.connectButton.setObjectName(u"connectButton")

        self.verticalLayout_3.addWidget(self.connectButton)

        self.disconnectButton = QPushButton(self.groupBox)
        self.disconnectButton.setObjectName(u"disconnectButton")

        self.verticalLayout_3.addWidget(self.disconnectButton)

        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.textBrowser = QTextBrowser(self.groupBox)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_3.addWidget(self.textBrowser)

        self.horizontalLayout.addWidget(self.groupBox)

        self.verticalSlider = QSlider(self)
        self.verticalSlider.setObjectName(u"verticalSlider")
        self.verticalSlider.setMinimum(1)
        self.verticalSlider.setMaximum(1024)
        self.verticalSlider.setOrientation(Qt.Orientation.Vertical)

        self.horizontalLayout.addWidget(self.verticalSlider)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = Canvas(self)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        self.horizontalSlider = QSlider(self)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMinimum(1000)
        self.horizontalSlider.setMaximum(10000)
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.horizontalSlider)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(u"Serial data recorder setup")
        self.groupBox.setTitle(u"Set Serial Port")
        self.label.setText(u"Port:")
        self.scanButton.setText(u"Scan")
        self.connectButton.setText(u"Connect")
        self.disconnectButton.setText(u"Disconnect")
        self.label_2.setText(u"Non-data Information")

        # find all available com ports
        self._port_name_list = []
        self.scan()

        self.disconnectButton.setEnabled(False)

        self.horizontalSlider.setValue(self._value["xlim"])
        self.verticalSlider.setValue(self._value["ylim"])

        if self._value["port"] in self._port_name_list:
            self.availablePortsComboBox.setCurrentText(self._value["port"])

        self.timeSeries = None

        self.scanButton.clicked.connect(self.scan)
        self.connectButton.clicked.connect(self.connect)
        self.disconnectButton.clicked.connect(self.port_disconnect)

        self.horizontalSlider.valueChanged.connect(self.horizontal_slider_value_change)
        self.verticalSlider.valueChanged.connect(self.vertical_slider_value_change)

        self.graphicsView.reinitialize()
        self.graphicsView.set_xlim(self._value["xlim"])
        self.graphicsView.set_ylim(self._value["ylim"])

    def port_disconnect(self):
        if self.timeSeries:
            self.timeSeries.port_disconnect()

        self.timeSeries = None

        self.scanButton.setEnabled(True)
        self.scan()
        self.disconnectButton.setEnabled(False)

    def connect(self):
        try:
            self.timeSeries.data_coming.disconnect()
            self.timeSeries.data_flow_aborted.disconnect()
        except:
            pass

        self.timeSeries = MyTimeSeries(self.availablePortsComboBox.currentText())
        if self.timeSeries.connected:
            self.print(f"Successfully connected to {self.availablePortsComboBox.currentText()}")
            self._value["port"] = self.availablePortsComboBox.currentText()
            self.scanButton.setEnabled(False)
            self.connectButton.setEnabled(False)
            self.disconnectButton.setEnabled(True)

            self.graphicsView.reinitialize()
            self.timeSeries.data_coming.connect(self.graphicsView.append)
            self.timeSeries.data_flow_aborted.connect(self.port_disconnect)

            self.timeSeries.start()
        else:
            self.print(f"Connection failure!")

    def scan(self):
        self._port_name_list = []
        _ports = list_ports.comports()
        for _port in _ports:
            self._port_name_list.append(_port.name)

        self.availablePortsComboBox.clear()

        if len(_ports):
            self.availablePortsComboBox.addItems(self._port_name_list)
            self.connectButton.setEnabled(True)
        else:
            self.connectButton.setEnabled(False)

        self.print(f"Port scanning finished! {len(_ports)} ports found.")

    def vertical_slider_value_change(self):
        self.graphicsView.set_ylim(self.verticalSlider.value())
        self._value["ylim"] = self.verticalSlider.value()

    def horizontal_slider_value_change(self):
        self.graphicsView.set_xlim(self.horizontalSlider.value())
        self._value["xlim"] = self.horizontalSlider.value()

    def print(self, content: str):
        self.textBrowser.append(content)

    def exec(self):

        _v = super(TSEditor, self).exec()

        try:
            self.timeSeries.port_disconnect()
        except:
            pass

        if _v:
            return copy.deepcopy(self._value), True

        return None, False


class TSDisplay(QWidget):
    show_event = pyqtSignal(int, int)
    close_event = pyqtSignal()

    def __init__(self):
        super(TSDisplay, self).__init__()

        self.resize(600, 400)
        self.horizontalLayout = QHBoxLayout(self)
        self.graphicsView = Canvas(self)

        self.horizontalLayout.addWidget(self.graphicsView)

        self.setWindowTitle(u"1D Time Series by Serial")

    @pyqtSlot(int, int)
    def show_event_rec(self, _xlim, _ylim):
        self.graphicsView.reinitialize()
        self.graphicsView.set_xlim(_xlim)
        self.graphicsView.set_ylim(_ylim)
        self.show()

    @pyqtSlot()
    def close_event_rec(self):
        self.close()


class TSThread(QThread):
    data_coming = pyqtSignal(float)
    data_flow_aborted = pyqtSignal()

    def __init__(self, _params, runner):
        super(TSThread, self).__init__()

        self.connected = False
        self.com_name = _params["port"]

        # try connecting to the port
        self._p = serial.Serial(self.com_name, baudrate=230400)
        if self._p.isOpen():
            self.connected = True

        self.data = []
        self.runner = runner
        self.path = "test.csv"

    def run(self):
        try:
            while self._p.isOpen():
                while self._p.inWaiting():
                    try:
                        _ndata = self._p.readline()
                        if _ndata is not None:
                            _ndata = _ndata.decode("utf-8")
                            _ts = self.runner.time()
                            _data = float(_ndata)
                            self.data_coming.emit(_data)
                            self.data.append([_ts, _ndata])
                    except ValueError:
                        pass
                    except UnicodeDecodeError:
                        pass
                    except TypeError:
                        break
                    except AttributeError:
                        break
                time.sleep(0.005)
        except serial.serialutil.SerialException as e:
            self.data_flow_aborted.emit()

    def setPath(self, path):
        self.path = path

    def port_disconnect(self):
        try:
            self._p.close()
        except serial.serialutil.SerialException as e:
            pass

        self.save()

    def save(self):
        with open(self.path, 'w') as f:
            st = ""
            for _data in self.data:
                st += f"{_data[0]},{_data[1]}"
            st = st.split()
            st = '\n'.join(st)
            f.write(st)


class MTimeSeries1:

    requirements = {
        "variable": False,
        "runner": True,
        "interface": False
    }
    value_editor = TSEditor
    filter_func = dict

    gui_param = {
        "menu_name": "1D Time Series (Developed for drinkers)",
        "group": "Math"
    }
    template_dict = {
        "type": "MTimeSeries1",

        "name": None,
        "value": {
            "port": "",
            "xlim": 5000,
            "ylim": 80
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.variable = dict()

        self.t_thread = None
        self.runner = None
        self._display = TSDisplay()
        self._display.show_event.connect(self._display.show_event_rec)
        self._display.close_event.connect(self._display.close_event_rec)

    def start(self, path):
        self.t_thread = TSThread(self._value, self.runner)
        self.t_thread.setPath(path)
        self.t_thread.data_coming.connect(self._display.graphicsView.append)

        self._display.show_event.emit(self._value["xlim"], self._value["ylim"])
        self.t_thread.start()

    def stop(self):
        self.t_thread.port_disconnect()
        self._display.close_event.emit()

    def set_record(self, _record):
        self._record = _record
