# -*- coding: utf-8 -*-
# created at: 2022/9/21 21:37
# author    : Gao Kai
# Email     : gaosimin1@163.com

from functools import partial
import os.path
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class FSAToolbox(QWidget):

    def __init__(self, gui_main):

        super(FSAToolbox, self).__init__()
        self.guiMain = gui_main
        self.setWindowIcon(gui_main.icon)

        self.setObjectName(u"FSAToolbox")
        self.resize(200, 400)
        self.move(260, 60)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.toolBox = QToolBox(self)
        self.toolBox.setObjectName(u"toolBox")
        self.toolBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.toolBox.setFrameShadow(QFrame.Shadow.Raised)

        self.setWindowTitle("FSA Toolbox")

        self.verticalLayout.addWidget(self.toolBox)

        self.toolBox.setCurrentIndex(1)
        self.toolBox.layout().setSpacing(0)

    def update_pages(self, _icon_path, _node_class: dict):
        # iterate through node class
        _sorted_node_class = dict()
        for _key, _value in _node_class.items():
            node_group = _value.gui_param["group"]
            if node_group not in _sorted_node_class:
                _sorted_node_class[node_group] = []
            _sorted_node_class[node_group].append(_key)

        for _key in _sorted_node_class:
            new_page = QWidget()
            _gridLayout = QGridLayout(new_page)
            _gridLayout.setSpacing(0)
            self.toolBox.addItem(new_page, _key)
            self.toolBox.setItemText(self.toolBox.indexOf(new_page), _key)

            button_counter_row = 0
            button_counter_col = 0
            for _node_name in _sorted_node_class[_key]:
                button_icon = QIcon(os.path.join(_icon_path, f"{_node_name}.png"))
                _new_button = QToolButton(new_page)
                _new_button.setIcon(button_icon)
                _new_button.setFixedSize(35, 35)
                _new_button.setIconSize(QSize(30, 30))
                _new_button.setToolTip(_node_name)
                _new_button.setToolTipDuration(0)
                _new_button.clicked.connect(partial(self.guiMain.fsa_viewer.enter_node_create_mode, _node_name))
                _gridLayout.addWidget(_new_button, button_counter_row, button_counter_col)
                button_counter_col += 1
                if button_counter_col > 4:
                    button_counter_col = 0
                    button_counter_row += 1
        self.toolBox.setEnabled(False)

    def show(self):
        super(FSAToolbox, self).show()
        self.guiMain.actionFSA_Toolbar.setChecked(True)

    def closeEvent(self, a0: QCloseEvent) -> None:
        super(FSAToolbox, self).closeEvent(a0)
        self.guiMain.actionFSA_Toolbar.setChecked(False)
