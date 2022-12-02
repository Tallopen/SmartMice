# -*- coding: utf-8 -*-
# created at: 2022/7/16 19:39
# author    : Gao Kai
# Email     : gaosimin1@163.com

import inspect
import os
from pathlib import Path
import re
import sys

for _p in Path(os.path.dirname(__file__)).iterdir():
    if re.match(r'^M[A-Z][a-zA-Z0-9_]*\.py$', _p.name):
        exec(f'from .{_p.name[:-3]} import *')

VAR_CLASS_DICT = dict()
for (_name, _) in inspect.getmembers(sys.modules[__name__]):
    if re.match('^M[A-Z][a-zA-Z0-9_]*$', _name):
        VAR_CLASS_DICT[_name] = eval(_name)
