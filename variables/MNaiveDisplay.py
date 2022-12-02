# -*- coding: utf-8 -*-
# created at: 2022/9/17 11:43
# author    : Gao Kai
# Email     : gaosimin1@163.com


import threading
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, _w, _s, _m):
        return None


class NaiveDisplayEditor(QDialog):

    def __init__(self, var_name, value: set, ass: dict, *args):
        super(NaiveDisplayEditor, self).__init__()

        available_variables = ass

        _var_icon = dict()
        for _var_type in set(available_variables.values()):
            _var_icon[_var_type] = QIcon(f"variables\\icon\\{_var_type}.png")

        _wrong_icon = QIcon("gui\\src\\NotOK.png")

        # prepare UI
        self.resize(500, 330)
        self.verticalLayout_4 = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout_2 = QVBoxLayout()
        self.label = QLabel(self)

        self.verticalLayout_2.addWidget(self.label)

        self.VarOut = QListWidget(self)

        self.verticalLayout_2.addWidget(self.VarOut)
        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.moveIn = QToolButton(self)

        self.verticalLayout.addWidget(self.moveIn)

        self.moveOut = QToolButton(self)

        self.verticalLayout.addWidget(self.moveOut)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.label_2 = QLabel(self)

        self.verticalLayout_3.addWidget(self.label_2)

        self.VarIn = QListWidget(self)

        self.verticalLayout_3.addWidget(self.VarIn)

        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_4.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(f"Edit naive display: {var_name}")
        self.label.setText(u"Available variables:")
        self.moveIn.setText(u">")
        self.moveOut.setText(u"<")
        self.label_2.setText(u"Variables to display:")

        self.moveIn.clicked.connect(self.move_in)
        self.moveOut.clicked.connect(self.move_out)

        # generate items
        _var_type_allowed = ("MNum", "MStr", "MTimer")
        for _var_name, _var_type in ass.items():
            if _var_name not in value and _var_type in _var_type_allowed:
                _new_item = QListWidgetItem(_var_icon[_var_type], _var_name)
                self.VarOut.addItem(_new_item)

        for _var_name in value:
            if _var_name in ass and ass[_var_name] in _var_type_allowed:
                _new_item = QListWidgetItem(_var_icon.get(ass.get(_var_name, None), _wrong_icon), _var_name)
            else:
                _new_item = QListWidgetItem(_wrong_icon, _var_name)
            self.VarIn.addItem(_new_item)

        self.VarIn.sortItems()
        self.VarOut.sortItems()

    def move_in(self):
        for item in self.VarOut.selectedItems():
            self.VarOut.takeItem(self.VarOut.indexFromItem(item).row())
            self.VarIn.addItem(item)

    def move_out(self):
        for item in self.VarIn.selectedItems():
            self.VarIn.takeItem(self.VarIn.indexFromItem(item).row())
            self.VarOut.addItem(item)

    def exec(self):
        _v = super(NaiveDisplayEditor, self).exec()

        _txt = []
        for _item_id in range(self.VarIn.count()):
            _txt.append(self.VarIn.item(_item_id).text())

        if _v:
            return _txt, _v
        return None, _v


class NaiveViewer(QWidget):

    show_event = pyqtSignal(dict)
    var_update_event = pyqtSignal(dict)
    close_event = pyqtSignal()

    def __init__(self, title):
        super(NaiveViewer, self).__init__()

        self.resize(500, 300)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setObjectName(u"tableView")
        self.verticalLayout.addWidget(self.tableWidget)

        _name_col = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, _name_col)
        _value_col = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, _value_col)

        _name_col = self.tableWidget.horizontalHeaderItem(0)
        _name_col.setText(QCoreApplication.translate("Form", u"Message Name", None))
        _value_col = self.tableWidget.horizontalHeaderItem(1)
        _value_col.setText(QCoreApplication.translate("Form", u"Value", None))

        self.tableWidget.setItemDelegate(EmptyDelegate(self.tableWidget))

        self.setWindowTitle(title)

        self.rec_2_id = dict()

    def show_event_rec(self, var_dict):
        self.rec_2_id = dict()
        for _item_id, _item_key in enumerate(var_dict):
            self.tableWidget.insertRow(_item_id)
            self.tableWidget.setRowHeight(_item_id, 6)
            self.tableWidget.setItem(_item_id, 0, QTableWidgetItem(str(_item_key)))
            self.tableWidget.setItem(_item_id, 1, QTableWidgetItem(str(var_dict[_item_key])))
            self.rec_2_id[_item_key] = _item_id
        self.show()

    def var_update_rec(self, var_dict):
        for _key, _dict in var_dict.items():
            if _key in self.rec_2_id:
                self.tableWidget.setItem(self.rec_2_id[_key], 1, QTableWidgetItem(str(var_dict[_key])))

    def close_event_rec(self):
        self.close()


class MNaiveDisplay:

    requirements = {
        "variable": True,
        "runner": True,
        "interface": False
    }
    value_editor = NaiveDisplayEditor
    filter_func = set

    gui_param = {
        "menu_name": "Naive Display",
        "group": "Visualization"
    }
    template_dict = {
        "type": "MNaiveDisplay",

        "name": None,
        "value": set(),

        "quote": set()
    }

    def __init__(self, value, _name):

        self._value = list(value)
        self._value_pair = dict()
        self._value.sort()
        self._name = _name
        self._record = None

        self.variable = dict()
        self.runner = None

        _value = []

        self._viewer = NaiveViewer(self._name)
        self._viewer.show_event.connect(self._viewer.show_event_rec)
        self._viewer.var_update_event.connect(self._viewer.var_update_rec)
        self._viewer.close_event.connect(self._viewer.close_event_rec)

    def set_record(self, _record):
        self._record = _record

    def _update(self):
        while self.runner.is_running():
            _acc_terms = dict()
            for _key, _value in self._value_pair.items():
                _v = self.variable[_key].get_value()
                if _value != _v:
                    _acc_terms[_key] = _v
                    self._value_pair[_key] = _v
            self._viewer.var_update_event.emit(_acc_terms)
            time.sleep(0.01)
        self._viewer.close_event.emit()

    def show(self):
        self._value_pair = dict()
        for _key in self._value:
            if _key in self.variable:
                if type(self.variable[_key]).__name__ in ("MNum", "MStr", "MTimer"):
                    self._value_pair[_key] = self.variable[_key].get_value()
        self._viewer.show_event.emit(self._value_pair)

        threading.Thread(target=self._update).start()
