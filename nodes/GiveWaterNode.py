# -*- coding: utf-8 -*-
# created at: 2021/11/1 14:58
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode
import winsound


class GiveWaterNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Communication"
    }
    has_input = True       # unless this node is a start node or is disabled, should always be True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "GiveWaterNode",
        "x": 0,                             # position X of the node
        "y": 0,                             # position Y of the node
        "var": {
            "lickometer": {
                "type": "MWater",
                "name": None
            },
        },
        "in-link": set(),
        "out-link": {
            "Done": None
        }
    }

    out_num = len(template_dict["out-link"])
    out_enum = dict(zip(template_dict["out-link"].keys(), range(out_num)))

    def __init__(self, runtime_dict: dict):
        super(GiveWaterNode, self).__init__(runtime_dict)

    def run(self, _record):
        self.runtime["var"]["lickometer"].give_water()
        return self.runtime["jump"]["Done"]
