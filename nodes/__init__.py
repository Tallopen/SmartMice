# -*- coding: utf-8 -*-
# created at: 2021/11/1 14:48
# author    : Gao Kai
# Email     : gaosimin1@163.com


import inspect
import os
from pathlib import Path
import re
import sys


from .BaseNode import BaseNode

# we first import all scripts under ../nodes
for _p in Path(os.path.dirname(__file__)).iterdir():

    # for simplicity, we only accept files whose name ended with "Node", in camelcase
    if re.match(r'^[a-zA-Z]*Node\.py$', _p.name):
        if _p.name[:-3] != "BaseNode":
            exec(f'from .{_p.name[:-3]} import *')

# establish a dict: node class name -> node class
NODE_CLASS_DICT = dict()
for (_name, _) in inspect.getmembers(sys.modules[__name__]):

    # also, a node class name should end with "Node", in camelcase
    if re.match('[a-zA-Z]*Node', _name) and eval(_name).enabled:
        NODE_CLASS_DICT[_name] = eval(_name)
