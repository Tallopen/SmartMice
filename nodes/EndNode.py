# -*- coding: utf-8 -*-
# created at: 2021/11/1 18:17
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode


class EndNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Control"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "EndNode",
        "x": 0,
        "y": 0,
        "var": {},
        "in-link": set(),
        "out-link": dict()
    }

    out_num = len(template_dict["out-link"])
    out_enum = dict(zip(template_dict["out-link"].keys(), range(out_num)))

    def __init__(self, runtime_dict):
        super(EndNode, self).__init__(runtime_dict)

    def run(self, _record):
        return None
