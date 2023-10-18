# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:37
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode


class SetLinearTrackIdNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Arithmetic"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "SetLinearTrackIdNode",
        "x": 0,
        "y": 0,
        "var": {
            "VR": {
                "type": "MVR",
                "name": None
            },
            "ID": {
                "type": "MNum",
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

    def __init__(self, runtime_dict):
        super(SetLinearTrackIdNode, self).__init__(runtime_dict)

    def run(self, _record):
        self.runtime["var"]["VR"].set_linear_track_ID(int(self.runtime["var"]["ID"].get_value()))
        return self.runtime["jump"]["Done"]
