# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class VarArrayEditor(QDialog):

    def __init__(self, var_name, value: set, ass: dict, *args):
        super(VarArrayEditor, self).__init__()

        available_variables = {_k: _i["type"] for _k, _i in ass.items()}

        _var_icon = dict()
        for _var_type in set(available_variables.values()):
            _var_icon[_var_type] = QIcon(f"variables\\icon\\{_var_type}.png")

        _wrong_icon = QIcon("gui\\src\\NotOK.png")

        # prepare UI
        self.resize(500, 330)
        self.verticalLayout_4 = QVBoxLayout(self)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.VarOut = QListWidget(self)
        self.VarOut.setObjectName(u"VarOut")

        self.verticalLayout_2.addWidget(self.VarOut)
        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.moveIn = QToolButton(self)
        self.moveIn.setObjectName(u"moveIn")

        self.verticalLayout.addWidget(self.moveIn)

        self.moveOut = QToolButton(self)
        self.moveOut.setObjectName(u"moveOut")

        self.verticalLayout.addWidget(self.moveOut)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.VarIn = QListWidget(self)
        self.VarIn.setObjectName(u"VarIn")

        self.verticalLayout_3.addWidget(self.VarIn)

        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_4.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(f"Edit Variable Set: {var_name}")
        self.label.setText(u"Available variables:")
        self.moveIn.setText(u">")
        self.moveOut.setText(u"<")
        self.label_2.setText(u"Variables in set:")

        self.moveIn.clicked.connect(self.move_in)
        self.moveOut.clicked.connect(self.move_out)

        # generate items
        for _var_name, _var_type in available_variables.items():
            if _var_name not in value:
                _new_item = QListWidgetItem(_var_icon[_var_type], _var_name)
                self.VarOut.addItem(_new_item)

        for _var_name in value:
            _new_item = QListWidgetItem(_var_icon.get(available_variables.get(_var_name, None), _wrong_icon), _var_name)
            self.VarIn.addItem(_new_item)

        self.VarIn.sortItems()
        self.VarOut.sortItems()

    def move_in(self):
        for item in self.VarOut.selectedItems():
            self.VarOut.takeItem(self.VarOut.indexFromItem(item).row())
            self.VarIn.addItem(item)

        self.VarIn.sortItems()
        self.VarOut.sortItems()

    def move_out(self):
        for item in self.VarIn.selectedItems():
            self.VarIn.takeItem(self.VarIn.indexFromItem(item).row())
            self.VarOut.addItem(item)

        self.VarIn.sortItems()
        self.VarOut.sortItems()

    def exec(self):
        _v = super(VarArrayEditor, self).exec()

        _txt = []
        for _item_id in range(self.VarIn.count()):
            _txt.append(self.VarIn.item(_item_id).text())
        _txt.sort()

        if _v:
            return _txt, _v
        return None, _v


class MVarArray:

    requirements = {
        "variable": True,
        "runner": False,
        "interface": False
    }
    value_editor = VarArrayEditor
    filter_func = set

    gui_param = {
        "menu_name": "Variable Set",
        "group": "Basic"
    }
    template_dict = {
        "type": "MVarArray",

        "name": None,
        "value": set(),

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = list(value)
        self._name = _name
        self._record = None
        self.variable = dict()
        self._id = 0

    def __iter__(self):
        self._id = 0
        return self

    def __next__(self):
        if self._id < len(self._value):
            _name = self._value[self._id]
            self._id += 1

            if _name in self.variable:
                if hasattr(self.variable[_name], "get_value") and callable(self.variable[_name].get_value):
                    return _name, str(self.variable[_name].get_value())
                else:
                    return _name, "None"
            else:
                raise Exception(f"variable {_name} not found.")

        else:
            raise StopIteration

    def set_record(self, _record):
        self._record = _record
