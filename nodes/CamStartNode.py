# -*- coding: utf-8 -*-
# created at: 2021/11/1 14:58
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode


class CamStartNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Communication"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "CamStartNode",
        "x": 0,                             # position X of the node
        "y": 0,                             # position Y of the node
        "var": {
            "camera": {
                "type": "MCam",
                "name": None
            },
            "save path": {
                "type": "MStr",
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
        super(CamStartNode, self).__init__(runtime_dict)

    def run(self, _record):
        self.runtime["var"]["camera"].run(self.runtime["var"]["save path"].get_value())
        return self.runtime["jump"]["Done"]
