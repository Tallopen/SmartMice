# -*- coding: utf-8 -*-
# created at: 2022/12/14 16:32
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os.path
import pickle


def group_by(_x: list, _func):
    _grouped = dict()
    for _item in _x:
        _key = _func(_item)
        if not _key:
            _key = "? (unknown)"
        if _key in _grouped:
            _grouped[_key].append(_item)
        else:
            _grouped[_key] = [_item]
    return _grouped


class Record:

    def __init__(self, _path, _data_path):

        self.is_exist = os.path.isfile(_path)
        if self.is_exist:
            with open(_path, 'rb') as f:
                self.props = pickle.load(f)
        else:
            self.props = dict()
        self.data_path = _data_path
        self.selected = False


class RecordBrowser(QWidget):

    def __init__(self, project):

        super(RecordBrowser, self).__init__()
        self.project = project
        self.record_list = self.refresh_record_list()

        # construct UI
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

        self.treeView = QTreeWidget(self)

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

        # fill options
        self.comboBox.addItem("round")      # with date-block-session-trial-round
        self.comboBox.addItem("subject")    # with group-subject
        self.comboBox.addItem("experimenter")

        # tree widget items
        self.tw_items = []

        self.sort_by(self.comboBox.currentText())

    def refresh_record_list(self):
        record_list = []
        for record_index in self.project.record_list():
            _res, _rcd = self.project.record_get_path(record_index)
            if _res:
                record_list.append(Record(_rcd[0], _rcd[1]))
        return record_list

    def sort_by(self, _key):

        _file_missing = list()
        _to_sort = list()
        for _record in self.record_list:
            if _record.is_exist:
               _to_sort.append(_record)
            else:
                _file_missing.append(_record)

        sort_result = dict()
        if _key == "round":
            sort_result = group_by(_to_sort, lambda x: x.props["creation-datetime"].split("-")[0])
            for _time_key, _time_item in sort_result.items():
                sort_result[_time_key] = group_by(_time_item, lambda x: x.props["block"])
                for _block_key, _block_item in sort_result[_time_key].items():
                    sort_result[_time_key][_block_key] = group_by(_block_item, lambda x: x.props["session"])
                    for _session_key, _session_item in sort_result[_time_key][_block_key].items():
                        sort_result[_time_key][_block_key][_session_key] = group_by(_session_item, lambda x: x.props["trial"])
                        for _trial_key, _trial_item in sort_result[_time_key][_block_key][_session_key].items():
                            sort_result[_time_key][_block_key][_session_key][_trial_key] = group_by(_trial_item, lambda x: x.props["round"])
        elif _key == "subject":
            sort_result = group_by(_to_sort, lambda x: x.props["group"])
            for _group_key, _group_item in sort_result.items():
                sort_result[_group_key] = group_by(_group_item, lambda x: x.props["subject"])
        else:
            sort_result = group_by(_to_sort, lambda x: x.props["experimenter"])
            for _exp_key, _exp_item in sort_result.items():
                sort_result[_exp_key] = group_by(_exp_item, lambda x: x.props["subject"])

        while self.tw_items:
            _item = self.tw_items.pop()
            del _item

        # sync sorting result into treeWidget
        if _key == "round":
            for _time_key, _time_item in sort_result.items():
                _time_tw_item = QTreeWidgetItem(self.treeView)
                _time_tw_item.setText(0, _time_key)
                _time_tw_item.setCheckState(0, Qt.CheckState.Unchecked)
                self.treeView.addTopLevelItem(_time_tw_item)
                self.tw_items.append(_time_tw_item)
                for _block_key, _block_item in sort_result[_time_key].items():
                    _block_tw_item = QTreeWidgetItem(_time_tw_item)
                    _block_tw_item.setText(0, _block_key)
                    _block_tw_item.setCheckState(0, Qt.CheckState.Unchecked)
                    self.tw_items.append(_block_tw_item)
                    for _session_key, _session_item in sort_result[_time_key][_block_key].items():
                        _session_tw_item = QTreeWidgetItem(_block_tw_item)
                        _session_tw_item.setText(0, _session_key)
                        _session_tw_item.setCheckState(0, Qt.CheckState.Unchecked)
                        self.tw_items.append(_session_tw_item)
                        for _trial_key, _trial_item in sort_result[_time_key][_block_key][_session_key].items():
                            _trial_tw_item = QTreeWidgetItem(_session_tw_item)
                            _trial_tw_item.setText(0, _trial_key)
                            _trial_tw_item.setCheckState(0, Qt.CheckState.Unchecked)
                            self.tw_items.append(_trial_tw_item)
                            for _round_key, _round_item in sort_result[_time_key][_block_key][_session_key][_trial_key].items():
                                _round_tw_item = QTreeWidgetItem(_trial_tw_item)
                                _round_tw_item.setText(0, _round_key)
                                _round_tw_item.setCheckState(0, Qt.CheckState.Unchecked)
                                self.tw_items.append(_round_tw_item)
                                for _rec in _round_item:
                                    _rec_tw_item = QTreeWidgetItem(_round_tw_item)
                                    _rec_tw_item.setText(0, _rec.props["name"])
                                    _rec_tw_item.setCheckState(0, Qt.CheckState.Unchecked)
                                    self.tw_items.append(_rec_tw_item)
        self.treeView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.treeView.expandAll()
