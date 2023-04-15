# -*- coding: utf-8 -*-
# created at: 2023/4/5 14:58
# author    : Gao Kai
# Email     : gaosimin1@163.com
import os

from . import BaseNode


class CMDNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Control"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "CMDNode",
        "x": 0,                             # position X of the node
        "y": 0,                             # position Y of the node
        "var": {
            "bash file": {
                "type": "MFile",
                "name": None
            },
            "record content": {
                "type": "MStr",
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
        super(CMDNode, self).__init__(runtime_dict)

    def run(self, _record):
        _v = self.runtime["var"]["record content"].get_value()
        os.system('"' + self.runtime["var"]["bash file"].get_value() + '"')
        _record.log("System Event", "CMD Run", _v)
        return self.runtime["jump"]["Done"]
