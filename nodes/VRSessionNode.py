# -*- coding: utf-8 -*-
# created at: 2021/11/1 14:58
# author    : Gao Kai
# Email     : gaosimin1@163.com
import time

from PyQt6.QtCore import *
from . import BaseNode


class SessionDelay(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, session_length, vr):
        super(SessionDelay, self).__init__()

        self.session_length = session_length
        self.vr = vr

        self.running = True

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.session_length:
            time.sleep(0.5)
        self.vr.send_on_signal()


class VRSessionNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Communication"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "VRSessionNode",
        "x": 0,                             # position X of the node
        "y": 0,                             # position Y of the node
        "var": {
            "VR": {
                "type": "MVR",
                "name": None
            },
            "session duration": {
                "type": "MNum",
                "name": None
            }
        },
        "in-link": set(),
        "out-link": {
            "Done": None
        }
    }

    out_num = len(template_dict["out-link"])
    out_enum = dict(zip(template_dict["out-link"].keys(), range(out_num)))

    def __init__(self, runtime_dict: dict):
        super(VRSessionNode, self).__init__(runtime_dict)

        self.time = None

    def run(self, _record):
        self.runtime["var"]["VR"].send_on_signal()

        self.time = SessionDelay(self.runtime["var"]["session duration"].get_value()+10, self.runtime["var"]["VR"])
        self.time.start()

        return self.runtime["jump"]["Done"]
