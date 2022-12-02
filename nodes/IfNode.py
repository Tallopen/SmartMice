# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:37
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode


class IfNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Logic"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "IfNode",
        "x": 0,
        "y": 0,
        "var": {
            "meta expression": {
                "type": "MExp",
                "name": None
            }
        },
        "in-link": set(),
        "out-link": {
            "True": None,
            "False": None
        }
    }

    out_num = len(template_dict["out-link"])
    out_enum = dict(zip(template_dict["out-link"].keys(), range(out_num)))

    def __init__(self, runtime_dict):
        super(IfNode, self).__init__(runtime_dict)

    def run(self, _record):
        _value = self.runtime["var"]["meta expression"].evaluate()
        if _value:
            return self.runtime["jump"]["True"]
        else:
            return self.runtime["jump"]["False"]
