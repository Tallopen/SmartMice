# -*- coding: utf-8 -*-
# created at: 2022/10/8 18:59
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class VariableSelectDialog(QDialog):

    def __init__(self, variable_list, icon: QIcon, original_variable):

        super(VariableSelectDialog, self).__init__()

        self.setMinimumSize(QSize(340, 205))
        self.setMaximumSize(QSize(340, 205))
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 170, 323, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 321, 161))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.listWidget = QListWidget(self.verticalLayoutWidget)
        self.listWidget.setObjectName(u"listWidget")

        for _item in variable_list:
            _new_item = QListWidgetItem(icon, _item, self.listWidget)
            self.listWidget.addItem(_new_item)
            if _item == original_variable:
                _new_item.setSelected(True)
            else:
                _new_item.setSelected(False)

        _new_item = QListWidgetItem("(None)", self.listWidget)
        if original_variable is None:
            _new_item.setSelected(True)
        else:
            _new_item.setSelected(False)

        self.listWidget.insertItem(0, _new_item)
        self.listWidget.sortItems(Qt.SortOrder.AscendingOrder)

        self.verticalLayout.addWidget(self.listWidget)

        self.setWindowTitle(u"Placeholder Edit")
        self.label.setText(u"Select a variable below for the placeholder:")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.original_variable = original_variable

    def exec(self):

        _v = super(VariableSelectDialog, self).exec()
        if len(self.listWidget.selectedItems()) == 1:
            _txt = self.listWidget.selectedItems()[0].text()
            if _txt != "(None)":
                if _txt != self.original_variable:
                    return _txt, _v
            else:
                return None, _v
        return None, _v


class RecordSelectDialog(QDialog):

    def __init__(self, variable_list):

        super(RecordSelectDialog, self).__init__()

        self.setMinimumSize(QSize(340, 205))
        self.setMaximumSize(QSize(340, 205))
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 170, 323, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 321, 161))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.listWidget = QListWidget(self.verticalLayoutWidget)
        self.listWidget.setObjectName(u"listWidget")

        for _item in variable_list:
            _new_item = QListWidgetItem(_item, self.listWidget)
            self.listWidget.addItem(_new_item)

        self.listWidget.sortItems(Qt.SortOrder.AscendingOrder)

        self.verticalLayout.addWidget(self.listWidget)

        self.setWindowTitle(u"Select a Record")
        self.label.setText(u"Choose a record below.\nAll records shown here are not spent:")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def exec(self):

        _v = super(RecordSelectDialog, self).exec()
        if _v and len(self.listWidget.selectedItems()) == 1:
            _txt = self.listWidget.selectedItems()[0].text()
            return _txt, _v
        return None, _v


def get_var_name(var_name_list, q_icon, original_variable):
    _d = VariableSelectDialog(var_name_list, QIcon(q_icon.toqpixmap()), original_variable)
    return _d.exec()


def get_record_name(record_name_list):
    _d = RecordSelectDialog(record_name_list)
    return _d.exec()
