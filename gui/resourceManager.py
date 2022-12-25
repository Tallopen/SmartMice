# -*- coding: utf-8 -*-
# created at: 2022/9/21 22:17
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


PROPERTY_PROJECT = {
    "name": True,
    "contact": True,
    "creation-time": False,
    "export-format": True
}
PROPERTY_FSA = {
    "name": True,
    "experimenter": True,
    "creation-time": False,
    "additional-note": True
}
PROPERTY_RECORD = {
    "name": True,
    "fsa": False,
    "experimenter": True,
    "group": True,
    "subject": True,
    "round": True,
    "trial": True,
    "session": True,
    "block": True,
    "creation-datetime": False,
    "record-datetime": False,
    "spent": False,
    "note": True,
    "length": False
}

DICT_CHOOSE = {
    "project": PROPERTY_PROJECT,
    "fsa": PROPERTY_FSA,
    "record": PROPERTY_RECORD
}


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, _w, _s, _m):
        return None


class ResourceManager(QWidget):

    def __init__(self, gui_main):
        super(ResourceManager, self).__init__()

        self.guiMain = gui_main

        self.setObjectName(u"ResourceManager")
        self.resize(250, 400)
        self.move(0, 60)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.dockWidget = QDockWidget(self)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.projectTreeView = QTreeWidget(self.dockWidgetContents)
        self.projectTreeView.setObjectName(u"projectTreeView")

        self.verticalLayout_4.addWidget(self.projectTreeView)

        self.dockWidget.setWidget(self.dockWidgetContents)

        self.verticalLayout_2.addWidget(self.dockWidget)

        self.dockWidget_2 = QDockWidget(self)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidget_2.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.propertyView = QTableWidget(self.dockWidgetContents_2)
        self.propertyView.setObjectName(u"propertyView")
        self.propertyView.setColumnCount(2)
        self.propertyView.setHorizontalHeaderLabels(["Property", "Value"])
        self.propertyView.setItemDelegateForColumn(0, EmptyDelegate(self.propertyView))

        self.verticalLayout_3.addWidget(self.propertyView)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)

        self.verticalLayout_2.addWidget(self.dockWidget_2)

        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.setWindowTitle("Resource Manager")
        self.dockWidget.setWindowTitle("Project Structure")
        self.dockWidget_2.setWindowTitle("Property Editor")

        self.projectTreeView.setHeaderHidden(True)
        self.ICON_PROJECT = QIcon("gui\\src\\Project.png")
        self.ICON_RECORD = QIcon("gui\\src\\Record.png")
        self.ICON_FSA = QIcon("gui\\src\\FSA.png")

        self.current_type = None
        self.property_table = dict()

        self.locked = False

        self.project_root_item = None
        self.project_tree_fsa_root_item = None
        self.project_tree_fsa_items = dict()
        self.project_tree_record_root_item = None
        self.project_tree_record_items = dict()

        self.projectTreeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.projectTreeView.customContextMenuRequested.connect(self._show_project_tree_context_menu)

        self.project_tree_context_menu = QMenu(self)

        self.actionSort = self.project_tree_context_menu.addAction('Sort')
        self.actionSort.triggered.connect(lambda: self.projectTreeView.sortByColumn(0, Qt.SortOrder.AscendingOrder))

    def _show_project_tree_context_menu(self, pos):
        self.project_tree_context_menu.move(self.pos() + self.projectTreeView.pos() + QPoint(0, 40) + pos)
        self.project_tree_context_menu.show()

    def renew_project(self, _name, _m: dict):
        del self.project_root_item, self.project_tree_fsa_root_item, self.project_tree_record_root_item

        self.project_root_item = QTreeWidgetItem(self.projectTreeView)
        self.project_root_item.setIcon(0, self.ICON_PROJECT)
        self.project_root_item.setText(0, _name)
        self.projectTreeView.addTopLevelItem(self.project_root_item)

        self.project_root_item.setSelected(True)

        self.project_tree_fsa_root_item = QTreeWidgetItem(self.project_root_item)
        self.project_tree_fsa_root_item.setIcon(0, self.ICON_FSA)
        self.project_tree_fsa_root_item.setText(0, "FSA")
        self.project_root_item.addChild(self.project_tree_fsa_root_item)

        self.project_tree_record_root_item = QTreeWidgetItem(self.project_root_item)
        self.project_tree_record_root_item.setIcon(0, self.ICON_RECORD)
        self.project_tree_record_root_item.setText(0, "Record")
        self.project_root_item.addChild(self.project_tree_record_root_item)

        self.guiMain.interface.fsa_added.connect(self._fsa_added)
        self.guiMain.interface.fsa_removed.connect(self._fsa_removed)
        self.guiMain.interface.fsa_selected.connect(self._fsa_selected)
        self.guiMain.interface.record_added.connect(self._record_added)
        self.guiMain.interface.record_removed.connect(self._record_removed)
        self.guiMain.interface.record_selected.connect(self._record_selected)

        self.projectTreeView.itemSelectionChanged.connect(self._tree_widget_item_select)

        for _key in _m["fsa-index"]:
            _new_tree_item = QTreeWidgetItem(self.project_tree_fsa_root_item)
            _new_tree_item.setText(0, _key)
            self.project_tree_fsa_items[_key] = _new_tree_item
            self.project_tree_fsa_root_item.addChild(_new_tree_item)

        for _key in _m["record-index"]:
            _new_tree_item = QTreeWidgetItem(self.project_tree_record_root_item)
            _new_tree_item.setText(0, _key)
            self.project_tree_record_items[_key] = _new_tree_item
            self.project_tree_record_root_item.addChild(_new_tree_item)

    def renew_property_table(self, _type, _props: dict):
        qb = QBrush(QColor(220, 220, 220))
        self.property_table = dict()

        try:
            self.propertyView.disconnect()
        except Exception as e:
            if e.args:
                pass

        self.dockWidget_2.setWindowTitle(_props["name"])
        for row_id in range(self.propertyView.rowCount())[::-1]:
            self.propertyView.removeRow(row_id)

        self.current_type = _type
        for _item_id, _item in enumerate(DICT_CHOOSE[_type].keys()):
            self.property_table[_item] = _item_id
            self.propertyView.insertRow(_item_id)
            self.propertyView.setRowHeight(_item_id, 6)
            self.propertyView.setItem(_item_id, 0, QTableWidgetItem(_item))
            self.propertyView.setItem(_item_id, 1, QTableWidgetItem(str(_props[_item])))
            self.propertyView.setItemDelegateForRow(_item_id, QItemDelegate(self.propertyView))
            if not DICT_CHOOSE[_type][_item]:
                self.propertyView.setItemDelegateForRow(_item_id, EmptyDelegate(self.propertyView))
                self.propertyView.item(_item_id, 0).setBackground(qb)
                self.propertyView.item(_item_id, 1).setBackground(qb)

        if _type == "project":
            self.propertyView.cellChanged.connect(self._project_property_view_item_change)

        elif _type == "fsa":
            self.propertyView.cellChanged.connect(self._fsa_property_view_item_change)

        else:
            self.propertyView.cellChanged.connect(self._record_property_view_item_change)

        self.guiMain.interface.project_property_change.connect(self._property_passive_change)
        self.guiMain.interface.project_name_change.connect(self._property_project_name_change)
        self.guiMain.interface.fsa_property_change.connect(self._fsa_property_passive_change)
        self.guiMain.interface.fsa_name_change.connect(self._property_fsa_name_change)
        self.guiMain.interface.record_property_change.connect(self._record_property_passive_change)
        self.guiMain.interface.record_name_change.connect(self._property_record_name_change)

    def _tree_widget_item_select(self):
        if len(self.projectTreeView.selectedItems()) == 1:
            selected_item = self.projectTreeView.selectedItems()[0]
            if selected_item.parent() is None:
                self.guiMain.project.fsa_select(None)
                self.renew_property_table("project", self.guiMain.project.project_properties_get())
                self.guiMain.set_app_state(1, 0)
                self.guiMain.fsa_toolbox.toolBox.setEnabled(False)
            else:
                if selected_item.parent().text(0) == "FSA":
                    self.guiMain.project.fsa_select(selected_item.text(0))
                    self.renew_property_table("fsa", self.guiMain.project.fsa_get_properties(selected_item.text(0)))
                    self.guiMain.set_app_state(2, 0)
                    self.guiMain.fsa_toolbox.toolBox.setEnabled(True)
                if selected_item.parent().text(0) == "Record":
                    self.guiMain.project.fsa_select(None)
                    self.guiMain.set_app_state(3, 0)
                    self.guiMain.fsa_toolbox.toolBox.setEnabled(False)
                    self.guiMain.interface.record_selected.emit(selected_item.text(0))
        else:
            self.guiMain.project.fsa_select(None)
            self.renew_property_table("project", self.guiMain.project.project_properties_get())
            self.guiMain.set_app_state(1, 0)
            self.guiMain.fsa_toolbox.toolBox.setEnabled(False)

    def _project_property_view_item_change(self, _row, _col):
        if not self.locked:
            self.guiMain.do("proj-prop-alter",
                            self.propertyView.item(_row, 0).text(),
                            self.propertyView.item(_row, _col).text()
                            )

    def _fsa_property_view_item_change(self, _row, _col):
        if not self.locked:
            self.guiMain.do("fsa-prop-alter",
                            self.dockWidget_2.windowTitle(),
                            self.propertyView.item(_row, 0).text(),
                            self.propertyView.item(_row, _col).text()
                            )

    def _record_property_view_item_change(self, _row, _col):
        if not self.locked:
            self.guiMain.do("record-prop-alter",
                            self.dockWidget_2.windowTitle(),
                            self.propertyView.item(_row, 0).text(),
                            self.propertyView.item(_row, _col).text()
                            )

    def _property_project_name_change(self, new_name):
        self.project_root_item.setText(0, new_name)
        if self.current_type == "project":
            self.dockWidget_2.setWindowTitle(new_name)

    def _property_passive_change(self, _item, _value):
        if self.current_type == "project":
            if _item in self.property_table:
                self.locked = True
                self.propertyView.item(self.property_table[_item], 1).setText(str(_value))
                self.locked = False

    def _fsa_property_passive_change(self, _name, _item, _value):
        if self.current_type == "fsa":
            if self.dockWidget_2.windowTitle() == _name:
                if _item in self.property_table:
                    self.locked = True
                    self.propertyView.item(self.property_table[_item], 1).setText(str(_value))
                    self.locked = False

    def _record_property_passive_change(self, _name, _item, _value):
        if self.current_type == "record":
            if self.dockWidget_2.windowTitle() == _name:
                if _item in self.property_table:
                    self.locked = True
                    self.propertyView.item(self.property_table[_item], 1).setText(str(_value))
                    self.locked = False

    def _property_fsa_name_change(self, _old_name, _new_name):
        if _old_name in self.project_tree_fsa_items:
            self.project_tree_fsa_items[_old_name].setText(0, _new_name)
            self.project_tree_fsa_items[_new_name] = self.project_tree_fsa_items[_old_name]
            self.project_tree_fsa_items.pop(_old_name)

        if self.current_type == "fsa":
            if self.dockWidget_2.windowTitle() == _old_name:
                self.dockWidget_2.setWindowTitle(_new_name)

    def _property_record_name_change(self, _old_name, _new_name):
        if _old_name in self.project_tree_record_items:
            self.project_tree_record_items[_old_name].setText(0, _new_name)
            self.project_tree_record_items[_new_name] = self.project_tree_record_items[_old_name]
            self.project_tree_record_items.pop(_old_name)

        if self.current_type == "record":
            if self.dockWidget_2.windowTitle() == _old_name:
                self.dockWidget_2.setWindowTitle(_new_name)

    def _fsa_added(self, name):
        _new_tree_item = QTreeWidgetItem(self.project_tree_fsa_root_item)
        _new_tree_item.setText(0, name)
        self.project_tree_fsa_items[name] = _new_tree_item
        self.project_tree_fsa_root_item.addChild(_new_tree_item)

    def _record_added(self, name):
        _new_tree_item = QTreeWidgetItem(self.project_tree_record_root_item)
        _new_tree_item.setText(0, name)
        self.project_tree_record_items[name] = _new_tree_item
        self.project_tree_record_root_item.addChild(_new_tree_item)

    def _fsa_selected(self, name):
        if not self.locked:
            self.guiMain.interface.record_selected2.emit(None)
            self.locked = True
            if name is None or not name:
                if len(self.projectTreeView.selectedItems()) == 0 or self.projectTreeView.selectedItems()[0].parent() is None or self.projectTreeView.selectedItems()[0].parent().text(0) in ["Record"]:
                    pass
                else:
                    self.projectTreeView.clearSelection()
                    self.project_root_item.setSelected(True)
                    self.renew_property_table("project", self.guiMain.project.project_properties_get())
                    self.guiMain.set_app_state(1, 0)
            else:
                self.projectTreeView.clearSelection()
                self.project_tree_fsa_items[name].setSelected(True)
                self.project_tree_fsa_items[name].parent().setExpanded(True)
                self.project_tree_fsa_items[name].parent().parent().setExpanded(True)
                self.renew_property_table("fsa", self.guiMain.project.fsa_get_properties(name))
                self.guiMain.set_app_state(2, 0)
            self.locked = False

    def _record_selected(self, name):
        if not self.locked:
            self.locked = True
            self.guiMain.interface.record_selected2.emit(name)
            self.projectTreeView.clearSelection()
            if name is None or not name:
                self.project_root_item.setSelected(True)
                self.renew_property_table("project", self.guiMain.project.project_properties_get())
                self.guiMain.set_app_state(1, 0)
            else:
                self.project_tree_record_items[name].setSelected(True)
                self.project_tree_record_items[name].parent().setExpanded(True)
                self.project_tree_record_items[name].parent().parent().setExpanded(True)
                _res, _rcd = self.guiMain.project.record_get_properties(name)
                if _res:
                    self.renew_property_table("record", _rcd)
                else:
                    QMessageBox.critical(self, "Record Fetch Error", "Requested record does not exist, may have been renamed, moved or deleted. Open record browser to fix this.")
                self.guiMain.set_app_state(3, 0)
            self.locked = False

    def _fsa_removed(self, name):
        self.project_tree_fsa_root_item.removeChild(self.project_tree_fsa_items[name])
        del self.project_tree_fsa_items[name]

    def _record_removed(self, name):
        self.project_tree_record_root_item.removeChild(self.project_tree_record_items[name])
        del self.project_tree_record_items[name]

    def show(self):
        super(ResourceManager, self).show()
        self.guiMain.actionResource_Manager.setChecked(True)

    def closeEvent(self, a0: QCloseEvent) -> None:
        super(ResourceManager, self).closeEvent(a0)
        self.guiMain.actionResource_Manager.setChecked(False)
