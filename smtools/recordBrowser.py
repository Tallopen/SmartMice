# -*- coding: utf-8 -*-
# created at: 2022/12/14 16:32
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os.path
import pickle


class Record:

    def __init__(self, _path, _data_path):

        self.is_exist = os.path.isfile(_path)
        if self.is_exist:
            with open(_path, 'rb') as f:
                self.props = pickle.load(f)
            self.data_path = _data_path
        else:
            self.props = dict()
            self.data_path = []


class RecordBrowser(QWidget):

    def __init__(self, project):

        super(RecordBrowser, self).__init__()
        self.project = project
        self.record_list = self.refresh_record_list()

        self.resize(386, 385)
        self.horizontalLayout_2 = QHBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.horizontalLayout_3 = QHBoxLayout()
        self.label = QLabel(self)

        self.horizontalLayout_3.addWidget(self.label)

        self.comboBox = QComboBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.comboBox)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.treeView = QTreeView(self)

        self.verticalLayout.addWidget(self.treeView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.exportButton = QPushButton(self)
        self.horizontalLayout.addWidget(self.exportButton)
        self.fixButton = QPushButton(self)
        self.horizontalLayout.addWidget(self.fixButton)
        self.removeButton = QPushButton(self)
        self.horizontalLayout.addWidget(self.removeButton)
        self.importButton = QPushButton(self)
        self.horizontalLayout.addWidget(self.importButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.setWindowTitle("Record Browser")
        self.label.setText("Sort by:")
        self.exportButton.setText("Export")
        self.fixButton.setText("Fix")
        self.removeButton.setText("Remove")
        self.importButton.setText("Import")

    def refresh_record_list(self):
        record_list = []
        for record_index in self.project.record_list():
            _res, _rcd = self.project.record_get_path(record_index)
            if _res:
                record_list.append(Record(_rcd[0], _rcd[1]))
        return record_list
