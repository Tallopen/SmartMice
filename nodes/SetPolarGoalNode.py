# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:37
# author    : Gao Kai
# Email     : gaosimin1@163.com


from . import BaseNode
import random
import math


class SetPolarGoalNode(BaseNode):

    enabled = True

    gui_param = {
        "group": "Arithmetic"
    }
    has_input = True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": "SetPolarGoalNode",
        "x": 0,
        "y": 0,
        "var": {
            "VR": {
                "type": "MVR",
                "name": None
            },
            "rmin": {
                "type": "MNum",
                "name": None
            },
            "rmax": {
                "type": "MNum",
                "name": None
            },
            "theta": {
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
        super(SetPolarGoalNode, self).__init__(runtime_dict)

    def run(self, _record):

        roll_distance = random.random() * (self.runtime["var"]["rmax"].get_value() - self.runtime["var"]["rmin"].get_value()) + self.runtime["var"]["rmin"].get_value()
        roll_angle = (random.random() * self.runtime["var"]["theta"].get_value() - 0.5 * self.runtime["var"]["theta"].get_value()) * math.pi / 180

        y = math.cos(roll_angle) * roll_distance
        x = math.sin(roll_angle) * roll_distance

        self.runtime["var"]["VR"].new_reward(x, y)
        _record.log("Variable", "Reward set", f"{x},{y},{roll_distance},{roll_angle}")

        return self.runtime["jump"]["Done"]
