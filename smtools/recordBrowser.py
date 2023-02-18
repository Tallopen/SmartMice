# -*- coding: utf-8 -*-
# created at: 2022/12/14 16:32
# author    : Gao Kai
# Email     : gaosimin1@163.com
import shutil

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os.path
import pickle
from openpyxl import Workbook
from scipy.io import savemat
import numpy as np


SORT_ITEM = ["fsa", "experimenter", "subject", "round", "trial", "session", "block",
             "group", "date"]
GROUP_FUNC = {
    "fsa": lambda x: x.props["fsa"],
    "experimenter": lambda x: x.props["experimenter"],
    "subject": lambda x: x.props["subject"],
    "round": lambda x: x.props["round"],
    "trial": lambda x: x.props["trial"],
    "session": lambda x: x.props["session"],
    "block": lambda x: x.props["block"],
    "group": lambda x: x.props["group"],
    "date": lambda x: x.props["creation-datetime"].split("-")[0]
}


def group_by(_x: list, _keyword_list: list):
    _grouped = dict()
    if _keyword_list:
        for _item in _x:
            _group_key = GROUP_FUNC[_keyword_list[0]](_item)
            if not _group_key:
                _group_key = "(unfilled)"
            if _group_key not in _grouped:
                _grouped[_group_key] = []
            _grouped[_group_key].append(_item)
        if len(_keyword_list) > 1:
            for _group_key in _grouped:
                _grouped[_group_key] = group_by(_grouped[_group_key], _keyword_list[1:])
    else:
        _grouped = _x
    return _grouped


def add_items(root_item, dict_2_parse, item_store_dict):
    if type(dict_2_parse) == list:
        for item in dict_2_parse:
            _temp_item = QTreeWidgetItem(root_item)
            _temp_item.setText(0, item.props["name"])
            _temp_item.setCheckState(0, item.check_state)
            item_store_dict[item.props["name"]] = item
    else:
        for item, key_dict in dict_2_parse.items():
            _temp_item = QTreeWidgetItem(root_item)
            _temp_item.setText(0, item)
            _temp_item.setCheckState(0, Qt.CheckState.Unchecked)
            add_items(_temp_item, key_dict, item_store_dict)


def check_state_calc(_item: QTreeWidgetItem):
    returned_state = _item.child(0).checkState(0)
    for _i in range(1, _item.childCount()):
        if _item.child(_i).checkState(0) != returned_state:
            return Qt.CheckState.PartiallyChecked
    return returned_state


def set_check_state(_item: QTreeWidgetItem):
    if _item.childCount():
        for _index in range(0, _item.childCount()):
            set_check_state(_item.child(_index))
        _item.setCheckState(0, check_state_calc(_item))


def extract_common(_a: list, _b: list):
    _c = []
    for _index in range(0, min(len(_a), len(_b))):
        if _a[_index] == _b[_index]:
            _c.append(_a[_index])
        else:
            return _c
    return _c


class Record:

    def __init__(self, name, _path, _data_path):

        self.is_exist = os.path.isfile(_path)
        if self.is_exist:
            with open(_path, 'rb') as f:
                self.props = pickle.load(f)
        else:
            self.props = dict()
            self.props["name"] = name
        self.data_path = _data_path
        self.check_state = Qt.CheckState.Unchecked


class RecordBrowser(QWidget):

    def __init__(self, project, master):

        super(RecordBrowser, self).__init__()
        self.project = project
        self.master = master
        self.record_list = self.refresh_record_list()

        # construct UI
        self.resize(550, 350)
        self.setWindowTitle("Record Browser")
        self.horizontalLayout_6 = QHBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.treeWidget = QTreeWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.treeWidget)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout_4 = QVBoxLayout()
        self.label_2 = QLabel(self)

        self.verticalLayout_4.addWidget(self.label_2)
        self.listWidget = QListWidget(self)
        self.verticalLayout_4.addWidget(self.listWidget)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.toolButton_2 = QToolButton(self)
        self.verticalLayout_5.addWidget(self.toolButton_2)
        self.toolButton_4 = QToolButton(self)
        self.verticalLayout_5.addWidget(self.toolButton_4)

        self.toolButton_3 = QToolButton(self)
        self.toolButton_3.setToolTipDuration(0)
        self.verticalLayout_5.addWidget(self.toolButton_3)
        self.toolButton = QToolButton(self)
        self.verticalLayout_5.addWidget(self.toolButton)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.verticalLayout_3 = QVBoxLayout()
        self.label = QLabel(self)

        self.verticalLayout_3.addWidget(self.label)
        self.listWidget_2 = QListWidget(self)
        self.verticalLayout_3.addWidget(self.listWidget_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_6.addLayout(self.verticalLayout)

        self.line_2 = QFrame(self)
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_6.addWidget(self.line_2)
        self.verticalLayout_2 = QVBoxLayout()
        self.label_4 = QLabel(self)
        self.verticalLayout_2.addWidget(self.label_4)
        self.label_10 = QLabel(self)
        self.verticalLayout_2.addWidget(self.label_10)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)
        self.pushButton_3 = QPushButton(self)
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.line_4 = QFrame(self)
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)
        self.verticalLayout_2.addWidget(self.line_4)

        self.label_3 = QLabel(self)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(250, 0))
        self.verticalLayout_2.addWidget(self.label_3)
        self.label_5 = QLabel(self)
        self.verticalLayout_2.addWidget(self.label_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton = QPushButton(self)

        self.horizontalLayout_3.addWidget(self.pushButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.line_3 = QFrame(self)
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.label_6 = QLabel(self)
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.label_6)

        self.gridLayout = QGridLayout()

        self.comboBox = QComboBox(self)
        self.comboBox.addItem("Excel document (*.xlsx)")
        self.comboBox.addItem("MATLAB data (*.mat)")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)

        self.label_8 = QLabel(self)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)

        self.verticalLayout_2.addLayout(self.gridLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_5.addWidget(self.pushButton_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.horizontalLayout_6.addLayout(self.verticalLayout_2)

        self.label_2.setText(QCoreApplication.translate("Form", u"Items:", None))
        self.toolButton_2.setToolTip(QCoreApplication.translate("Form", u"Move Item Up", None))
        self.toolButton_2.setText(QCoreApplication.translate("Form", u"U", None))
        self.toolButton_4.setToolTip(QCoreApplication.translate("Form", u"Move Item Down", None))
        self.toolButton_4.setText(QCoreApplication.translate("Form", u"D", None))
        self.toolButton_3.setText(QCoreApplication.translate("Form", u">", None))
        self.toolButton.setText(QCoreApplication.translate("Form", u"<", None))
        self.label.setText(QCoreApplication.translate("Form", u"Sort by:", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Common Main Root:", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"A common root does not exist", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Modify", None))
        self.pushButton_3.clicked.connect(self.modify_record_root_dir)
        self.label_3.setText(QCoreApplication.translate("Form", u"Common Sub-path Root:", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"(None)", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Modify", None))
        self.pushButton.setEnabled(False)
        self.label_6.setText(QCoreApplication.translate("Form", u"Export:", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Type:", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Export", None))

        for item_name in SORT_ITEM:
            self.listWidget.addItem(QListWidgetItem(item_name))
        self.listWidget.sortItems(Qt.SortOrder.AscendingOrder)

        self.toolButton_3.clicked.connect(self.move_in)
        self.toolButton.clicked.connect(self.move_out)
        self.toolButton_2.clicked.connect(self.move_up)
        self.toolButton_4.clicked.connect(self.move_down)
        self.pushButton_2.clicked.connect(self.export)

        self.tw_items = dict()
        self.treeWidget.setHeaderHidden(True)
        self.sort()

        self.treeWidget.itemClicked.connect(self.item_checked)
        self.property_root = ""

        self.checking_enabled = True

    def refresh_record_list(self):
        record_list = []
        for record_index in self.project.record_list():
            _res, _rcd = self.project.record_get_path(record_index)
            if _res:
                record_list.append(Record(record_index, _rcd[0], _rcd[1]))
        return record_list

    def move_in(self):
        for item in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.indexFromItem(item).row())
            self.listWidget_2.addItem(item)
        self.sort()

    def move_out(self):
        for item in self.listWidget_2.selectedItems():
            self.listWidget_2.takeItem(self.listWidget_2.indexFromItem(item).row())
            self.listWidget.addItem(item)
        self.sort()

    def move_up(self):
        for item in self.listWidget_2.selectedItems():
            row_index = self.listWidget_2.indexFromItem(item).row()
            new_row_index = max(0, row_index - 1)
            self.listWidget_2.takeItem(row_index)
            self.listWidget_2.insertItem(new_row_index, item)
            self.listWidget_2.clearSelection()
            item.setSelected(True)
        self.sort()

    def move_down(self):
        max_row_number = self.listWidget_2.count() - 1
        for item in self.listWidget_2.selectedItems():
            row_index = self.listWidget_2.indexFromItem(item).row()
            new_row_index = min(max_row_number, row_index + 1)
            self.listWidget_2.takeItem(row_index)
            self.listWidget_2.insertItem(new_row_index, item)
            self.listWidget_2.clearSelection()
            item.setSelected(True)
        self.sort()

    def item_checked(self, _item: QTreeWidgetItem, _column):

        # all child item will be checked
        self._check_item(_item, _value=_item.checkState(0))

        # change check state of all parent items
        self._change_parents(_item)

        self._update_info()

    def _change_parents(self, _item: QTreeWidgetItem):
        if _item.parent() is not None and self.checking_enabled:
            _check_state = check_state_calc(_item.parent())
            if _check_state is not None:
                _item.parent().setCheckState(0, _check_state)
            self._change_parents(_item.parent())

    def _check_item(self, _item: QTreeWidgetItem, _value):
        if self.checking_enabled:
            _item.setCheckState(0, _value)
            if _item.childCount():
                for _i in range(_item.childCount()):
                    self._check_item(_item.child(_i), _value)
            else:
                self.tw_items[_item.text(0)].check_state = _value

    def _update_info(self):
        property_root_list = []
        _temp = []
        _sep = '/'

        if self.record_list:
            _sep = '/' if '/' in self.record_list[0].props["main-path"] else '\\'

        for _rec in self.record_list:
            if _rec.check_state == Qt.CheckState.Checked:
                property_root_list.append(_rec.props["main-path"].split(_sep))

        if len(property_root_list):
            _temp = property_root_list[0]
            for _index in range(1, len(property_root_list)):
                _temp = extract_common(_temp, property_root_list[_index])

        property_root = _sep.join(_temp)
        self.property_root = property_root
        if not property_root:
            property_root = "A common root does not exist"

        self.label_10.setText(property_root)

    def modify_record_root_dir(self):
        if self.property_root:
            new_root = QFileDialog.getExistingDirectory(self, "Modify Common Root", self.property_root)
            if new_root:
                for _rec in self.record_list:
                    if _rec.check_state == Qt.CheckState.Checked:
                        if _rec.is_exist:
                            _old_rcd_path = os.path.join(_rec.props["main-path"], _rec.props["name"] + ".smrprop")
                            _new_rcd_path = os.path.join(new_root, _rec.props["name"] + ".smrprop")

                            shutil.move(_old_rcd_path, _new_rcd_path)
                            with open(_new_rcd_path, "rb") as f:
                                _rcd = pickle.load(f)
                            _rcd["main-path"] = new_root
                            with open(_new_rcd_path, "wb") as f:
                                pickle.dump(_rcd, f)

                            _old_data_path = os.path.join(_rec.props["main-path"], _rec.props["name"] + ".smrdata")
                            if os.path.isfile(_old_data_path):
                                _new_data_path = os.path.join(new_root, _rec.props["name"] + ".smrdata")
                                shutil.move(_old_data_path, _new_data_path)

                        self.project._m["record"][_rec.props["name"]]["path"] = new_root

                self.project.save()
                self.master.history.clear()
                self.master.actionRedo.setEnabled(False)
                self.master.actionUndo.setEnabled(False)
                self.record_list = self.refresh_record_list()
                self.sort()
                self._update_info()

    def sort(self):
        self.checking_enabled = False

        self.treeWidget.clear()

        _file_missing = list()
        _to_sort = list()
        for _record in self.record_list:
            if _record.is_exist:
                _to_sort.append(_record)
            else:
                _file_missing.append(_record)

        keyword_list = [self.listWidget_2.item(_i).text() for _i in range(self.listWidget_2.count())]
        sort_result = group_by(_to_sort, keyword_list)

        # sync sorting result into treeWidget
        if type(sort_result) == list:
            for _item in sort_result:
                _temp_item = QTreeWidgetItem(self.treeWidget)
                _temp_item.setText(0, _item.props["name"])
                _temp_item.setCheckState(0, _item.check_state)
                self.treeWidget.addTopLevelItem(_temp_item)
                self.tw_items[_item.props["name"]] = _item
        else:
            for _key, _item in sort_result.items():
                _temp_item = QTreeWidgetItem(self.treeWidget)
                _temp_item.setText(0, _key)
                self.treeWidget.addTopLevelItem(_temp_item)
                add_items(_temp_item, _item, self.tw_items)

        for _index in range(0, self.treeWidget.topLevelItemCount()):
            set_check_state(self.treeWidget.topLevelItem(_index))

        self.treeWidget.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.treeWidget.expandAll()

        self.checking_enabled = True

    def export(self):
        _dir = QFileDialog.getExistingDirectory(self, "Export Record", "")

        if _dir:
            if not os.path.isdir(_dir):
                os.mkdir(_dir)

            # log selected records
            selected_records = []
            for _rec in self.record_list:
                if _rec.check_state == Qt.CheckState.Checked:
                    if _rec.is_exist:
                        selected_records.append(_rec)
                    else:
                        QMessageBox.critical(self, "Export Records", f"Record file of '{_rec.props['name']}' is missing, export aborted.")
                        return

            if self.comboBox.currentText()[0] == "E":
                # export as excel table
                for _rec in selected_records:
                    _path = os.path.join(_dir, _rec.props["name"] + ".xlsx")
                    _data_path = os.path.join(_rec.props["main-path"], _rec.props["name"] + ".smrdata")

                    _w = Workbook()
                    _ws = _w.active
                    _ws.title = "info"
                    for _key, _item in _rec.props.items():
                        _ws.append([_key, str(_item)])

                    if _rec.props["spent"] and os.path.isfile(_data_path):
                        with open(_data_path, "rb") as f:
                            _data = pickle.load(f)
                        _ws = _w.create_sheet("data")

                        for _row in _data["record"]:
                            _ws.append(_row)

                    _w.save(_path)

            else:
                # export as matlab file directly
                for _rec in selected_records:
                    _path = os.path.join(_dir, _rec.props["name"] + ".mat")
                    _data_path = os.path.join(_rec.props["main-path"], _rec.props["name"] + ".smrdata")

                    _content = _rec.props
                    if _rec.props["spent"] and os.path.isfile(_data_path):
                        with open(_data_path, "rb") as f:
                            _data = pickle.load(f)
                        _new_data = []
                        for _row in _data["record"]:
                            _new_data.append(np.array(_row, np.object))
                        _new_data = np.array(_new_data)
                        _content["data"] = _new_data

                    savemat(_path, _content)

            QMessageBox.about(self, "Export", "Export complete!           ")
