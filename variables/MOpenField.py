# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com
import random
import threading
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import numpy as np
import cv2


def find_min_elements(matrix, n):
    flattened_indices = np.argsort(matrix.flatten())[:n]

    row_indices = np.floor(flattened_indices / matrix.shape[1]).astype(int)
    col_indices = flattened_indices % matrix.shape[1]

    return [(row, col) for row, col in zip(row_indices, col_indices)]


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, _w, _s, _m):
        return None


class Canvas(QGraphicsView):
    resized = pyqtSignal()

    def __init__(self, master, *args):
        super(Canvas, self).__init__(*args)

        self.master = master

        self.q_scene = QGraphicsScene()
        self.q_pix_item = QGraphicsPixmapItem()
        self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.q_scene.addItem(self.q_pix_item)
        self.setScene(self.q_scene)

        self.pixmap = None

    def draw_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.q_pix_item.setPixmap(self.pixmap)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.q_scene = QGraphicsScene()
        self.q_pix_item = QGraphicsPixmapItem()
        self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        if self.pixmap is not None:
            self.q_pix_item.setPixmap(self.pixmap.scaled(self.width()-2, self.height()-2))
        self.q_scene.addItem(self.q_pix_item)
        self.setScene(self.q_scene)
        self.resized.emit()
        return super(Canvas, self).resizeEvent(a0)


class OpenFieldEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(OpenFieldEditor, self).__init__()

        available_variables = {_k: _i["type"] for _k, _i in ass.items()}

        self.value = value

        self.resize(376, 237)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(50, 0))

        self.horizontalLayout.addWidget(self.label_2)

        self.XLowLimit = QLineEdit(self)
        self.XLowLimit.setObjectName(u"XLowLimit")
        self.XLowLimit.setMinimumSize(QSize(75, 0))
        self.XLowLimit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout.addWidget(self.XLowLimit)

        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.XHighLimit = QLineEdit(self)
        self.XHighLimit.setObjectName(u"XHighLimit")
        self.XHighLimit.setMinimumSize(QSize(75, 0))
        self.XHighLimit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout.addWidget(self.XHighLimit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_4 = QLabel(self)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_3.addWidget(self.label_4)

        self.YLowLimit = QLineEdit(self)
        self.YLowLimit.setObjectName(u"YLowLimit")
        self.YLowLimit.setMinimumSize(QSize(75, 0))
        self.YLowLimit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_3.addWidget(self.YLowLimit)

        self.label_5 = QLabel(self)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.YHighLimit = QLineEdit(self)
        self.YHighLimit.setObjectName(u"YHighLimit")
        self.YHighLimit.setMinimumSize(QSize(75, 0))
        self.YHighLimit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_3.addWidget(self.YHighLimit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_6 = QLabel(self)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_2.addWidget(self.label_6)

        self.BinSizeLineEdit = QLineEdit(self)
        self.BinSizeLineEdit.setObjectName(u"BinSizeLineEdit")
        self.BinSizeLineEdit.setMinimumSize(QSize(75, 0))
        self.BinSizeLineEdit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_2.addWidget(self.BinSizeLineEdit)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.line = QFrame(self)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.label_7 = QLabel(self)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout.addWidget(self.label_7)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_9 = QLabel(self)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.label_9, 1, 0, 1, 1)

        self.label_8 = QLabel(self)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(40, 0))

        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)

        self.XVarCombo = QComboBox(self)
        self.XVarCombo.setObjectName(u"XVarCombo")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.XVarCombo.sizePolicy().hasHeightForWidth())
        self.XVarCombo.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.XVarCombo, 0, 1, 1, 1)

        self.YVarCombo = QComboBox(self)
        sizePolicy.setHeightForWidth(self.YVarCombo.sizePolicy().hasHeightForWidth())
        self.YVarCombo.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.YVarCombo, 1, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(f"Open Field Editor: {var_name}")
        self.label.setText(u"Field Size")
        self.label_2.setText(u"X Limit: ")
        self.XLowLimit.setText(str(value["XLim"][0]))
        self.label_3.setText(u"~")
        self.XHighLimit.setText(str(value["XLim"][1]))
        self.label_4.setText(u"Y Limit: ")
        self.YLowLimit.setText(str(value["YLim"][0]))
        self.label_5.setText(u"~")
        self.YHighLimit.setText(str(value["YLim"][1]))
        self.label_6.setText(u"Square Binning Size:")
        self.BinSizeLineEdit.setText(str(value["binSize"]))
        self.label_7.setText(u"Variable Source:")
        self.label_9.setText(u"Y:")
        self.label_8.setText(u"X:")

        available_variable_name = set()

        # generate items
        for _var_name, _var_type in available_variables.items():
            if _var_type == "MNum":
                self.XVarCombo.addItem(_var_name)
                self.YVarCombo.addItem(_var_name)
                available_variable_name.add(_var_name)

        if self.value["XVar"] in available_variable_name:
            self.XVarCombo.setCurrentText(self.value["XVar"])

        if self.value["YVar"] in available_variable_name:
            self.YVarCombo.setCurrentText(self.value["YVar"])

    def exec(self):
        _v = super(OpenFieldEditor, self).exec()

        self.value["XVar"] = self.XVarCombo.currentText()
        self.value["YVar"] = self.YVarCombo.currentText()
        self.value["XLim"] = [float(self.XLowLimit.text()), float(self.XHighLimit.text())]
        self.value["YLim"] = [float(self.YLowLimit.text()), float(self.YHighLimit.text())]
        self.value["binSize"] = float(self.BinSizeLineEdit.text())

        if _v:
            return self.value, _v
        return None, _v


class OFViewer(QWidget):

    show_event = pyqtSignal(list, list, float)
    var_update_event = pyqtSignal(float, float)
    close_event = pyqtSignal()

    def __init__(self, title):
        super(OFViewer, self).__init__()

        self.resize(400, 300)
        self.verticalLayout = QVBoxLayout(self)
        self.graphicsView = Canvas(self)
        self.verticalLayout.addWidget(self.graphicsView)
        self.setWindowTitle(title)

        self.map = np.zeros([1, 1])

        self.of_img = np.zeros([1, 1, 1])
        self.traj_img = np.zeros([1, 1, 1])
        self.total_img = self.of_img + self.traj_img

        self.last_positions = [[0, 0]] * 20

        self.startTime = 0
        self.lastTime = 0

        self.xlim = [0, 0]
        self.ylim = [0, 0]
        self.binSize = 0
        self.mapXn = 0
        self.mapYn = 0

    def show_event_rec(self, Xlim, Ylim, binSize):
        self.xlim = Xlim
        self.ylim = Ylim
        self.binSize = binSize
        self.mapXn = int(np.ceil((Xlim[1]-Xlim[0]) / binSize))
        self.mapYn = int(np.ceil((Ylim[1]-Ylim[0]) / binSize))

        self.map = np.zeros([self.mapYn, self.mapXn])
        self.of_img = np.zeros([self.graphicsView.height(), self.graphicsView.width(), 3], dtype=np.uint8)
        self.traj_img = np.zeros([self.graphicsView.height(), self.graphicsView.width(), 3], dtype=np.uint8)
        self.total_img = self.of_img + self.traj_img
        # self.graphicsView.draw_pixmap(self.total_img)
        self.startTime = time.time()
        self.show()

    def var_update_rec(self, cx, cy):
        currentTime = time.time()
        deltaTime = currentTime - self.lastTime

        if deltaTime > 0:
            self.last_positions.append([cx, cy])
            self.last_positions.pop(0)

            if self.lastTime:
                self.of_img = np.zeros([self.graphicsView.height(), self.graphicsView.width()], dtype=np.uint8)
                self.of_img = cv2.cvtColor(self.of_img,cv2.COLOR_GRAY2BGR)
                # if this is not the first point, find all bins that are passed through,
                # and the theoretical time cost on each bin, add to self.map
                start_point = np.array(self.last_positions[-2])
                end_point = np.array(self.last_positions[-1])

                # use 50x linspace to find out index
                xind = (np.linspace(start_point[0], end_point[0], 50) - self.xlim[0]) / self.binSize
                yind = (np.linspace(start_point[1], end_point[1], 50) - self.ylim[0]) / self.binSize
                xindmin = xind - 0.02
                xindmax = xind + 0.02
                yindmin = yind - 0.02
                yindmax = yind + 0.02
                xind = np.concatenate([xind, xindmin, xindmax, xind, xind])
                yind = np.concatenate([yind, yind, yind, yindmax, yindmin])
                xind = np.floor(xind)
                yind = np.floor(yind)
                good_index = np.logical_and(np.logical_and(np.logical_and(0 <= xind, xind < self.mapXn), 0 <= yind), yind < self.mapYn)
                xind = xind[good_index].astype(np.int)
                yind = yind[good_index].astype(np.int)
                time_unit = 1 / len(xind) * deltaTime
                for i in range(len(xind)):
                    self.map[yind[i], xind[i]] += time_unit

                # then use only red channel to show each bin's time
                illum = np.floor(self.map / (currentTime - self.startTime) * 100 * self.mapXn*self.mapYn)
                binWidth = np.floor(min(self.graphicsView.width() / self.mapXn, self.graphicsView.height() / self.mapYn))
                h = self.graphicsView.height()

                for xi in range(self.mapXn):
                    for yi in range(self.mapYn):
                        self.of_img = cv2.fillPoly(self.of_img, [np.array([[round(xi*binWidth), round(h-yi*binWidth)],
                                                                [round((xi+1)*binWidth), round(h-yi*binWidth)],
                                                                [round((xi+1)*binWidth), round(h-(yi+1)*binWidth)],
                                                                [round(xi*binWidth), round(h-(yi+1)*binWidth)]], dtype=np.int32)], (round(illum[yi, xi]), 0, 0))

                # use all channels to show recent 10 positions
                self.traj_img = np.zeros([self.graphicsView.height(), self.graphicsView.width()], dtype=np.uint8)
                self.traj_img = cv2.cvtColor(self.traj_img, cv2.COLOR_GRAY2BGR)
                for i in range(20):
                    cv2.circle(self.traj_img, (round((self.last_positions[-i][0] - self.xlim[0]) / self.binSize * binWidth),
                                               round(h-(self.last_positions[-i][1]- self.ylim[0])/self.binSize*binWidth)), round(binWidth/5), (0, 255-i*10, 255-i*10), -1)

                # add all these together and display it
                self.total_img = self.of_img + self.traj_img
                tim = QPixmap(QImage(self.total_img, self.total_img.shape[1], self.total_img.shape[0], self.total_img.shape[1]*3, QImage.Format.Format_RGB888)).scaled(self.graphicsView.width()-2, self.graphicsView.height()-2)
                self.graphicsView.draw_pixmap(tim)

        self.lastTime = currentTime

    def close_event_rec(self):
        self.close()

    def get_pos_by_less_visit(self):
        if self.map.size <= 0:
            target_bin = [np.random.randint(0, self.mapYn), np.random.randint(0, self.mapXn)]
        else:
            target_bin_num = int(self.map.size*0.4)
            target_bins = find_min_elements(self.map, target_bin_num)
            target_bin = target_bins[np.random.randint(0, target_bin_num)]

        return ((target_bin[1] + random.random()) * self.binSize + self.xlim[0]) / 10, ((target_bin[0] + random.random()) * self.binSize + self.ylim[0]) / 10


class MOpenField:

    requirements = {
        "variable": True,
        "runner": True,
        "interface": False
    }
    value_editor = OpenFieldEditor
    filter_func = dict

    gui_param = {
        "menu_name": "Open Field",
        "group": "Visualization"
    }
    template_dict = {
        "type": "MOpenField",

        "name": None,
        "value": {
            "XLim": [-200, 200],
            "YLim": [-200, 200],
            "binSize": 20,
            "XVar": "",
            "YVar": ""
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None

        self.variable = dict()
        self.runner = None

        self._viewer = OFViewer(self._name)
        self._viewer.show_event.connect(self._viewer.show_event_rec)
        self._viewer.var_update_event.connect(self._viewer.var_update_rec)
        self._viewer.close_event.connect(self._viewer.close_event_rec)

    def set_record(self, _record):
        self._record = _record

    def _update(self):
        while self.runner.is_running():
            _acc_terms = dict()
            self._viewer.var_update_event.emit(self.variable[self._value["XVar"]].get_value(), self.variable[self._value["YVar"]].get_value())
            time.sleep(0.04)
        self._viewer.close_event.emit()

    def show(self):
        self._viewer.show_event.emit(self._value["XLim"], self._value["YLim"], self._value["binSize"])

        threading.Thread(target=self._update).start()
        time.sleep(1)

    def get_pos_by_less_visit(self):
        return self._viewer.get_pos_by_less_visit()
