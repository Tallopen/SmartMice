# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:46
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from variables.MCam import CAMERA_VALUES
import copy
import cv2
import numpy as np
import time


class MyCamera(QThread):

    img_change = pyqtSignal()

    def __init__(self, value):
        super(MyCamera, self).__init__()

        self.cam = cv2.VideoCapture(value["ID"])
        self.cam.set(cv2.CAP_PROP_FPS, 30)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        for key, value in value.items():
            if key in CAMERA_VALUES:
                self.cam.set(CAMERA_VALUES[key][2], value)
        self.cam.read()

        self.img = None

    def run(self):
        while self.cam.isOpened():
            _img = self.cam.read()
            if _img[0]:
                rgb_img = cv2.cvtColor(_img[1], cv2.COLOR_BGR2RGB)
                self.img = rgb_img
                self.img_change.emit()
            else:
                self.img = None
            time.sleep(0.04)

    def destroy(self):
        self.cam.release()
        self.img = None


class Canvas(QGraphicsView):
    resized = pyqtSignal()
    mouse_move = pyqtSignal(int, int)
    mouse_wheel_event = pyqtSignal(int)
    middle_mouse_move = pyqtSignal(int, int)
    left_mouse_click = pyqtSignal(int, int)
    left_mouse_press = pyqtSignal(int, int)
    left_mouse_move = pyqtSignal(int, int)
    right_mouse_click = pyqtSignal(int, int)

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

        self.centerX = 0
        self.centerY = 0
        self.scale = 1

    def coor2pix(self, x, y):
        return round((x - self.centerX) * self.scale + self.width() / 2), round(self.height() / 2 - (y - self.centerY) * self.scale)

    def pix2coor(self, x, y):
        return round((x - self.width() / 2) / self.scale + self.centerX, 2), round((self.height() / 2 - y) / self.scale + self.centerY, 2)

    def draw_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.q_pix_item.setPixmap(self.pixmap)

    def wheelEvent(self, a0):
        if self.ready:
            self.mouse_wheel_event.emit(a0.angleDelta().y())
        return super(Canvas, self).wheelEvent(a0)

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
        if self.ready:
            if a0.buttons() == Qt.MouseButton.LeftButton:
                self.left_mouse_move.emit(a0.position().x()-4, a0.position().y()-4)
            elif a0.buttons() == Qt.MouseButton.MiddleButton:
                self.middle_mouse_move.emit(a0.position().x()-self.prev_mouse_pos.x(), a0.position().y()-self.prev_mouse_pos.y())
            else:
                self.mouse_move.emit(a0.position().x() - 4, a0.position().y() - 4)
        self.prev_mouse_pos = a0.position()
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
            if self.pressed_button == Qt.MouseButton.RightButton:
                self.right_mouse_click.emit(a0.position().x() - 4, a0.position().y() - 4)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        return super(Canvas, self).mouseReleaseEvent(a0)


class TrackerEditor(QDialog):

    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(TrackerEditor, self).__init__(*args)

        # find all camera variables and add to combo box
        self.Cams = dict()
        for var_name, var_content in ass.items():
            if var_content["type"] == "MCam":
                self.Cams[var_name] = var_content["value"]

        self._value = value

        # below is gui-related
        if not self.objectName():
            self.setObjectName(u"Dialog")
        self.resize(950, 670)
        self.setWindowTitle("Tracker Editor")
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ResetButton = QToolButton(self)
        self.ResetButton.setObjectName(u"ResetButton")

        self.horizontalLayout.addWidget(self.ResetButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.GeometricView = Canvas(self)
        self.GeometricView.setObjectName(u"GeometricView")

        self.gridLayout_3.addWidget(self.GeometricView, 1, 1, 1, 1)

        self.label_11 = QLabel(self)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_3.addWidget(self.label_11, 0, 1, 1, 1)

        self.groupBox = QGroupBox(self)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(75, 0))

        self.horizontalLayout_4.addWidget(self.label)

        self.CamVariablesCombo = QComboBox(self.groupBox)
        self.CamVariablesCombo.setObjectName(u"CamVariablesCombo")
        self.CamVariablesCombo.setMinimumSize(QSize(250, 0))

        for camVarName in self.Cams.keys():
            self.CamVariablesCombo.addItem(camVarName)

        self.horizontalLayout_4.addWidget(self.CamVariablesCombo)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.CameraTransform = QLabel(self.groupBox)
        self.CameraTransform.setObjectName(u"CameraTransform")

        self.verticalLayout_4.addWidget(self.CameraTransform)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(75, 16777215))

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.CamWLE = QLineEdit(self.groupBox)
        self.CamWLE.setObjectName(u"CamWLE")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CamWLE.sizePolicy().hasHeightForWidth())
        self.CamWLE.setSizePolicy(sizePolicy)
        self.CamWLE.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.CamWLE, 2, 1, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(75, 16777215))

        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)

        self.CamHLE = QLineEdit(self.groupBox)
        self.CamHLE.setObjectName(u"CamHLE")
        sizePolicy.setHeightForWidth(self.CamHLE.sizePolicy().hasHeightForWidth())
        self.CamHLE.setSizePolicy(sizePolicy)
        self.CamHLE.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.CamHLE, 3, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(75, 16777215))

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMaximumSize(QSize(75, 16777215))

        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)

        self.CamXLE = QLineEdit(self.groupBox)
        self.CamXLE.setObjectName(u"CamXLE")
        sizePolicy.setHeightForWidth(self.CamXLE.sizePolicy().hasHeightForWidth())
        self.CamXLE.setSizePolicy(sizePolicy)
        self.CamXLE.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.CamXLE, 0, 1, 1, 1)

        self.CamYLE = QLineEdit(self.groupBox)
        self.CamYLE.setObjectName(u"CamYLE")
        sizePolicy.setHeightForWidth(self.CamYLE.sizePolicy().hasHeightForWidth())
        self.CamYLE.setSizePolicy(sizePolicy)
        self.CamYLE.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.CamYLE, 1, 1, 1, 1)

        self.verticalLayout_4.addLayout(self.gridLayout)

        self.gridLayout_3.addWidget(self.groupBox, 2, 0, 1, 1)

        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)

        self.CameraView = Canvas(self)
        self.CameraView.setObjectName(u"CameraView")

        self.gridLayout_3.addWidget(self.CameraView, 1, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_15 = QLabel(self.groupBox_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setMinimumSize(QSize(150, 0))
        self.label_15.setMaximumSize(QSize(300, 16777215))

        self.horizontalLayout_5.addWidget(self.label_15)

        self.CurrentPointIDLabel = QLabel(self.groupBox_2)
        self.CurrentPointIDLabel.setObjectName(u"CurrentPointIDLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.CurrentPointIDLabel.sizePolicy().hasHeightForWidth())
        self.CurrentPointIDLabel.setSizePolicy(sizePolicy1)

        self.horizontalLayout_5.addWidget(self.CurrentPointIDLabel)

        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.line_2 = QFrame(self.groupBox_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_6.addWidget(self.line_2)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_6.addWidget(self.label_10)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.CamPtXLE = QLineEdit(self.groupBox_2)
        self.CamPtXLE.setObjectName(u"CamPtXLE")
        sizePolicy.setHeightForWidth(self.CamPtXLE.sizePolicy().hasHeightForWidth())
        self.CamPtXLE.setSizePolicy(sizePolicy)
        self.CamPtXLE.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.CamPtXLE, 0, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy2)
        self.label_8.setMaximumSize(QSize(75, 16777215))

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 1, 0, 1, 1)

        self.CamPtYLE = QLineEdit(self.groupBox_2)
        self.CamPtYLE.setObjectName(u"CamPtYLE")
        sizePolicy.setHeightForWidth(self.CamPtYLE.sizePolicy().hasHeightForWidth())
        self.CamPtYLE.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.CamPtYLE, 1, 1, 1, 1)

        self.verticalLayout_6.addLayout(self.gridLayout_2)

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_6.addWidget(self.label_12)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(75, 0))

        self.gridLayout_4.addWidget(self.label_13, 0, 0, 1, 1)

        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(75, 0))

        self.gridLayout_4.addWidget(self.label_14, 1, 0, 1, 1)

        self.GeoPtXLE = QLineEdit(self.groupBox_2)
        self.GeoPtXLE.setObjectName(u"GeoPtXLE")

        self.gridLayout_4.addWidget(self.GeoPtXLE, 0, 1, 1, 1)

        self.GeoPtYLE = QLineEdit(self.groupBox_2)
        self.GeoPtYLE.setObjectName(u"GeoPtYLE")

        self.gridLayout_4.addWidget(self.GeoPtYLE, 1, 1, 1, 1)

        self.verticalLayout_6.addLayout(self.gridLayout_4)

        self.verticalLayout_3.addLayout(self.verticalLayout_6)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setText("Bin Threshold:")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.horizontalSlider = QSlider(self.groupBox_2)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMaximum(256)
        self.horizontalSlider.setPageStep(16)
        self.horizontalSlider.setValue(128)
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.horizontalSlider.setInvertedAppearance(False)
        self.horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.horizontalSlider.setTickInterval(16)

        self.horizontalLayout_6.addWidget(self.horizontalSlider)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.gridLayout_3.addWidget(self.groupBox_2, 2, 1, 1, 1)

        self.horizontalLayout_3.addLayout(self.gridLayout_3)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_2.addWidget(self.buttonBox)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.ResetButton.setText(QCoreApplication.translate("Dialog", u"Reset", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"Geometric View", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Camera", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Variable:", None))
        self.CameraTransform.setText(QCoreApplication.translate("Dialog", u"Camera Transform", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Height", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Y", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Width", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"X", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Camera View", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"GroupBox", None))
        self.label_15.setText(QCoreApplication.translate("Dialog", u"Current Point Pair ID", None))
        self.CurrentPointIDLabel.setText(QCoreApplication.translate("Dialog", u"None", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"Camera Point Property", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"X", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"Y", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"Geometric Point Property", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"X", None))
        self.label_14.setText(QCoreApplication.translate("Dialog", u"Y", None))

        self.CameraView.middle_mouse_move.connect(self.camera_view_mouse_move)
        self.CameraView.mouse_wheel_event.connect(self.camera_view_mouse_wheel)
        self.CameraView.left_mouse_click.connect(self.camera_view_left_mouse_click)
        self.CameraView.left_mouse_move.connect(self.camera_view_left_mouse_move)
        self.CameraView.right_mouse_click.connect(self.camera_view_right_mouse_click)
        self.GeometricView.middle_mouse_move.connect(self.geom_view_mouse_move)
        self.GeometricView.mouse_wheel_event.connect(self.geom_view_mouse_wheel)
        self.GeometricView.left_mouse_click.connect(self.geom_view_left_mouse_click)
        self.GeometricView.left_mouse_move.connect(self.geom_view_left_mouse_move)
        self.GeometricView.right_mouse_click.connect(self.geom_view_right_mouse_click)

        # load value
        if self._value["cam"]:
            self.CamVariablesCombo.setCurrentText(self._value["cam"])

        self.CamVariablesCombo.currentTextChanged.connect(self.update_camera)

        self.camBoundingBox = self._value["cam-bbox"]
        self.CamXLE.setText(str(self.camBoundingBox[0]))
        self.CamYLE.setText(str(self.camBoundingBox[1]))
        self.CamWLE.setText(str(self.camBoundingBox[2]))
        self.CamHLE.setText(str(self.camBoundingBox[3]))

        self.CamXLE.textEdited.connect(self.camera_data_renew)
        self.CamYLE.textEdited.connect(self.camera_data_renew)
        self.CamWLE.textEdited.connect(self.camera_data_renew)
        self.CamHLE.textEdited.connect(self.camera_data_renew)

        self.CamPtXLE.textEdited.connect(self.pair_point_renew)
        self.CamPtYLE.textEdited.connect(self.pair_point_renew)
        self.GeoPtXLE.textEdited.connect(self.pair_point_renew)
        self.GeoPtYLE.textEdited.connect(self.pair_point_renew)

        # initialize threshold setting
        self.horizontalSlider.setValue(self._value["thresh"])
        self.horizontalSlider.valueChanged.connect(self.set_bin_thresh)

        # initialize camera
        self.currentCamera = None
        self.vd = None
        self.update_camera()

        self.CameraView.ready = True
        self.GeometricView.ready = True
        self.selected_pt = None
        self.change_selected_pair_point(None)

        self.neglect_le_change = False

    def set_bin_thresh(self, *args):
        self._value["thresh"] = self.horizontalSlider.value()

    def camera_data_renew(self, *args):
        if int(self.CamWLE.text()) < 10:
            self.CamWLE.setText('10')
        if int(self.CamHLE.text()) < 10:
            self.CamHLE.setText('10')
        self._value["cam-bbox"] = [
            int(self.CamXLE.text()),
            int(self.CamYLE.text()),
            int(self.CamWLE.text()),
            int(self.CamHLE.text()),
        ]
        self.camBoundingBox = self._value["cam-bbox"]
        self.update_canvas()
        self.neglect_le_change = True
        self.CamXLE.setText(str(self.camBoundingBox[0]))
        self.CamYLE.setText(str(self.camBoundingBox[1]))
        self.CamWLE.setText(str(self.camBoundingBox[2]))
        self.CamHLE.setText(str(self.camBoundingBox[3]))
        self.neglect_le_change = False

    def pair_point_renew(self, *args):
        if self.selected_pt is not None:
            try:
                self._value["geo-ser"]["pt-closed"][self.selected_pt] = [
                    float(self.CamPtXLE.text()),
                    float(self.CamPtYLE.text()),
                    float(self.GeoPtXLE.text()),
                    float(self.GeoPtYLE.text())
                ]
                self.update_canvas()
            except ValueError:
                pass

    def change_selected_pair_point(self, point_id):
        self.selected_pt = point_id
        self.CurrentPointIDLabel.setText(str(self.selected_pt))
        if self.selected_pt is None:
            self.CamPtXLE.setEnabled(False)
            self.GeoPtXLE.setEnabled(False)
            self.CamPtYLE.setEnabled(False)
            self.GeoPtYLE.setEnabled(False)
        else:
            self.CamPtXLE.setEnabled(True)
            self.GeoPtXLE.setEnabled(True)
            self.CamPtYLE.setEnabled(True)
            self.GeoPtYLE.setEnabled(True)
            self.neglect_le_change = True
            self.CamPtXLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][0]))
            self.CamPtYLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][1]))
            self.GeoPtXLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][2]))
            self.GeoPtYLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][3]))
            self.neglect_le_change = False

    def camera_view_left_mouse_move(self, x, y):
        self.neglect_le_change = True
        threshold = 2048 / self.CameraView.scale ** 2
        if self.selected_pt is not None:
            cx, cy = self.CameraView.pix2coor(x, y)
            if (self._value["geo-ser"]["pt-closed"][self.selected_pt][1] - cy) ** 2 + (self._value["geo-ser"]["pt-closed"][self.selected_pt][0] - cx) ** 2 <= threshold:
                self._value["geo-ser"]["pt-closed"][self.selected_pt][:2] = [cx, cy]
                self.CamPtXLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][0]))
                self.CamPtYLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][1]))
            else:
                self.camera_view_left_mouse_click(x, y)
        self.update_canvas()
        self.neglect_le_change = False

    def geom_view_left_mouse_move(self, x, y):
        self.neglect_le_change = True
        threshold = 2048 / self.GeometricView.scale ** 2
        if self.selected_pt is not None:
            cx, cy = self.GeometricView.pix2coor(x, y)
            if (self._value["geo-ser"]["pt-closed"][self.selected_pt][3] - cy) ** 2 + (self._value["geo-ser"]["pt-closed"][self.selected_pt][2] - cx) ** 2 <= threshold:
                self._value["geo-ser"]["pt-closed"][self.selected_pt][2:] = [cx, cy]
                self.GeoPtXLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][2]))
                self.GeoPtYLE.setText(str(self._value["geo-ser"]["pt-closed"][self.selected_pt][3]))
            else:
                self.geom_view_left_mouse_click(x, y)
        self.update_canvas()
        self.neglect_le_change = False

    def camera_view_left_mouse_click(self, x, y):
        cx, cy = self.CameraView.pix2coor(x, y)
        selected_pt = None
        threshold = 128 / self.CameraView.scale ** 2
        for ptid, pt in enumerate(self._value["geo-ser"]["pt-closed"]):
            if (pt[1] - cy) ** 2 + (pt[0] - cx) ** 2 <= threshold:
                selected_pt = ptid
        self.change_selected_pair_point(selected_pt)
        self.update_canvas()

    def geom_view_left_mouse_click(self, x, y):
        cx, cy = self.GeometricView.pix2coor(x, y)
        selected_pt = None
        threshold = 128 / self.GeometricView.scale ** 2
        for ptid, pt in enumerate(self._value["geo-ser"]["pt-closed"]):
            if (pt[3] - cy) ** 2 + (pt[2] - cx) ** 2 <= threshold:
                selected_pt = ptid
        self.change_selected_pair_point(selected_pt)
        self.update_canvas()

    def camera_view_right_mouse_click(self, x, y):
        self.CurrentPointIDLabel.setText(str(self.selected_pt))
        x, y = self.CameraView.pix2coor(x, y)
        self._value["geo-ser"]["pt-closed"].append([x, y, self.GeometricView.centerX, self.GeometricView.centerY])

        self.change_selected_pair_point(len(self._value["geo-ser"]["pt-closed"]) - 1)
        self.update_canvas()

    def geom_view_right_mouse_click(self, x, y):
        self.CurrentPointIDLabel.setText(str(self.selected_pt))
        x, y = self.GeometricView.pix2coor(x, y)
        self._value["geo-ser"]["pt-closed"].append([self.CameraView.centerX, self.CameraView.centerY, x, y])

        self.change_selected_pair_point(len(self._value["geo-ser"]["pt-closed"]) - 1)
        self.update_canvas()

    def geom_view_mouse_wheel(self, delta_y):
        delta_scale = 1.1 ** (delta_y / 60)
        self.GeometricView.scale /= delta_scale
        self.GeometricView.centerX *= delta_scale
        self.GeometricView.centerY *= delta_scale

    def camera_view_mouse_wheel(self, delta_y):
        delta_scale = 1.1 ** (delta_y / 60)
        self.CameraView.scale /= delta_scale
        self.CameraView.centerX *= delta_scale
        self.CameraView.centerY *= delta_scale

    def geom_view_mouse_move(self, delta_x, delta_y):
        self.GeometricView.centerX -= delta_x / self.GeometricView.scale
        self.GeometricView.centerY += delta_y / self.GeometricView.scale
        self.update_canvas()

    def camera_view_mouse_move(self, delta_x, delta_y):
        self.CameraView.centerX -= delta_x / self.CameraView.scale
        self.CameraView.centerY += delta_y / self.CameraView.scale
        self.update_canvas()

    def update_camera(self, *args):
        if self.vd:
            try:
                self.vd.img_change.disconnect()
            except:
                pass
            self.vd.destroy()
        self.currentCamera = None
        if self.CamVariablesCombo.currentText():
            self.currentCamera = self.Cams[self.CamVariablesCombo.currentText()]
            self.vd = MyCamera(self.currentCamera)
            self.vd.img_change.connect(self.update_canvas)
            self.vd.start()

    def update_canvas(self):
        img = self.vd.img
        if img is not None:
            # crop by ROI
            if self.currentCamera["ROI"]:
                _w = img.shape[1]
                _h = img.shape[0]
                _x0 = max(self.currentCamera["ROI"][0][0], 0)
                _x1 = min(self.currentCamera["ROI"][1][0], _w - 1)
                _y0 = max(self.currentCamera["ROI"][0][1], 0)
                _y1 = min(self.currentCamera["ROI"][1][1], _h - 1)
                img = img[_y0:_y1, _x0:_x1, :]

            # create a new RGB img
            blank = np.zeros([self.CameraView.height() - 2, self.CameraView.width() - 2, 3], np.uint8)
            [_cx, _cy] = self.CameraView.coor2pix(self.camBoundingBox[0], self.camBoundingBox[1])

            _cw = round(self.camBoundingBox[2] * self.CameraView.scale / 2)
            _ch = round(self.camBoundingBox[3] * self.CameraView.scale / 2)
            img2 = cv2.resize(img, [_cw*2, _ch*2])

            if 0 <= _cx + _cw and _cx - _cw < self.CameraView.width() - 2 and 0 <= _cy + _ch and _cy - _ch < self.CameraView.height() - 2:
                # crop img if it exceeds border
                if _cx - _cw < 0:
                    img2 = img2[:, (_cw-_cx):]
                if _cx + _cw > self.CameraView.width() - 2:
                    img2 = img2[:, :(self.CameraView.width() - 2 - max(_cx - _cw, 0))]
                if _cy - _ch < 0:
                    img2 = img2[(_ch - _cy):, :]
                if _cy + _ch > self.CameraView.height() - 2:
                    img2 = img2[:(self.CameraView.height() - 2 - max(_cy - _ch, 0)), :]
                blank[max((_cy - _ch), 0):(_cy + _ch), max((_cx - _cw), 0):(_cx + _cw)] = img2

            ptco = []

            for ptid, pt in enumerate(self._value["geo-ser"]["pt-closed"]):
                ptco.append(self.CameraView.coor2pix(pt[0], pt[1]))

            for ptid in range(len(ptco)):
                if ptid:
                    cv2.line(blank, ptco[ptid-1], ptco[ptid], [255, 150, 150], 2)
                else:
                    cv2.line(blank, ptco[0], ptco[-1], [255, 150, 150], 2)

            for ptid, pt in enumerate(ptco):
                if ptid != self.selected_pt:
                    cv2.circle(blank, pt, 4, [255, 0, 0], 1)
                else:
                    cv2.circle(blank, pt, 4, [255, 255, 0], 1)

            pix_map = QPixmap(QImage(blank.data, blank.shape[1], blank.shape[0], blank.shape[1]*blank.shape[2], QImage.Format.Format_RGB888)).scaled(self.CameraView.width() - 2, self.CameraView.height() - 2)

            self.CameraView.draw_pixmap(pix_map)

            blank2 = np.zeros([self.GeometricView.height() - 2, self.GeometricView.width() - 2, 3], np.uint8) * 255

            # transform first if possible
            # triangularize source & destination points
            src_points = []
            dptco = []
            for ptid, pt in enumerate(self._value["geo-ser"]["pt-closed"]):
                _x = img.shape[1] * ((pt[0] - self._value["cam-bbox"][0]) / self._value["cam-bbox"][2] + 0.5)
                _y = img.shape[0] * ((self._value["cam-bbox"][1] - pt[1]) / self._value["cam-bbox"][3] + 0.5)
                src_points.append([_x, _y])
                dptco.append(self.GeometricView.coor2pix(pt[2], pt[3]))

            src_points = np.array(src_points, dtype=np.float32)
            dst_points = np.array(dptco, dtype=np.float32)

            rect = (-500, -500, 1500, 1500)
            subdiv = cv2.Subdiv2D(rect)
            for p in dst_points:
                subdiv.insert((int(p[0]), int(p[1])))
            triangles = subdiv.getTriangleList()

            for triangle in triangles:
                pt1, pt2, pt3 = triangle.reshape(3, 2)
                vertex_indices = np.array([subdiv.findNearest(pt)[0] for pt in (pt1, pt2, pt3)], dtype=int)

                H = cv2.getAffineTransform(src_points[vertex_indices - 4], dst_points[vertex_indices - 4])
                warped_triangle = cv2.warpAffine(img, H, (blank2.shape[1], blank2.shape[0]))
                mask = np.zeros_like(blank2)
                roi_corners = np.array([pt1, pt2, pt3], dtype=np.int16)
                cv2.fillPoly(mask, [np.int32(roi_corners)], (1.0, 1.0, 1.0), 16, 0)
                blank2 += warped_triangle * mask

            # binarize by thresholding
            blank3 = cv2.cvtColor(blank2, cv2.COLOR_RGB2GRAY)
            _, blank3 = cv2.threshold(blank3, self._value["thresh"], 255, cv2.THRESH_BINARY)
            blank3 = cv2.bitwise_not(blank3)
            if len(dst_points):
                mask = np.zeros_like(blank3)
                cv2.fillPoly(mask, [np.int32(dst_points)-1], (1.0, 1.0, 1.0), 16, 0)
                blank3 *= mask
            blank3 = cv2.morphologyEx(blank3, cv2.MORPH_CLOSE, np.ones([4, 4], np.uint8))
            blank3 = cv2.morphologyEx(blank3, cv2.MORPH_OPEN, np.ones([4, 4], np.uint8))

            # just for test
            blank2 = cv2.cvtColor(blank3, cv2.COLOR_GRAY2RGB)

            # get connected components
            _, _, stats, centroids = cv2.connectedComponentsWithStats(blank3, connectivity=8)

            if len(dst_points) and stats.shape[0] > 1:
                max_component_id = np.argmax(stats[1:, 4]) + 1

                cv2.circle(blank2, list(np.int32(np.round(centroids[max_component_id, :]))), 5, [255, 128, 0], 4)

            # draw geometry outline
            for ptid in range(len(dptco)):
                if ptid:
                    cv2.line(blank2, dptco[ptid-1], dptco[ptid], [255, 150, 150], 2)
                else:
                    cv2.line(blank2, dptco[0], dptco[-1], [255, 150, 150], 2)

            for ptid, pt in enumerate(dptco):
                if ptid != self.selected_pt:
                    cv2.circle(blank2, pt, 4, [255, 0, 0], 1)
                else:
                    cv2.circle(blank2, pt, 4, [255, 255, 0], 1)

            pix_map = QPixmap(QImage(blank2.data, blank2.shape[1], blank2.shape[0], blank2.shape[1]*blank2.shape[2], QImage.Format.Format_RGB888)).scaled(self.GeometricView.width() - 2, self.GeometricView.height() - 2)

            self.GeometricView.draw_pixmap(pix_map)

    def exec(self):

        _v = super(TrackerEditor, self).exec()

        try:
            self.vd.destroy()
        except:
            pass

        if _v:
            return copy.deepcopy(self._value), _v

        return None, _v


class MTracker:

    requirements = {
        "variable": True,
        "runner": False,
        "interface": False
    }
    value_editor = TrackerEditor
    filter_func = dict

    gui_param = {
        "menu_name": "Naive Tracker",
        "group": "Math"
    }
    template_dict = {
        "type": "MTracker",

        "name": None,
        "value": {
            "cam": None,
            "cam-bbox": [0, 0, 1280, 720],
            "geo-ser": {
                "pt-closed": []   # must in pairs: (camXY, geoXY)
            },   # closed, point series-formed lines
            "thresh": 127
        },

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
