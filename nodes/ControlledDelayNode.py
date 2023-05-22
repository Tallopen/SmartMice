# -*- coding: utf-8 -*-
# created at: 2021/11/1 18:17
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode
import time

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class Timing(QThread):

    time_update = pyqtSignal(int, int, int)

    def __init__(self):

        super(Timing, self).__init__()
        self.running = True
        self.start_time = 0

    def run(self):
        while self.running:
            delta_time = time.time() - self.start_time
            hours = int(delta_time // 3600)
            minutes = int(delta_time // 60 - 60 * hours)
            seconds = int(delta_time % 60)
            self.time_update.emit(hours, minutes, seconds)
            time.sleep(0.1)

    def set_start_time(self, t):
        self.start_time = t


class DelayControlPanel(QDialog):

    def __init__(self, *args, **kwargs):
        super(DelayControlPanel, self).__init__(*args, **kwargs)

        # generate GUI
        self.resize(210, 100)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(210, 100))
        self.setMaximumSize(QSize(210, 100))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.HourLCD = QLCDNumber(self)
        self.HourLCD.setObjectName(u"HourLCD")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.HourLCD.sizePolicy().hasHeightForWidth())
        self.HourLCD.setSizePolicy(sizePolicy1)
        self.HourLCD.setFrameShape(QFrame.Shape.NoFrame)
        self.HourLCD.setFrameShadow(QFrame.Shadow.Plain)
        self.HourLCD.setLineWidth(0)
        self.HourLCD.setDigitCount(5)
        self.HourLCD.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.horizontalLayout.addWidget(self.HourLCD)

        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setMaximumSize(QSize(5, 16777215))

        self.horizontalLayout.addWidget(self.label)

        self.MinuteLCD = QLCDNumber(self)
        self.MinuteLCD.setObjectName(u"MinuteLCD")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.MinuteLCD.sizePolicy().hasHeightForWidth())
        self.MinuteLCD.setSizePolicy(sizePolicy2)
        self.MinuteLCD.setFrameShape(QFrame.Shape.NoFrame)
        self.MinuteLCD.setFrameShadow(QFrame.Shadow.Plain)
        self.MinuteLCD.setLineWidth(0)
        self.MinuteLCD.setDigitCount(2)
        self.MinuteLCD.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.horizontalLayout.addWidget(self.MinuteLCD)

        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(5, 16777215))

        self.horizontalLayout.addWidget(self.label_2)

        self.SecondLCD = QLCDNumber(self)
        self.SecondLCD.setObjectName(u"SecondLCD")
        sizePolicy2.setHeightForWidth(self.SecondLCD.sizePolicy().hasHeightForWidth())
        self.SecondLCD.setSizePolicy(sizePolicy2)
        self.SecondLCD.setFrameShape(QFrame.Shape.NoFrame)
        self.SecondLCD.setFrameShadow(QFrame.Shadow.Plain)
        self.SecondLCD.setLineWidth(0)
        self.SecondLCD.setDigitCount(2)
        self.SecondLCD.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.horizontalLayout.addWidget(self.SecondLCD)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(u"Controlled Delay")
        self.label_3.setText(u"Time From Halt:")
        self.label.setText(u":")
        self.label_2.setText(u":")

        # begin timing
        self.t = Timing()
        self.continue_timer = True
        self.start_time = 0

        self.t.time_update.connect(self._timer_thread_event)

    @pyqtSlot(int, int, int)
    def _timer_thread_event(self, _h, _m, _s):
        self.HourLCD.display(_h)
        self.MinuteLCD.display(_m)
        self.SecondLCD.display(_s)

    def exec(self):
        self.start_time = time.time()
        self.t.set_start_time(self.start_time)
        self.t.start()
        _v = super(DelayControlPanel, self).exec()
        self.t.time_update.disconnect()
        self.t.running = False
        return _v


class ControlledDelayNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Control"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "ControlledDelayNode",
        "x": 0,
        "y": 0,
        "var": dict(),
        "in-link": set(),
        "out-link": {
            "Done": None
        }
    }

    out_num = len(template_dict["out-link"])
    out_enum = dict(zip(template_dict["out-link"].keys(), range(out_num)))

    def __init__(self, runtime_dict):
        super(ControlledDelayNode, self).__init__(runtime_dict)

        self._t = DelayControlPanel()

    def run(self, _record):
        self._t.exec()
        return self.runtime["jump"]["Done"]
