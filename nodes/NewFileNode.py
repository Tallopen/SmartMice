# -*- coding: utf-8 -*-
# created at: 2021/11/1 18:17
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode
from tkinter.filedialog import asksaveasfilename


class NewFileNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Control"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "NewFileNode",
        "x": 0,
        "y": 0,
        "var": {
            "output to": {
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

    def __init__(self, runtime_dict):
        super(NewFileNode, self).__init__(runtime_dict)

    def run(self, _record):
        _v = self.runtime["var"]["output to"].set_value(asksaveasfilename(title=self.runtime["name"]))
        return self.runtime["jump"]["Done"]
