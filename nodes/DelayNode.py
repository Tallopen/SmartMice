# -*- coding: utf-8 -*-
# created at: 2021/11/1 18:17
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode
import time


class DelayNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Control"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "DelayNode",
        "x": 0,
        "y": 0,
        "var": {
            "delay second": {
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

    def __init__(self, runtime_dict):
        super(DelayNode, self).__init__(runtime_dict)

    def run(self, _record):
        _v = self.runtime["var"]["delay second"].get_value()
        time.sleep(_v)
        return self.runtime["jump"]["Done"]
