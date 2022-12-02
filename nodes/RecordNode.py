# -*- coding: utf-8 -*-
# created at: 2021/11/1 14:58
# author    : Gao Kai
# Email     : gaosimin1@163.com


class RecordNode:

    enabled = True

    gui_param = {
        "group": "Control"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "RecordNode",
        "x": 0,                             # position X of the node
        "y": 0,                             # position Y of the node
        "var": {
            "variables": {
                "type": "MVarArray",
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

        self.runtime = runtime_dict

    def run(self, _record):
        for _var_name, _var_value in self.runtime["var"]["variables"]:
            _record.log("Variable Log", _var_name, _var_value)
        return self.runtime["jump"]["Done"]
