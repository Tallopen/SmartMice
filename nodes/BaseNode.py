# -*- coding: utf-8 -*-
# created at: 2021/11/1 14:58
# author    : Gao Kai
# Email     : gaosimin1@163.com


# base class of all smartMice nodes
class BaseNode:

    enabled = False

    has_input = False       # unless this node is a start node or is disabled, should always be True

    template_dict = {
        "name": None,
        "show-name": False,
        "type": None,
        "x": 0,                             # position X of the node
        "y": 0,                             # position Y of the node
        "var": {
            # If no variable, leave this vacant.
            # Otherwise, variables should be in the form of below:
            #     "one": {
            #         "type": "MInt",
            #         "name": None
            #     },
            #     "two": ...
        },
        "in-link": set(),
        "out-link": dict()
    }

    out_num = len(template_dict["out-link"])
    out_enum = dict(zip(template_dict["out-link"].keys(), range(out_num)))

    def __init__(self, runtime_dict: dict):

        self.runtime = runtime_dict

    def run(self, _record):
        """
        run action of nodes.
        :param _record: the record to log in
        :return: every id within length of self._output (which are numbers >= 0) can be returned. Note: if None is
                 returned, the program will be terminated. If -1 is returned, the nodes will run again
        """
        return None
