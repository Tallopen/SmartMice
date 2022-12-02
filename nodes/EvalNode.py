# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:37
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode


class EvalNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Arithmetic"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "EvalNode",
        "x": 0,
        "y": 0,
        "var": {
            "meta expression": {
                "type": "MExp",
                "name": None
            },
            "return": {
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
        super(EvalNode, self).__init__(runtime_dict)

    def run(self, _record):
        _value = self.runtime["var"]["meta expression"].evaluate()
        self.runtime["var"]["return"].set_value(_value)
        return self.runtime["jump"]["Done"]
