# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com


import copy
import math
import threading
import time

import socket

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import *
from PyQt6.QtWidgets import *
from PyQt6 import QtOpenGL
import serial
from serial.tools import list_ports

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import cv2

import numpy as np
import quaternion


# note: you may want to check network configuration of your computer to ensure your local ip
LOCAL_IP = "127.0.0.1"

# make sure this port below is available
BALL_UDP_PORT = 4514


def rotate_vector_2d(x, y, theta):
    return f"{round(x*np.cos(theta) - y*np.sin(theta), 3)},{round(x*np.sin(theta) + y*np.cos(theta), 3)}"


class MyThread(QThread):

    def __init__(self, target):

        super(QThread, self).__init__()
        self._foo = target

    def run(self):
        self._foo()


class VRBallVisualizer(QOpenGLWidget):

    def __init__(self, *args, **kwargs):
        super(VRBallVisualizer, self).__init__(*args, **kwargs)

        self._x = 8
        self._y = 0
        self._z = 0

        self.radius = 2

        self.main_axis_dots = []
        for angle_id in range(600):
            _x = self.radius * math.cos(angle_id * math.pi / 300)
            _y = self.radius * math.sin(angle_id * math.pi / 300)
            self.main_axis_dots.append([_x, _y, 0])
            self.main_axis_dots.append([_y, 0, _x])
            self.main_axis_dots.append([0, _x, _y])
        self.main_axis_dots = np.array(self.main_axis_dots, dtype=float)

        self.latitude_dots = []
        for h in range(1, 8):
            sub_radius = self.radius * math.sqrt(1 - (h/8) ** 2)
            for angle_id in range(600):
                _x = sub_radius * math.cos(angle_id * math.pi / 300)
                _y = sub_radius * math.sin(angle_id * math.pi / 300)

                self.latitude_dots.append([_x, _y, h / 8 * self.radius])
                self.latitude_dots.append([_x, _y, -h / 8 * self.radius])
        self.latitude_dots = np.array(self.latitude_dots, dtype=float)

        self.x_axis_dots = []
        for pt_id in range(1, 90):
            self.x_axis_dots.append([0, 0, (pt_id-40)/40*self.radius])
        self.x_axis_dots = np.array(self.x_axis_dots, dtype=float)

        self.triangle_dots = np.array([
            [-0.1*self.radius, 0, 1.25*self.radius],
            [0.1*self.radius, 0, 1.25*self.radius],
            [0, 0, 1.5*self.radius],
            [0, -0.1*self.radius, 1.25*self.radius],
            [0, 0.1*self.radius, 1.25*self.radius],
            [0, 0, 1.5*self.radius],
        ], dtype=float)

        self.q = quaternion.quaternion(1, 0, 0, 0)

    def initializeGL(self) -> None:
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

    def paintGL(self) -> None:
        try:
            if self.q.norm() > 0:
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                gluLookAt(8, 0, 0, 0, 0, 0, 0, 1, 0)

                _main_axis_dots = quaternion.rotate_vectors(self.q, self.main_axis_dots)
                _latitude_dots = quaternion.rotate_vectors(self.q, self.latitude_dots)
                _x_axis_dots = quaternion.rotate_vectors(self.q, self.x_axis_dots)
                _triangle_dots = quaternion.rotate_vectors(self.q, self.triangle_dots)

                glColor3f(0.5, 1.0, 1.0)
                glPointSize(3)

                glBegin(GL_POINTS)
                for dot in _main_axis_dots:
                    glVertex3f(-dot[1], -dot[2], -dot[0])
                glEnd()

                glPointSize(1)
                glColor3f(1.0, 1.0, 1.0)
                glBegin(GL_POINTS)
                for dot in _latitude_dots:
                    glVertex3f(-dot[1], -dot[2], -dot[0])
                glEnd()

                glColor3f(0.3, 0.3, 1.0)
                glPointSize(4)
                glBegin(GL_POINTS)
                for dot in _x_axis_dots:
                    glVertex3f(-dot[1], -dot[2], -dot[0])
                glEnd()

                glColor3f(0.3, 1.0, 0.3)
                glBegin(GL_TRIANGLES)
                for dot in _triangle_dots:
                    glVertex3f(-dot[1], -dot[2], -dot[0])
                glEnd()
        except Exception as e:
            pass

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 0.01, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(8, 0, 0, 0, 0, 0, 0, 1, 0)

    def set_view_point(self, _q):
        self.q = _q
        self.update()


class VRBallEditor(QDialog):

    # noinspection PyArgumentList
    def __init__(self, var_name, value: dict, ass: dict, *args):
        super(VRBallEditor, self).__init__()

        self.setWindowTitle("VR ball pose detection settings for "+var_name)

        # find all camera variables and add to combo box
        self.Cams = dict()
        for var_name, var_content in ass.items():
            if var_content["type"] == "MCam":
                self.Cams[var_name] = var_content["value"]

        self.resize(700, 500)
        # below are codes generating the GUI
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.label_2 = QLabel(self)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.pitchScalingSpin = QDoubleSpinBox(self)
        self.pitchScalingSpin.setMaximum(1000)
        self.pitchScalingSpin.setMinimum(-1000)
        self.pitchScalingSpin.setSingleStep(0.01)
        self.pitchScalingSpin.setValue(value["pitch-scale"])

        self.horizontalLayout_3.addWidget(self.pitchScalingSpin)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.label_3 = QLabel(self)

        self.horizontalLayout_4.addWidget(self.label_3)

        self.rollScalingSpin = QDoubleSpinBox(self)
        self.rollScalingSpin.setMaximum(1000)
        self.rollScalingSpin.setMinimum(-1000)
        self.rollScalingSpin.setSingleStep(0.01)
        self.rollScalingSpin.setValue(value["roll-scale"])

        self.horizontalLayout_4.addWidget(self.rollScalingSpin)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.label_6 = QLabel(self)

        self.horizontalLayout_5.addWidget(self.label_6)

        self.yawScalingSpin = QDoubleSpinBox(self)
        self.yawScalingSpin.setEnabled(False)
        self.yawScalingSpin.setMaximum(1000)
        self.yawScalingSpin.setMinimum(-1000)
        self.yawScalingSpin.setSingleStep(0.01)
        self.yawScalingSpin.setValue(value["yaw-scale"])

        self.horizontalLayout_5.addWidget(self.yawScalingSpin)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.rotateLayout = QHBoxLayout()
        self.rotateLabel = QLabel(self)

        self.rotateLayout.addWidget(self.rotateLabel)

        self.rotateSpin = QDoubleSpinBox(self)
        self.rotateSpin.setMaximum(360)
        self.rotateSpin.setMinimum(0)
        self.rotateSpin.setSingleStep(10)
        self.rotateSpin.setValue(value.get("rotate", 0))

        self.rotateLayout.addWidget(self.rotateSpin)

        self.verticalLayout_2.addLayout(self.rotateLayout)

        self.poseResetButton = QPushButton(self)
        self.poseResetButton.setMinimumSize(QSize(200, 0))

        self.verticalLayout_2.addWidget(self.poseResetButton)

        self.label_4 = QLabel(self)

        self.verticalLayout_2.addWidget(self.label_4)

        self.dfCombo = QComboBox(self)

        for _item in ["yaw", "pitch - roll", "pitch - yaw", "yaw - pitch - roll"]:
            self.dfCombo.addItem(_item)

        self.verticalLayout_2.addWidget(self.dfCombo)

        self.line = QFrame(self)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.allowRuntimeCorrectionCheckBox = QCheckBox("Runtime Correction")
        self.verticalLayout_2.addWidget(self.allowRuntimeCorrectionCheckBox)

        self.horizontalLayout_6 = QHBoxLayout()
        self.label_8 = QLabel("Camera:   ")
        self.cameraCombo = QComboBox(self)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.cameraCombo.setSizePolicy(sizePolicy2)

        for camVarName in self.Cams.keys():
            self.cameraCombo.addItem(camVarName)

        self.horizontalLayout_6.addWidget(self.label_8)
        self.horizontalLayout_6.addWidget(self.cameraCombo)
        self.verticalLayout_2.addItem(self.horizontalLayout_6)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.label_5 = QLabel(self)

        self.verticalLayout_2.addWidget(self.label_5)

        self.baudRateCombo = QComboBox(self)
        for _bd_rate in ["4800", "9600", "14400", "19200", "28800", "38400", "57600", "115200"]:
            self.baudRateCombo.addItem(_bd_rate)
        self.baudRateCombo.setEnabled(False)

        self.verticalLayout_2.addWidget(self.baudRateCombo)

        self.line_2 = QFrame(self)
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

        self.label_22 = QLabel(self)

        self.verticalLayout_2.addWidget(self.label_22)

        self.portCombo = QComboBox(self)

        self.verticalLayout_2.addWidget(self.portCombo)

        self.scanPort = QPushButton(self)
        self.scanPort.clicked.connect(self.scan)

        self.verticalLayout_2.addWidget(self.scanPort)

        self.connectToPort = QPushButton(self)
        self.connectToPort.setEnabled(False)

        self.verticalLayout_2.addWidget(self.connectToPort)

        self.disconnectFromPort = QPushButton(self)
        self.disconnectFromPort.setEnabled(False)

        self.verticalLayout_2.addWidget(self.disconnectFromPort)

        self.portMessageBrowser = QTextBrowser(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.portMessageBrowser.sizePolicy().hasHeightForWidth())
        self.portMessageBrowser.setSizePolicy(sizePolicy)
        self.portMessageBrowser.setMinimumSize(QSize(0, 150))
        self.portMessageBrowser.setMaximumSize(QSize(16777215, 150))

        self.verticalLayout_2.addWidget(self.portMessageBrowser)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.label = QLabel(self)

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.ballPoseWidget = VRBallVisualizer(self)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ballPoseWidget.sizePolicy().hasHeightForWidth())
        self.ballPoseWidget.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.ballPoseWidget)

        self.label_21 = QLabel(self)

        self.verticalLayout_3.addWidget(self.label_21)

        self.line_4 = QFrame(self)
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_4)

        self.gridLayout = QGridLayout()
        self.label_9 = QLabel(self)
        self.gridLayout.addWidget(self.label_9, 0, 3, 1, 1)
        self.rotAxisLabel = QLabel(self)
        self.gridLayout.addWidget(self.rotAxisLabel, 0, 1, 1, 1)
        self.label_12 = QLabel(self)
        self.gridLayout.addWidget(self.label_12, 2, 0, 1, 1)
        self.label_14 = QLabel(self)
        self.gridLayout.addWidget(self.label_14, 1, 3, 1, 1)
        self.HDOffsetLabel = QLabel(self)
        self.gridLayout.addWidget(self.HDOffsetLabel, 2, 1, 1, 1)
        self.placeOffsetLabel = QLabel(self)
        self.gridLayout.addWidget(self.placeOffsetLabel, 3, 1, 1, 1)
        self.label_7 = QLabel(self)
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.label_17 = QLabel(self)
        self.gridLayout.addWidget(self.label_17, 2, 3, 1, 1)
        self.pitchSpeedLabel = QLabel(self)
        self.gridLayout.addWidget(self.pitchSpeedLabel, 1, 4, 1, 1)
        self.label_19 = QLabel(self)
        self.gridLayout.addWidget(self.label_19, 3, 0, 1, 1)
        self.rotAngleLabel = QLabel(self)
        self.gridLayout.addWidget(self.rotAngleLabel, 1, 1, 1, 1)
        self.rollSpeedLabel = QLabel(self)
        self.gridLayout.addWidget(self.rollSpeedLabel, 2, 4, 1, 1)
        self.label_11 = QLabel(self)
        self.gridLayout.addWidget(self.label_11, 1, 0, 1, 1)
        self.yawSpeedLabel = QLabel(self)
        self.gridLayout.addWidget(self.yawSpeedLabel, 0, 4, 1, 1)
        self.line_3 = QFrame(self)
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_3, 0, 2, 1, 1)

        self.line_5 = QFrame(self)
        self.line_5.setFrameShape(QFrame.Shape.VLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_5, 1, 2, 1, 1)

        self.line_6 = QFrame(self)
        self.line_6.setFrameShape(QFrame.Shape.VLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_6, 2, 2, 1, 1)

        self.line_7 = QFrame(self)
        self.line_7.setFrameShape(QFrame.Shape.VLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_7, 3, 2, 1, 1)

        self.verticalLayout_3.addLayout(self.gridLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_3.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.dfCombo.setCurrentIndex(1)
        self.baudRateCombo.setCurrentIndex(10)

        self.label_2.setText(QCoreApplication.translate("Form", u"Pitch scaling:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Roll scaling:", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Yaw scaling:", None))
        self.rotateLabel.setText("Rotate:")
        self.poseResetButton.setText(QCoreApplication.translate("Form", u"Reset Ball Pose Estimation", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Degree of Freedom:", None))

        self.label_5.setText(QCoreApplication.translate("Form", u"Baud Rate:", None))

        self.baudRateCombo.setCurrentText(QCoreApplication.translate("Form", u"115200", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"Available serial ports:", None))
        self.scanPort.setText(QCoreApplication.translate("Form", u"Scan Port", None))
        self.connectToPort.setText(QCoreApplication.translate("Form", u"Connect to Port", None))
        self.disconnectFromPort.setText(QCoreApplication.translate("Form", u"Disconnect", None))
        self.label.setText(QCoreApplication.translate("Form", u"Estimated Ball Pose:", None))
        self.label_21.setText(QCoreApplication.translate("Form", u"Pose Parameters:", None))
        self.label_9.setToolTip(QCoreApplication.translate("Form", u"Yaw angular velocity", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Yaw ang. speed", None))
        self.rotAxisLabel.setText(QCoreApplication.translate("Form", u"(1, 0, 0)", None))
        self.label_12.setToolTip(QCoreApplication.translate("Form", u"Accumulated head direction offset", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Acc. HD offset", None))
        self.label_14.setToolTip(QCoreApplication.translate("Form", u"Pitch angular velocity", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Pitch ang. speed", None))
        self.HDOffsetLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.placeOffsetLabel.setText(QCoreApplication.translate("Form", u"(0, 0)", None))
        self.label_7.setToolTip(QCoreApplication.translate("Form", u"Accumulated rotation axis", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Acc. rot. axis", None))
        self.label_17.setToolTip(QCoreApplication.translate("Form", u"Roll angular velocity", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Roll ang. speed", None))
        self.pitchSpeedLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_19.setToolTip(QCoreApplication.translate("Form", u"Accumulated place offset (cm)", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"Acc. place offset", None))
        self.rotAngleLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.rollSpeedLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_11.setToolTip(QCoreApplication.translate("Form", u"Accumulated rotation angle", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Acc. rot. angle", None))
        self.yawSpeedLabel.setText(QCoreApplication.translate("Form", u"0", None))

        self.connectToPort.clicked.connect(self.connect)

        # add codes below
        self._value = value

        self.port = None

        self.quaternion_history = [
            quaternion.quaternion(1, 0, 0, 0),
            quaternion.quaternion(1, 0, 0, 0),
            quaternion.quaternion(1, 0, 0, 0),
            quaternion.quaternion(1, 0, 0, 0)
        ]
        self.time_stamp = [
            time.time()-3e5,
            time.time()-2e5,
            time.time()-1e5,
            time.time()
        ]

        self.acc_x = 0
        self.acc_y = 0

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.counter = 0

        self._port_name_list = []
        self.scan()
        if self._value["COM"] in self._port_name_list:
            self.portCombo.setCurrentText(self._value["COM"])

        self._value["runtime correction"] = self._value.get("runtime correction", False)
        self.allowRuntimeCorrectionCheckBox.setChecked(self._value["runtime correction"])
        self.cameraCombo.setEnabled(self._value["runtime correction"])

        self.allowRuntimeCorrectionCheckBox.clicked.connect(self.allow_runtime_correction_change)

        self._value["source"] = self._value.get("source", None)
        if self._value["source"] is not None:
            self.cameraCombo.setCurrentText(self._value["source"])

        self.cameraCombo.currentTextChanged.connect(self.camera_change)

    def allow_runtime_correction_change(self):
        self._value["runtime correction"] = self.allowRuntimeCorrectionCheckBox.isChecked()
        self.cameraCombo.setEnabled(self._value["runtime correction"])

    def camera_change(self):
        self._value["source"] = self.cameraCombo.currentText()

    def scan(self):
        _ports = list_ports.comports()
        self._port_name_list = []
        for _port in _ports:
            self._port_name_list.append(_port.name)

        self.portCombo.clear()

        if len(_ports):
            self.portCombo.addItems(self._port_name_list)
            self.connectToPort.setEnabled(True)
            self.baudRateCombo.setEnabled(True)
        else:
            self.connectToPort.setEnabled(False)
            self.baudRateCombo.setEnabled(False)

    def print(self, content: str):
        self.portMessageBrowser.append(content)

    def process_qu(self, _qu):
        _q = quaternion.quaternion(_qu[0], _qu[1], _qu[2], _qu[3])
        _t = time.time()

        self.quaternion_history.append(_q)
        self.quaternion_history.pop(0)
        self.time_stamp.append(_t)
        self.time_stamp.pop(0)

        self.ballPoseWidget.set_view_point(_q)

        # rotation axis
        _rot_axis = quaternion.as_rotation_vector(_q)
        _rot_axis = _rot_axis / np.linalg.norm(_rot_axis)
        _rot_angle = (_q.angle() / math.pi * 180) % 360

        self.rotAxisLabel.setText("({:.3f}, {:.3f}, {:.3f})".format(_rot_axis[0], _rot_axis[1], _rot_axis[2]))
        self.rotAngleLabel.setText("{:.1f}".format(_rot_angle))

        _t_prime = (self.time_stamp[3] - self.time_stamp[2])
        _q_prime = self.quaternion_history[3] / self.quaternion_history[2]

        lspeed = quaternion.rotate_vectors(_q_prime, np.eye(3))
        lspeed = (lspeed / np.diag(lspeed) - np.eye(3)) / _t_prime
        lspeed = (- lspeed + np.transpose(lspeed)) / 2
        lspeed_x = lspeed[0, 2] * self.pitchScalingSpin.value()
        lspeed_y = lspeed[1, 2] * self.rollScalingSpin.value()

        self.rollSpeedLabel.setText("{:.2f}".format(lspeed_x))
        self.yawSpeedLabel.setText("{:.2f}".format(lspeed_y))

        if abs(lspeed_x) < 0.5:
            lspeed_x = 0
        if abs(lspeed_y) < 0.5:
            lspeed_y = 0

        self.acc_y += lspeed_y * (self.time_stamp[3] - self.time_stamp[2])
        self.acc_x += lspeed_x * (self.time_stamp[3] - self.time_stamp[2])
        self.acc_x = round(self.acc_x, 5)     # acc means accumulated, not acceleration
        self.acc_y = round(self.acc_y, 5)

        self.placeOffsetLabel.setText(f"({self.acc_x}, {self.acc_y})")

        if self.counter > 3:
            server_address = (LOCAL_IP, BALL_UDP_PORT)
            _s = rotate_vector_2d(lspeed_x, lspeed_y, self.rotateSpin.value()*math.pi / 180)
            self.client_socket.sendto(_s.encode("gbk"), server_address)
        else:
            self.counter += 1

    def begin_pose_check(self):
        counter = 0
        self.counter = 0
        try:
            while self.port.isOpen():
                if self.port.in_waiting:
                    _new_line = self.port.readline().decode('utf8')[:-2]
                    counter += 1
                    if counter == 2:
                        counter = 0
                        _preprocess = _new_line.split(',')
                        if len(_preprocess) == 4:
                            _qu = [int(_preprocess[_i]) / 32768 for _i in range(4)]
                            self.process_qu(_qu)
                        else:
                            self.print(_new_line)
        except serial.SerialException as e:
            self.print("Port disconnected.")
            self.scanPort.setEnabled(True)
            self.scan()
        except Exception as e:
            pass

    def connect(self):
        try:
            baud_rate = int(self.baudRateCombo.currentText())
            self.port = serial.Serial(self.portCombo.currentText(), baud_rate)
            self.print(f"Port {self.port.name} connected successfully!")
            self.connectToPort.setEnabled(False)
            self.baudRateCombo.setEnabled(False)
            threading.Thread(target=self.begin_pose_check).start()
            self.scanPort.setEnabled(False)
            self._value["COM"] = self.portCombo.currentText()
        except Exception as e:
            QMessageBox.critical(self, "Connect to port", f"Connection error: {e.args}")

    def exec(self):
        _v = super(VRBallEditor, self).exec()

        if self.port is not None and self.port.isOpen():
            self.port.close()

        server_address = (LOCAL_IP, BALL_UDP_PORT)
        self.client_socket.sendto(f"0,0".encode("gbk"), server_address)
        self.client_socket.close()

        if _v:
            return {
                        "COM": self._value["COM"],
                        "yaw-scale": self.yawScalingSpin.value(),
                        "pitch-scale": self.pitchScalingSpin.value(),
                        "roll-scale": self.rollScalingSpin.value(),
                        "rotate": self.rotateSpin.value(),

                        "runtime correction": self._value["runtime correction"],
                        "source": self._value["source"]
                    }, _v

        return None, _v


class RunTimeVRBall(QThread):

    def __init__(self):
        super(RunTimeVRBall, self).__init__()

        self.ble_com = None
        self.scales = [1, 1, 1]

        # create udp socket as soon as this class is initialized
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_port = (LOCAL_IP, BALL_UDP_PORT)

        self.time_stamp = [
            time.time() - 1e-2,
            time.time()
        ]

        self._qu = [1, 0, 0, 0]

        self.quaternion_history = [
            quaternion.quaternion(1, 0, 0, 0),
            quaternion.quaternion(1, 0, 0, 0)
        ]
        self.delta_x = 0
        self.delta_y = 0
        self.rotate = 0

    def connect_to_port(self, com_name, scales, rotate):
        self.ble_com = serial.Serial(com_name, 115200)
        self.scales = scales
        self.rotate = rotate * math.pi / 180

        # connect to port and wait until ball is connected
        while self.ble_com.isOpen():
            if self.ble_com.in_waiting:
                _new_line = self.ble_com.readline().decode('utf8')[:-2]
                _preprocess = _new_line.split(',')
                if len(_preprocess) == 4:
                    break

    def run(self):
        # use connect_to_port() before you use run()
        try:
            if self.ble_com and self.ble_com.isOpen():
                while self.ble_com.isOpen():
                    self._get_ball_pose()
                    self._feed_back_ball_pose()
                    time.sleep(0.04)
        except serial.SerialException as e:
            pass

    def _get_ball_pose(self):
        # skip data beyond computation power
        while self.ble_com.in_waiting:
            try:
                _new_line = self.ble_com.readline()
            except TypeError:
                return
            except AttributeError:
                return
            if _new_line is None:
                return
            _new_line = _new_line.decode('utf8')[:-2]
            _preprocess = _new_line.split(',')
            if len(_preprocess) == 4:
                self._qu = [int(_preprocess[_i]) / 32768 for _i in range(4)]

        # compute pose
        _q = quaternion.quaternion(self._qu[0], self._qu[1], self._qu[2], self._qu[3])
        _t = time.time()

        # use successive minus
        self.quaternion_history.append(_q)
        self.quaternion_history.pop(0)
        self.time_stamp.append(_t)
        self.time_stamp.pop(0)

        _q_prime = self.quaternion_history[1] / self.quaternion_history[0]
        _t_prime = self.time_stamp[1] - self.time_stamp[0]

        lspeed = quaternion.rotate_vectors(_q_prime, np.eye(3))
        lspeed = (lspeed / np.diag(lspeed) - np.eye(3)) / _t_prime
        lspeed = (- lspeed + np.transpose(lspeed)) / 2
        self.delta_x = lspeed[0, 2] * self.scales[1]
        self.delta_y = lspeed[1, 2] * self.scales[2]

        if abs(self.delta_x) < 0.5:
            self.delta_x = 0
        if abs(self.delta_y) < 0.5:
            self.delta_y = 0

        self.delta_x = round(self.delta_x, 5)
        self.delta_y = round(self.delta_y, 5)

    def _feed_back_ball_pose(self):
        try:
            self.client_socket.sendto(rotate_vector_2d(self.delta_x, self.delta_y, self.rotate).encode("gbk"), self.udp_port)
        except:
            pass
    
    def stop(self):
        try:
            self.delta_x = 0
            self.delta_y = 0
            self._feed_back_ball_pose()
            self.client_socket.close()
            self.ble_com.close()
        except:
            pass


class Canvas(QGraphicsView):
    resized = pyqtSignal()

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


class CorrectionWindow(QWidget):

    my_resized = pyqtSignal(int, int)
    img_updated = pyqtSignal(object)
    to_close = pyqtSignal()
    direction_corrected = pyqtSignal(float)

    def __init__(self, title, vrball: RunTimeVRBall):

        super(CorrectionWindow, self).__init__()
        self.vrball = vrball

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.CameraReturn = Canvas(self)

        self.verticalLayout.addWidget(self.CameraReturn)

        self.horizontalLayout = QHBoxLayout()

        self.angleSlider = QSlider(Qt.Orientation.Horizontal)
        self.angleSlider.setMaximum(720)
        self.angleSlider.setMinimum(0)
        MySizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.angleSlider.setSizePolicy(MySizePolicy)
        self.angleSlider.setValue(self.vrball.rotate*180/np.pi)
        self.angleSlider.setSingleStep(1)

        self.angleLabel = QLabel(str(round(self.vrball.rotate*180/np.pi,1)))
        self.angleLabel.setMinimumWidth(70)
        self.horizontalLayout.addWidget(self.angleSlider)
        self.horizontalLayout.addWidget(self.angleLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.angleSlider.valueChanged.connect(self.slider_value_change)

        self.setWindowTitle(title)

    def slider_value_change(self):
        new_value = self.angleSlider.value()
        self.angleLabel.setText(str(round(new_value, 1)))
        self.vrball.rotate = new_value/180*np.pi

    def update_value(self):
        self.angleSlider.setValue(self.vrball.rotate*180/np.pi)
        self.angleLabel.setText(str(round(self.vrball.rotate*180/np.pi,1)))

    def set_size(self, _w, _h):
        self.resize(_w, _h)
        self.show()

    def update_img(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pix_map = QPixmap(QImage(img, img.shape[1], img.shape[0], img.shape[1]*img.shape[2], QImage.Format.Format_RGB888)).scaled(self.CameraReturn.width()-2, self.CameraReturn.height()-2)
        self.CameraReturn.draw_pixmap(pix_map)


class MVRBall:

    requirements = {
        "variable": True,
        "runner": False,
        "interface": False
    }
    value_editor = VRBallEditor
    filter_func = dict

    gui_param = {
        "menu_name": "VR Ball Sensor Interface",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MVRBall",

        "name": None,
        "value": {
            "COM": "",
            "yaw-scale": 0.05,
            "pitch-scale": 0.05,
            "roll-scale": 0.05,
            "rotate": 0,

            "runtime correction": False,
            "source": None
        },
        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = dict(value)
        self._name = _name
        self._record = None
        self.variable = dict()
        self._id = 0

        self._x = 0
        self._y = 0

        self.vr_ball = RunTimeVRBall()

        self._runtime_correction = self._value.get("runtime correction", False)
        self.cam = None
        if self._runtime_correction:
            self._correction_window = CorrectionWindow(self._name, self.vr_ball)
            self._correction_window.my_resized.connect(self._correction_window.set_size)
            self._correction_window.img_updated.connect(self._correction_window.update_img)
            self._correction_window.to_close.connect(self._correction_window.close)

        self._running = False

    def start(self):
        if self._runtime_correction:
            self.cam = self.variable[self._value["source"]]

        self.vr_ball.connect_to_port(self._value["COM"], [
           self._value["yaw-scale"],
           self._value["pitch-scale"],
           self._value["roll-scale"]
        ], self._value.get("rotate", 0))
        self.vr_ball.start()
        self._running = True

        if self._runtime_correction:
            self._correction_window.CameraReturn.ready = True
            _x0, _x1, _y0, _y1, _w, _h = self.cam.get_wh()
            self._correction_window.update_value()
            self._correction_window.my_resized.emit(_w, _h)
            self._t1 = MyThread(target=self._update_window)
            self._t1.start()

    def stop(self):
        self.vr_ball.stop()
        self._running = False

    def set_record(self, _record):
        self._record = _record

    def _update_window(self):
        while self._running:
            self._correction_window.img_updated.emit(self.cam.current_img)
            time.sleep(0.03)
        self._correction_window.to_close.emit()
