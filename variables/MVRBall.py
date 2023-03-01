# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com


import copy
import math
import threading
import time

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

import numpy as np
import quaternion


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
        self.pitchScalingSpin.setSingleStep(0.01)
        self.pitchScalingSpin.setValue(1)

        self.horizontalLayout_3.addWidget(self.pitchScalingSpin)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.label_3 = QLabel(self)

        self.horizontalLayout_4.addWidget(self.label_3)

        self.rollScalingSpin = QDoubleSpinBox(self)
        self.rollScalingSpin.setMaximum(1000)
        self.rollScalingSpin.setSingleStep(0.01)
        self.rollScalingSpin.setValue(1)

        self.horizontalLayout_4.addWidget(self.rollScalingSpin)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.label_6 = QLabel(self)

        self.horizontalLayout_5.addWidget(self.label_6)

        self.yawScalingSpin = QDoubleSpinBox(self)
        self.yawScalingSpin.setEnabled(False)
        self.yawScalingSpin.setMaximum(1000)
        self.yawScalingSpin.setSingleStep(0.01)
        self.yawScalingSpin.setValue(1)

        self.horizontalLayout_5.addWidget(self.yawScalingSpin)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

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

    def scan(self):
        _ports = list_ports.comports()
        _port_name_list = []
        for _port in _ports:
            _port_name_list.append(_port.name)

        self.portCombo.clear()

        if len(_ports):
            self.portCombo.addItems(_port_name_list)
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

        _q1 = self.quaternion_history[0].inverse() * self.quaternion_history[2]
        _q2 = self.quaternion_history[1].inverse() * self.quaternion_history[3]

        euler_alter = (quaternion.as_euler_angles(_q2) / (self.time_stamp[2] - self.time_stamp[0]) + quaternion.as_euler_angles(_q1) / (self.time_stamp[3] - self.time_stamp[1])) / 2
        euler_alter = euler_alter / math.pi * 180

        self.yawSpeedLabel.setText("{:.1f}".format(euler_alter[1]))
        self.rollSpeedLabel.setText("{:.1f}".format(euler_alter[0]))
        self.pitchSpeedLabel.setText("{:.1f}".format(euler_alter[2]))
        # 上面这个计算有问题，别忘了

    def begin_pose_check(self):
        counter = 0
        try:
            while self.port.isOpen():
                if self.port.in_waiting:
                    _new_line = self.port.readline().decode('utf8')[:-2]
                    counter += 1
                    if counter == 2:
                        counter = 0
                        _preprocess = _new_line.split(',')
                        if len(_preprocess) == 4:
                            _qu = [int(_preprocess[_i]) * 0.000030517578125 for _i in range(4)]
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
        except Exception as e:
            QMessageBox.critical(self, "Connect to port", f"Connection error: {e.args}")

    def exec(self):
        _v = super(VRBallEditor, self).exec()

        if _v:
            return copy.deepcopy(self._value), _v

        if self.port is not None and self.port.isOpen():
            self.port.close()

        return None, _v


class MVRBall:

    requirements = {
        "variable": True,
        "runner": False,
        "interface": False
    }
    value_editor = VRBallEditor
    filter_func = set

    gui_param = {
        "menu_name": "Variable Set",
        "group": "Hardware"
    }
    template_dict = {
        "type": "MVRBall",

        "name": None,
        "value": {
            "COM": "",
            "yaw-scale": 1,
            "pitch-scale": 1,
            "roll-scale": 1,
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

    def set_coordinate(self, _x, _y):
        self._x = _x
        self._y = _y

    def get_coordinate(self):
        pass

    def set_record(self, _record):
        self._record = _record
