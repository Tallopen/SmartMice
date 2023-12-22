# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com

import copy
import gc
import queue
import threading

import cv2
from functools import partial
import os.path
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from queue import Queue
import time

import numpy as np


COMMON_FRAME_SIZE = {
    "1920*1080": (1920, 1080),
    "1280*720": (1280, 720),
    "720*480": (720, 480),
    "640*480": (640, 480),
    "320*240": (320, 240)
}
COMMON_FRAME_SIZE_REVERSE = {j:i for i,j in COMMON_FRAME_SIZE.items()}
COMMON_FRAME_RATE = [10, 20, 24, 25, 30, 50, 60, 120]


class MyThread(QThread):

    def __init__(self, target):

        super(QThread, self).__init__()
        self._foo = target

    def run(self):
        self._foo()


CAMERA_VALUES = {
    "brightness": (-128, 128, cv2.CAP_PROP_BRIGHTNESS),
    "contrast": (0, 256, cv2.CAP_PROP_CONTRAST),
    "gain": (1, 64, cv2.CAP_PROP_GAIN),
    "saturation": (0, 256, cv2.CAP_PROP_SATURATION),
    "exposure": (-12, 0, cv2.CAP_PROP_EXPOSURE),
    "hue": (0, 180, cv2.CAP_PROP_HUE),
    "white balance": (0, 10000, cv2.CAP_PROP_WB_TEMPERATURE),
    "gamma": (0, 256, cv2.CAP_PROP_GAMMA)
}


class Canvas(QGraphicsView):
    resized = pyqtSignal()
    mouse_move = pyqtSignal(int, int)
    left_mouse_click = pyqtSignal(int, int)
    left_mouse_press = pyqtSignal(int, int)
    left_mouse_move = pyqtSignal(int, int)

    def __init__(self, master, *args):
        super(Canvas, self).__init__(*args)

        self.master = master
        self.ready = False
        self.pressed_button = None
        self.setMouseTracking(True)

        self.q_scene = QGraphicsScene()
        self.q_pix_item = QGraphicsPixmapItem()
        self.q_pix_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.q_scene.addItem(self.q_pix_item)
        self.setScene(self.q_scene)

        self.pixmap = None

        self.prev_mouse_pos = QPointF(0, 0)

    def draw_pixmap(self, pixmap):
        self.pixmap = pixmap
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

    def mouseMoveEvent(self, a0: QMouseEvent):
        self.prev_mouse_pos = a0.position()
        if self.ready:
            if a0.buttons() == Qt.MouseButton.LeftButton:
                self.left_mouse_move.emit(a0.position().x()-4, a0.position().y()-4)
            else:
                self.mouse_move.emit(a0.position().x()-4, a0.position().y()-4)
        return super(Canvas, self).mouseMoveEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent):
        if self.ready:
            self.pressed_button = a0.buttons()
            if self.pressed_button == Qt.MouseButton.LeftButton:
                self.left_mouse_press.emit(a0.position().x()-4, a0.position().y()-4)
            elif a0.buttons() == Qt.MouseButton.MiddleButton:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
        return super(Canvas, self).mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if self.ready:
            if self.pressed_button == Qt.MouseButton.LeftButton:
                self.left_mouse_click.emit(a0.position().x()-4, a0.position().y()-4)
        return super(Canvas, self).mouseReleaseEvent(a0)


class VideoTick(QThread):

    img_change = pyqtSignal()

    def __init__(self, master, use_optical_flow):

        super(VideoTick, self).__init__()
        self.master = master
        self.last_img = None
        self.use_optical_flow = use_optical_flow

    def run(self):
        _img = None
        while not self.master.stop_video:
            self.last_img = _img
            _img = self.master.vd.read()
            if _img[0]:
                _img = _img[1]
                if self.use_optical_flow and self.last_img is not None:
                    flow = cv2.calcOpticalFlowFarneback(cv2.cvtColor(self.last_img, cv2.COLOR_BGR2GRAY), cv2.cvtColor(_img, cv2.COLOR_BGR2GRAY), None, 0.05, 1, 30, 1, 1, 150, 1)
                    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

                    hsv = np.zeros_like(_img)
                    hsv[:, :, 1] = 255
                    hsv[..., 0] = ang * 180 / np.pi / 2
                    hsv[..., 2] = mag * 5  #cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
                    rgb_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                else:
                    rgb_img = cv2.cvtColor(_img, cv2.COLOR_BGR2RGB)
                self.master.img = rgb_img
                self.img_change.emit()
            time.sleep(0.02)
        self.master.vd.release()


class CamEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(CamEditor, self).__init__()

        self.value = value
        self.value_copy = copy.deepcopy(self.value)

        self.resize(457, 480)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.CameraReturn = Canvas(self)
        self.CameraReturn.setObjectName(u"CameraReturn")

        self.verticalLayout.addWidget(self.CameraReturn)

        self.horizontalLayout_2 = QHBoxLayout()
        self.label_2 = QLabel(self)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setMinimumSize(QSize(100, 0))
        self.pushButton_2.setMaximumSize(QSize(100, 16777215))

        self.showWindowCheckBox = QCheckBox("Show Window", self)
        self.value_copy["show window"] = value.get("show window", True)
        self.showWindowCheckBox.setChecked(self.value_copy["show window"])
        self.showWindowCheckBox.clicked.connect(self.show_window_set)

        self.saveCheckBox = QCheckBox("Save", self)
        self.value_copy["save"] = value.get("save", True)
        self.saveCheckBox.setChecked(self.value_copy["save"])
        self.saveCheckBox.clicked.connect(self.save_set)

        self.ofCheckBox = QCheckBox("Use Optical Flow", self)
        self.value_copy["optic flow"] = value.get("optic flow", False)
        self.ofCheckBox.setChecked(self.value_copy["optic flow"])
        self.ofCheckBox.clicked.connect(self.of_set)

        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.horizontalLayout_2.addWidget(self.showWindowCheckBox)
        self.horizontalLayout_2.addWidget(self.saveCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.label_3 = QLabel("Frame Rate:", self)
        self.FrameRateCombo = QComboBox(self)
        for _frame_rate in COMMON_FRAME_RATE:
            self.FrameRateCombo.addItem(str(_frame_rate))
        _fr = value.get("frame rate", 30)
        self.value_copy["frame rate"] = _fr
        self.FrameRateCombo.setCurrentText(str(_fr))

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.label_4 = QLabel("Frame Size:", self)
        self.FrameSizeCombo = QComboBox(self)
        for _frame_size in COMMON_FRAME_SIZE.keys():
            self.FrameSizeCombo.addItem(_frame_size)
        _fs = value.get("frame size", (640, 480))
        self.FrameSizeCombo.setCurrentText(COMMON_FRAME_SIZE_REVERSE.get(_fs, "640*480"))
        self.value_copy["frame size"] = COMMON_FRAME_SIZE[self.FrameSizeCombo.currentText()]

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.FrameRateCombo.setSizePolicy(sizePolicy)
        self.FrameSizeCombo.setSizePolicy(sizePolicy)

        self.FrameRateCombo.currentTextChanged.connect(self.frame_rate_change)
        self.FrameSizeCombo.currentTextChanged.connect(self.frame_size_change)

        self.horizontalLayout_3.addWidget(self.label_3)
        self.horizontalLayout_3.addWidget(self.FrameRateCombo)
        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)
        self.horizontalLayout_3.addWidget(self.label_4)
        self.horizontalLayout_3.addWidget(self.FrameSizeCombo)
        self.horizontalLayout_3.addWidget(self.ofCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 435, 194))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Set MCam Parameter")
        self.label_2.setText(f"{var_name}: (0x0)")
        self.pushButton_2.setText("Set ID")
        self.pushButton_2.clicked.connect(self.set_camera_id)

        self.CameraReturn.left_mouse_press.connect(self.set_roi_begin)
        self.CameraReturn.left_mouse_move.connect(self.set_roi)
        self.CameraReturn.left_mouse_click.connect(self.release_mouse)

        self.scroll_item = dict()
        for key, value in CAMERA_VALUES.items():
            _horizontalLayout = QHBoxLayout()
            _label = QLabel(self.scrollAreaWidgetContents)
            _label.setText(key)

            _horizontalLayout.addWidget(_label)

            _horizontalSlider = QSlider(self.scrollAreaWidgetContents)
            _horizontalSlider.setMinimum(value[0])
            _horizontalSlider.setMaximum(value[1])
            _horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
            _horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
            _horizontalSlider.setTickInterval((value[1]-value[0]+14) // 16)

            _horizontalLayout.addWidget(_horizontalSlider)

            _spinBox = QSpinBox(self.scrollAreaWidgetContents)
            _spinBox.setMinimum(value[0])
            _spinBox.setMaximum(value[1])

            _horizontalLayout.addWidget(_spinBox)
            self.scroll_item[key] = [_horizontalSlider, _spinBox, value[2], True]
            self.verticalLayout_3.addLayout(_horizontalLayout)

        self.stop_video = True
        self.vd = None
        self._v = None
        self.img = None

        self.start_video()

        self.editing_roi = False
        self.roi_pt1 = ()

    def of_set(self):
        self.value_copy["optic flow"] = self.ofCheckBox.isChecked()
        if not self.stop_video:
            self._v.use_optical_flow = self.value_copy["optic flow"]

    def cor_transform(self, _x, _y):
        _h = self.img.shape[0]
        _w = self.img.shape[1]

        _x = int(_x / self.CameraReturn.width() * _w)
        _y = int(_y / self.CameraReturn.height() * _h)

        return _x, _y

    def set_roi_begin(self, _x, _y):
        if self.img is not None:
            self.roi_pt1 = self.cor_transform(_x, _y)
            self.editing_roi = True

    def set_roi(self, _x, _y):
        if self.img is not None and self.editing_roi:
            roi_pt2 = self.cor_transform(_x, _y)
            pt1 = min(self.roi_pt1[0], roi_pt2[0]), min(self.roi_pt1[1], roi_pt2[1])
            pt2 = max(self.roi_pt1[0], roi_pt2[0]), max(self.roi_pt1[1], roi_pt2[1])
            self.value_copy["ROI"] = [pt1, pt2]

    def show_window_set(self):
        self.value_copy["show window"] = self.showWindowCheckBox.isChecked()

    def save_set(self):
        self.value_copy["save"] = self.saveCheckBox.isChecked()

    def release_mouse(self, _x, _y):
        if self.img is not None and self.editing_roi:
            roi_pt2 = self.cor_transform(_x, _y)
            pt1 = min(self.roi_pt1[0], roi_pt2[0]), min(self.roi_pt1[1], roi_pt2[1])
            pt2 = max(self.roi_pt1[0], roi_pt2[0]), max(self.roi_pt1[1], roi_pt2[1])
            self.value_copy["ROI"] = [pt1, pt2]
            self.editing_roi = False

    def set_camera_id(self):
        self.stop_video = True
        self.camera_del()
        _value_shown = self.value_copy["ID"]
        if not self.value_copy["ID"]:
            _value_shown = 0
        _i = QInputDialog.getInt(self, "Camera ID set", "Set a camera ID below, which should be a non-negative integer", _value_shown)
        if _i[1]:
            self.value_copy["ID"] = _i[0]
            self.start_video()
        else:
            QMessageBox.critical(self, "Camera Error", f"Not a legal ID.")

    def start_video(self):
        if self.value_copy["ID"] is not None:
            self.vd = cv2.VideoCapture(self.value_copy["ID"])
            if self.vd.isOpened():
                self.stop_video = False
                self.camera_init()

                self._v = VideoTick(self, self.value_copy["optic flow"])
                self._v.img_change.connect(self.video_tick)
                self._v.start()

                self.CameraReturn.ready = True
                return
        QMessageBox.critical(self, "Camera Error", f"The camera (ID = {self.value['ID']}) cannot be connected.")

    def camera_init(self):
        self.vd.set(cv2.CAP_PROP_FPS, self.value_copy["frame rate"])
        self.vd.set(cv2.CAP_PROP_FRAME_WIDTH, self.value_copy["frame size"][0])
        self.vd.set(cv2.CAP_PROP_FRAME_HEIGHT, self.value_copy["frame size"][1])
        for key, value in self.scroll_item.items():
            value[0].setValue(self.value[key])
            value[1].setValue(self.value[key])
            self.vd.set(value[2], self.value[key])
            value[0].valueChanged.connect(partial(self.scroll_value_change, key, value))
            value[1].valueChanged.connect(partial(self.spin_value_change, key, value))

    def camera_del(self):
        try:
            self.vd.release()
        except:
            pass
        for key, value in self.scroll_item.items():
            try:
                value[0].valueChanged.disconnect()
                value[1].valueChanged.disconnect()
            except:
                pass

    def scroll_value_change(self, key, value_array):
        if value_array[3]:
            value_array[3] = False
            value_array[1].setValue(value_array[0].value())
            value_array[3] = True

        self.vd.set(value_array[2], value_array[0].value())
        self.value_copy[key] = value_array[0].value()

    def frame_rate_change(self):
        self.value_copy["frame rate"] = int(self.FrameRateCombo.currentText())
        self.stop_video = True
        self.camera_del()
        self.start_video()
        self.value_copy["frame rate"] = int(self.vd.get(cv2.CAP_PROP_FPS))
        self.FrameRateCombo.setCurrentText(str(self.value_copy["frame rate"]))

    def frame_size_change(self):
        self.value_copy["frame size"] = COMMON_FRAME_SIZE[self.FrameSizeCombo.currentText()]
        self.stop_video = True
        self.camera_del()
        self.start_video()

    def spin_value_change(self, key, value_array):
        if value_array[3]:
            value_array[3] = False
            value_array[0].setValue(value_array[1].value())
            value_array[3] = True

        self.vd.set(value_array[2], value_array[1].value())
        self.value_copy[key] = value_array[1].value()

    def video_tick(self):
        img = copy.deepcopy(self.img)
        img += (255-img)//5*4
        if self.value_copy["ROI"]:
            pt11 = self.value_copy["ROI"][0]
            pt21 = self.value_copy["ROI"][1]
            pt1 = min(pt11[0], pt21[0]), min(pt11[1], pt21[1])
            pt2 = max(pt11[0], pt21[0]), max(pt11[1], pt21[1])
            pt1 = max(pt1[0], 0), max(pt1[1], 0)
            pt2 = min(pt2[0], img.shape[1]-1), min(pt2[1], img.shape[0]-1)
        else:
            pt1 = (0, 0)
            pt2 = (img.shape[1]-1, img.shape[0]-1)

        img[pt1[1]:pt2[1], pt1[0]:pt2[0], :] = self.img[pt1[1]:pt2[1], pt1[0]:pt2[0], :]
        cv2.rectangle(img, pt1, pt2, color=(255, 0, 0), thickness=2)

        pix_map = QPixmap(QImage(img, img.shape[1], img.shape[0], QImage.Format.Format_RGB888)).scaled(self.CameraReturn.width()-2, self.CameraReturn.height()-2)
        self.CameraReturn.draw_pixmap(pix_map)

    def exec(self):
        _v = super(CamEditor, self).exec()
        self.stop_video = True

        if _v:
            return self.value_copy, _v
        else:
            return None, _v


def none_func(x):
    return x


class CameraWindow(QWidget):

    my_resized = pyqtSignal(int, int)
    img_updated = pyqtSignal(object)
    to_close = pyqtSignal()

    def __init__(self, title):

        super(CameraWindow, self).__init__()
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.CameraReturn = Canvas(self)

        self.verticalLayout.addWidget(self.CameraReturn)
        self.setWindowTitle(title)

    def set_size(self, _w, _h):
        self.resize(_w, _h)
        self.show()

    def update_img(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pix_map = QPixmap(QImage(img, img.shape[1], img.shape[0], img.shape[1]*img.shape[2], QImage.Format.Format_RGB888)).scaled(self.CameraReturn.width()-2, self.CameraReturn.height()-2)
        self.CameraReturn.draw_pixmap(pix_map)


class MCam:

    requirements = {
        "variable": True,
        "runner": True,
        "interface": False
    }
    value_editor = CamEditor

    filter_func = none_func

    gui_param = {
        "menu_name": "Camera",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MCam",

        "name": None,
        "value": {
            "ID": None,
            "brightness": 0,   # -128 - 128
            "contrast": 20,
            "saturation": 128,
            "hue": 128,   # 0-180
            "exposure": -8,
            "gain": 6,
            "white balance": 4000,         # 3000-7000
            "gamma": 128,      # what's the range? ...
            "ROI": None,

            "frame size": (720, 480),
            "frame rate": 20,

            "show window": True,
            "save": True,
            "optic flow": False
        },

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = value
        self._name = _name
        self._record = None
        self.variable = dict()
        self.runner = None

        self._folder = ""

        self._vd = None
        self._img_queue = Queue(50)  # the maximum buffered frame number is 50, frames will be lost if surpassing this number
        self._img_count = 0
        self._save_batch_count = 0
        self._recording = False
        self._time_stamp = []

        self._window = CameraWindow(self._name)
        self._window.my_resized.connect(self._window.set_size)
        self._window.img_updated.connect(self._window.update_img)
        self._window.to_close.connect(self._window.close)

        self._show_window = self._value.get("show window", True)
        self._save = self._value.get("save", True)
        self._optic_flow = self._value.get("optic flow", False)

        self.current_img = None
        self._ready = False

        self._t3 = None

    def set_record(self, _record):
        self._record = _record

    def run(self, folder: str):
        self._folder = folder
        if self._save:
            if not os.path.isdir(self._folder):
                os.mkdir(self._folder)

        self._vd = cv2.VideoCapture(self._value["ID"])
        if self._vd.isOpened():
            self._recording = True

            self._vd.set(cv2.CAP_PROP_FPS, self._value["frame rate"])
            self._vd.set(cv2.CAP_PROP_FRAME_WIDTH, self._value["frame size"][0])
            self._vd.set(cv2.CAP_PROP_FRAME_HEIGHT, self._value["frame size"][1])
            for _key, _value in CAMERA_VALUES.items():
                self._vd.set(_value[2], self._value[_key])
            self._vd.set(cv2.CAP_PROP_FPS, 20)
            self.current_img = self._vd.read()[1]

            threading.Thread(target=self._cam_tick).start()
            threading.Thread(target=self._cam_save).start()

            if self._show_window:
                _x0, _x1, _y0, _y1, _w, _h = self.get_wh()
                self._window.CameraReturn.ready = True
                self._window.my_resized.emit(_w, _h)
                self._t3 = MyThread(target=self._update_window)
                self._t3.start()
        else:
            raise Exception(f"Camera Error: The camera (ID = {self._value['ID']}) cannot be connected.")

    def _cam_tick(self):
        while self._recording:
            self._img_queue.put((self._record.get_time(), self._vd.read()[1]))
            if not self.runner.is_running():
                self._vd.release()
                self.stop()

    def get_wh(self):
        _w = self.current_img.shape[1]
        _h = self.current_img.shape[0]
        _x0 = 0
        _x1 = _w
        _y0 = 0
        _y1 = _h
        if self._value["ROI"]:
            _x0 = max(self._value["ROI"][0][0], 0)
            _x1 = min(self._value["ROI"][1][0], _w-1)
            _y0 = max(self._value["ROI"][0][1], 0)
            _y1 = min(self._value["ROI"][1][1], _h-1)
            _w = _x1 - _x0
            _h = _y1 - _y0
        return _x0, _x1, _y0, _y1, _w, _h

    def _cam_save(self):
        if self._save:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            file_name = os.path.join(self._folder, str(self._save_batch_count)+".mp4")
            time_stamp_file_name = os.path.join(self._folder, "timestamp.csv")
            self._record.append_data_accessory("MCam", (file_name, time_stamp_file_name))
            _x0, _x1, _y0, _y1, _w, _h = self.get_wh()
            _f = cv2.VideoWriter(file_name, fourcc, 20, (_w, _h))

            while self._recording:
                try:
                    _current_img = self._img_queue.get(block=True, timeout=0.04)
                except queue.Empty:
                    continue
                if _current_img is not None:
                    _img = _current_img[1]
                    if self._value["ROI"] is not None:
                        _img = _img[_y0:_y1, _x0:_x1, :]
                    self.current_img = _img
                    self._ready = True
                    _f.write(_img)
                    self._time_stamp.append(_current_img[0])
                    self._img_count += 1
                if self._img_count == 1000:
                    _f.release()
                    del _f
                    gc.collect()
                    self._img_count = 0
                    self._save_batch_count += 1
                    file_name = os.path.join(self._folder, str(self._save_batch_count)+".mp4")
                    _f = cv2.VideoWriter(file_name, fourcc, 20, (_w, _h))

            while not self._img_queue.empty():
                try:
                    _current_img = self._img_queue.get(block=True, timeout=0.04)
                except queue.Empty:
                    continue
                _img = _current_img[1]
                if self._value["ROI"] is not None:
                    _img = _img[_y0:_y1, _x0:_x1, :]
                _f.write(_img)
                self._time_stamp.append(_current_img[0])
                self._img_count += 1
                if self._img_count == 1000:
                    _f.release()
                    del _f
                    gc.collect()
                    self._img_count = 0
                    self._save_batch_count += 1
                    file_name = os.path.join(self._folder, str(self._save_batch_count)+".mp4")
                    _f = cv2.VideoWriter(file_name, fourcc, 20, (_w, _h))

            _f.release()

            time_stamp_record = "Frame ID,Relative Time (s)"
            for _t, _ts in enumerate(self._time_stamp):
                time_stamp_record += "\n" + str(_t+1) + "," + str(_ts)

            with open(time_stamp_file_name, 'w') as f:
                f.write(time_stamp_record)
        else:
            _x0, _x1, _y0, _y1, _w, _h = self.get_wh()

            while self._recording:
                try:
                    _current_img = self._img_queue.get(block=True, timeout=0.04)
                except queue.Empty:
                    continue
                if _current_img is not None:
                    _img = _current_img[1]
                    if self._value["ROI"] is not None:
                        _img = _img[_y0:_y1, _x0:_x1, :]
                    self.current_img = _img
                    self._ready = True

    def _update_window(self):
        while self._recording:
            if self._ready:
                self._window.img_updated.emit(self.current_img)
            time.sleep(0.03)
        self._window.to_close.emit()

    def stop(self):
        self._recording = False
