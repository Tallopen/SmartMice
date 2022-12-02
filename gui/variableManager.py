# -*- coding: utf-8 -*-
# created at: 2022/9/21 21:15
# author    : Gao Kai
# Email     : gaosimin1@163.com


from functools import partial
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os.path


class GUIVariableManager(QWidget):

    def __init__(self, gui_main):
        super(GUIVariableManager, self).__init__()

        self.guiMain = gui_main
        self.setWindowIcon(gui_main.icon)

        self.setObjectName(u"VariableManager")
        self.resize(300, 420)
        self.move(1120, 60)
        vertical_layout = QVBoxLayout(self)
        vertical_layout.setSpacing(0)
        vertical_layout.setObjectName(u"vertical_layout")
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.dockWidget = QDockWidget(self)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_4 = QLabel(self.dockWidgetContents)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.createVariableTab = QTabWidget(self.dockWidgetContents)
        self.createVariableTab.setObjectName(u"createVariableTab")
        self.createVariableTab.setMinimumSize(QSize(0, 80))
        self.createVariableTab.setMaximumSize(QSize(16777215, 80))
        self.createVariableTab.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_3.addWidget(self.createVariableTab)

        self.variableTree = QTreeWidget(self.dockWidgetContents)
        self.variableTree.setObjectName(u"variableTree")

        self.verticalLayout_3.addWidget(self.variableTree)

        self.dockWidget.setWidget(self.dockWidgetContents)

        vertical_layout.addWidget(self.dockWidget)

        self.dockWidget_2 = QDockWidget(self)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidget_2.setMinimumSize(QSize(241, 128))
        self.dockWidget_2.setMaximumSize(QSize(524287, 128))
        self.dockWidget_2.setStyleSheet(u"")
        self.dockWidget_2.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.gridLayout = QGridLayout(self.dockWidgetContents_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.Value = QLineEdit(self.dockWidgetContents_2)
        self.Value.setObjectName(u"Value")

        self.gridLayout.addWidget(self.Value, 2, 1, 1, 1)

        self.label_2 = QLabel(self.dockWidgetContents_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.line = QFrame(self.dockWidgetContents_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)

        self.label = QLabel(self.dockWidgetContents_2)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)

        self.line_2 = QFrame(self.dockWidgetContents_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 1, 1, 1, 1)

        self.variableName = QLineEdit(self.dockWidgetContents_2)
        self.variableName.setObjectName(u"variableName")

        self.gridLayout.addWidget(self.variableName, 0, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label_3 = QLabel(self.dockWidgetContents_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.openVariableEditor = QPushButton(self.dockWidgetContents_2)
        self.openVariableEditor.setObjectName(u"openVariableEditor")

        self.horizontalLayout.addWidget(self.openVariableEditor)

        self.gridLayout.addLayout(self.horizontalLayout, 4, 1, 1, 1)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)

        vertical_layout.addWidget(self.dockWidget_2)

        self.setWindowTitle(QCoreApplication.translate("VariableManager", u"Variable Manager", None))
        self.dockWidget.setWindowTitle(QCoreApplication.translate("VariableManager", u"Variable Viewer", None))
        self.label_4.setText(QCoreApplication.translate("VariableManager", u"Create variables by clicking on buttons below:", None))

        self.dockWidget_2.setWindowTitle(QCoreApplication.translate("VariableManager", u"Variable Editor", None))
        self.label_2.setText(QCoreApplication.translate("VariableManager", u"Variable Name: ", None))
        self.label.setText(QCoreApplication.translate("VariableManager", u"Initial Value: ", None))
        self.label_3.setText(QCoreApplication.translate("VariableManager", u"Or: ", None))
        self.openVariableEditor.setText(QCoreApplication.translate("VariableManager", u"Open Editor ...", None))

        self.createVariableTab.setCurrentIndex(0)

        self.variableTree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.variableTree.customContextMenuRequested.connect(self._show_variable_tree_context_menu)

        self.locked = False

        self.variable_tree_context_menu = QMenu(self)

        self.actionSort = self.variable_tree_context_menu.addAction('Sort')
        self.actionSort.triggered.connect(lambda: self.variableTree.sortByColumn(0, Qt.SortOrder.AscendingOrder))
        self.variable_tree_context_menu.addSeparator()
        self.actionDeleteSelectedVar = self.variable_tree_context_menu.addAction('Delete selected variable')
        self.actionDeleteSelectedVar.triggered.connect(self._remove_var)
        self.actionDeleteSelectedVar.setEnabled(False)

        self.variableTree.setHeaderHidden(True)
        self.variableTree.itemSelectionChanged.connect(self._variable_selected)

        self.variableName.returnPressed.connect(self._name_change)

        self.varIcon = dict()
        self.editor = dict()
        self.filter_func = dict()

        self.reg_variables = dict()
        self.reg_variable_type = dict()

        self.Value.setEnabled(False)
        self.openVariableEditor.setEnabled(False)
        self.variableName.setEnabled(False)

    def _remove_var(self):
        for _item in self.variableTree.selectedItems():
            self.guiMain.do(
                "var-delete", _item.text(0), self.reg_variable_type[_item.text(0)], None
            )

    def _show_variable_tree_context_menu(self, pos):
        self.variable_tree_context_menu.move(self.pos() + self.variableTree.pos() + QPoint(0, 40) + pos)
        if len(self.variableTree.selectedItems()):
            self.actionDeleteSelectedVar.setEnabled(True)
        else:
            self.actionDeleteSelectedVar.setEnabled(False)
        self.variable_tree_context_menu.show()

    def update_variable_list(self, _icon_path, variable_dict: dict):
        # iterate through node class
        _sorted_var_class = dict()
        for _key, _value in variable_dict.items():
            var_group = _value.gui_param["group"]
            if var_group not in _sorted_var_class:
                _sorted_var_class[var_group] = []
            _sorted_var_class[var_group].append(_key)
            if _value.value_editor is None:
                self.editor[_key] = None
                self.filter_func[_key] = _value.filter_func
            else:
                self.editor[_key] = _value.value_editor
                self.filter_func[_key] = None

        for _key in _sorted_var_class:
            new_page = QWidget()
            _hor_layout = QHBoxLayout(new_page)
            _hor_layout.setSpacing(0)
            self.createVariableTab.addTab(new_page, _key)
            self.createVariableTab.setTabText(self.createVariableTab.indexOf(new_page), _key)

            button_counter_col = 0
            for _var_name in _sorted_var_class[_key]:
                button_icon = QIcon(os.path.join(_icon_path, f"{_var_name}.png"))
                self.varIcon[_var_name] = button_icon
                _new_button = QToolButton(new_page)
                _new_button.setFixedSize(30, 30)
                _new_button.setIconSize(QSize(27, 27))
                _new_button.setIcon(button_icon)
                _new_button.setToolTip(variable_dict[_var_name].gui_param["menu_name"])
                _new_button.setToolTipDuration(0)

                _new_button.clicked.connect(partial(self.guiMain.do, "var-create", _var_name))

                _hor_layout.addWidget(_new_button)
                button_counter_col += 1

    def renew_variables(self, _v):
        for _name in _v:
            _new_item = QTreeWidgetItem(self.variableTree)
            _new_item.setText(0, _name)
            _new_item.setIcon(0, self.varIcon[_v[_name]["type"]])
            self.variableTree.addTopLevelItem(_new_item)
            self.reg_variables[_name] = _new_item
            self.reg_variable_type[_name] = _v[_name]["type"]
        self.guiMain.interface.var_added.connect(self._variable_added)
        self.guiMain.interface.var_renamed.connect(self._variable_name_changed)
        self.guiMain.interface.var_removed.connect(self._variable_removed)
        self.guiMain.interface.var_property_change.connect(self._variable_value_passive_change)

    def _variable_added(self, _type, _name):
        _new_item = QTreeWidgetItem(self.variableTree)
        _new_item.setText(0, _name)
        _new_item.setIcon(0, self.varIcon[_type])
        self.variableTree.addTopLevelItem(_new_item)
        self.reg_variables[_name] = _new_item
        self.reg_variable_type[_name] = _type

    def _variable_removed(self, _name):
        self.variableTree.takeTopLevelItem(self.variableTree.indexOfTopLevelItem(self.reg_variables[_name]))
        del self.reg_variables[_name]
        del self.reg_variable_type[_name]

    def _variable_selected(self):
        self.locked = True
        if len(self.variableTree.selectedItems()) == 1:
            selected_item = self.variableTree.selectedItems()[0]
            self.renew_variable_display(selected_item)
            self.variableName.setEnabled(True)
            self.selected_variable = selected_item.text(0)
        else:
            self.selected_variable = None
            self.Value.setText("")
            self.Value.setEnabled(False)
            self.variableName.setText("")
            self.variableName.setEnabled(False)
            self.openVariableEditor.setEnabled(False)
        self.locked = False

    def renew_variable_display(self, selected_item):
        self.locked = True

        try:
            self.Value.disconnect()
        except TypeError:
            pass

        try:
            self.openVariableEditor.disconnect()
        except TypeError:
            pass

        self.variableName.setText(selected_item.text(0))
        _var_type = self.reg_variable_type[selected_item.text(0)]
        if self.editor[_var_type] is None:
            self.Value.setEnabled(True)
            self.Value.returnPressed.connect(self._value_change)
            self.Value.setText(str(self.guiMain.project.var_get_properties(selected_item.text(0))[1]["value"]))
            self.openVariableEditor.setEnabled(False)
        else:
            self.Value.setText("")
            self.Value.setEnabled(False)
            self.openVariableEditor.setEnabled(True)
            self.openVariableEditor.clicked.connect(lambda: self.update_variable_value(selected_item.text(0)))
        self.locked = False

    def update_variable_value(self, variable_name):
        ret_v = self.guiMain.project.get_var_editor(variable_name)
        if ret_v[1] and ret_v[0] is not None:
            self.guiMain.do(
                "var-prop-change", variable_name, "value", ret_v[0]
            )

    def _name_change(self):
        if not self.locked:
            self.guiMain.do(
                "var-prop-change", self.selected_variable, "name", self.variableName.text()
            )
            self.variableName.clearFocus()

    def _value_change(self):
        if not self.locked:
            self.guiMain.do(
                "var-prop-change", self.selected_variable, "value", self.Value.text()
            )
            self.Value.clearFocus()

    def _variable_name_changed(self, _name, new_name):
        if _name in self.reg_variables:
            self.reg_variables[_name].setText(0, new_name)
        self.reg_variables[new_name] = self.reg_variables[_name]
        self.reg_variables.pop(_name)
        self.reg_variable_type[new_name] = self.reg_variable_type[_name]
        self.reg_variable_type.pop(_name)
        if _name == self.selected_variable:
            self.selected_variable = new_name

    def _variable_value_passive_change(self, _name, _key, _new_value):
        if _name == self.selected_variable:
            self.locked = True
            if _key == "name":
                self.variableName.setText(_new_value)
            elif _key == "value":
                if self.Value.isEnabled():
                    self.Value.setText(_new_value)
                else:
                    self.Value.setText("")
            self.locked = False

    def show(self):
        super(GUIVariableManager, self).show()
        self.guiMain.actionVariable_Manager.setChecked(True)

    def closeEvent(self, a0: QCloseEvent) -> None:
        super(GUIVariableManager, self).closeEvent(a0)
        self.guiMain.actionVariable_Manager.setChecked(False)
