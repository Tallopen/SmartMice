# -*- coding: utf-8 -*-
# created at: 2022/9/19 15:01
# author    : Gao Kai
# Email     : gaosimin1@163.com

from core.interface import GUIInterface
from core.project import Project
from functools import partial
from gui.variableManager import GUIVariableManager
from gui.FSAToolbox import FSAToolbox
from gui.monitorPanel import MonitorPanel
from gui.resourceManager import ResourceManager
from gui.fsaViewer import FSAViewer
from interface.action import History
import os.path
import pickle
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import shutil
from smtools.recordBrowser import RecordBrowser


APP_STATE_BASIC = 0
APP_STATE_PROJECT = 1
APP_STATE_FSA_SELECTED = 2
APP_STATE_RECORD_SELECTED = 3
APP_STATE_FSA_COMPILED = 4

RUN_STATE_BASIC = 0
RUN_STATE_RUNNING = 1
RUN_STATE_PAUSING = 2


class GUIMain(QMainWindow):

    def __init__(self):
        super(GUIMain, self).__init__()

        self.saved = True

        if not self.objectName():
            self.setObjectName(u"self")

        self.icon = QIcon("gui\\ico\\icon.ico")
        self.resize(500, 22)
        self.move(0, 0)
        self.setWindowIcon(self.icon)
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QSize(500, 0))
        self.setMaximumSize(QSize(16777215, 22))

        self.opened_fsa = ""

        # Subwidget pool
        self.resource_manager = ResourceManager(self)
        self.fsa_viewer = FSAViewer(self)
        self.fsa_toolbox = FSAToolbox(self)
        self.monitor_panel = MonitorPanel(self)
        self.variable_manager = GUIVariableManager(self)

        self.interface = None
        self.history = None
        self.project = None

        self.do_redo_undo_func = {
            "proj-prop-alter": (self._proj_prop_alter, self._proj_prop_alter_redo, self._proj_prop_alter_undo),
            "fsa-create": (self._fsa_create, self._fsa_recover, self._fsa_delete),
            "fsa-prop-alter": (self._fsa_prop_alter, self._fsa_prop_alter_redo, self._fsa_prop_alter_undo),
            "fsa-delete": (self._fsa_delete, self._fsa_delete, self._fsa_recover),
            "record-create": (self._record_create, self._record_recover, self._record_delete),
            "record-delete": (self._record_delete, self._record_delete, self._record_recover),
            "record-prop-alter": (self._record_prop_alter, self._record_prop_alter_redo, self._record_prop_alter_undo),
            "var-create": (self._var_create, self._var_recover, self._var_delete),
            "var-delete": (self._var_delete, self._var_delete, self._var_recover),
            "var-prop-change": (self._var_prop_alter, self._var_prop_alter_redo, self._var_prop_alter_undo),
            "node-create": (self._node_create, self._node_recover, self._node_delete),
            "bulk-delete": (self._bulk_delete, self._bulk_re_delete, self._bulk_recover),
            "bulk_node_move": (self._bulk_move, self.bulk_move_forward, self.bulk_move_back),
            "node-rename": (self._node_rename, self._node_rename_redo, self._node_rename_undo),
            "node-set-var": (self._fill_ph, self._fill_ph_redo, self._fill_ph_undo),
            "link-create": (self._link_create, self._link_add, self._link_remove)
        }

        # Create Menu
        self.actionNew_Project = QAction(self)
        self.actionNew_Project.triggered.connect(self.new_project)
        self.actionNew_Project.setObjectName(u"actionNew_Project")
        self.actionOpen_Project = QAction(self)
        self.actionOpen_Project.triggered.connect(lambda: self.open_project())
        self.actionOpen_Project.setObjectName(u"actionOpen_Project")
        self.actionSave_Project = QAction(self)
        self.actionSave_Project.triggered.connect(self.save_project)
        self.actionSave_Project.setObjectName(u"actionSave_Project")
        self.actionClose_Project = QAction(self)
        self.actionClose_Project.triggered.connect(self.close_project)
        self.actionClose_Project.setObjectName(u"actionClose_Project")
        self.actionExit = QAction(self)
        self.actionExit.triggered.connect(lambda: self.closeEvent(QCloseEvent()))
        self.actionExit.setObjectName(u"actionExit")

        # edit menu
        self.actionUndo = QAction(self)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionRedo = QAction(self)
        self.actionRedo.setObjectName(u"actionRedo")

        self.actionResource_Manager = QAction(self)
        self.actionResource_Manager.triggered.connect(lambda: self.toggle_window(self.actionResource_Manager, self.resource_manager))
        self.actionResource_Manager.setObjectName(u"actionResource_Manager")
        self.actionResource_Manager.setCheckable(True)

        self.actionFSA_Viewer = QAction(self)
        self.actionFSA_Viewer.triggered.connect(lambda: self.toggle_window(self.actionFSA_Viewer, self.fsa_viewer))
        self.actionFSA_Viewer.setObjectName(u"actionFSA_Viewer")
        self.actionFSA_Viewer.setCheckable(True)

        self.actionVariable_Manager = QAction(self)
        self.actionVariable_Manager.triggered.connect(lambda: self.toggle_window(self.actionVariable_Manager, self.variable_manager))
        self.actionVariable_Manager.setObjectName(u"actionVariable_Manager")
        self.actionVariable_Manager.setCheckable(True)

        self.actionMonitor_Array = QAction(self)
        self.actionMonitor_Array.triggered.connect(lambda: self.toggle_window(self.actionMonitor_Array, self.monitor_panel))
        self.actionMonitor_Array.setObjectName(u"actionMonitor_Array")
        self.actionMonitor_Array.setCheckable(True)

        self.actionFSA_Toolbar = QAction(self)
        self.actionFSA_Toolbar.triggered.connect(lambda: self.toggle_window(self.actionFSA_Toolbar, self.fsa_toolbox))
        self.actionFSA_Toolbar.setObjectName(u"actionFSA_Toolbar")
        self.actionFSA_Toolbar.setCheckable(True)

        # Tools menu
        self.actionAnalyser = QAction(self)
        self.actionRecord_Browser = QAction(self)
        self.actionRecord_Browser.triggered.connect(self._show_record_browser)
        self.actionData_Transfer = QAction(self)

        # FSA menu
        self.actionNew_FSA = QAction(self)
        self.actionNew_FSA.triggered.connect(lambda: self.do("fsa-create"))
        self.actionNew_FSA.setObjectName(u"actionNew_FSA")
        self.actionDelete_FSA = QAction(self)
        self.actionDelete_FSA.triggered.connect(lambda: self.do("fsa-delete", self.resource_manager.dockWidget_2.windowTitle()))
        self.actionDelete_FSA.setObjectName(u"actionDelete_FSA")
        self.actionDuplicate_FSA = QAction(self)
        self.actionDuplicate_FSA.setObjectName(u"actionDuplicate_FSA")
        self.actionData_Export = QAction(self)
        self.actionData_Export.setObjectName(u"actionData_Export")
        self.actionNew_Record = QAction(self)
        self.actionNew_Record.triggered.connect(lambda: self.do("record-create"))
        self.actionNew_Record.setObjectName(u"actionNew_Record")
        self.actionDelete_Record = QAction(self)
        self.actionDelete_Record.triggered.connect(lambda: self.do("record-delete", self.resource_manager.dockWidget_2.windowTitle()))
        self.actionDelete_Record.setObjectName(u"actionDelete_Record")
        self.actionLay_Out = QAction(self)
        self.actionLay_Out.setObjectName(u"actionLay_Out")
        self.actionRun = QAction(self)
        self.actionRun.setObjectName(u"actionRun")

        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 0))
        self.horizontalLayout = QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.centralWidget)
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 500, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuRecent_Project = QMenu(self.menuFile)
        self.menuRecent_Project.setObjectName(u"menuRecent_Project")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuFSA = QMenu(self.menubar)
        self.menuFSA.setObjectName(u"menuFSA")
        self.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuFSA.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addAction(self.actionOpen_Project)
        self.menuFile.addAction(self.menuRecent_Project.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Project)
        self.menuFile.addAction(self.actionClose_Project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionResource_Manager)
        self.menuEdit.addAction(self.actionFSA_Viewer)
        self.menuEdit.addAction(self.actionFSA_Toolbar)
        self.menuEdit.addAction(self.actionVariable_Manager)
        self.menuEdit.addAction(self.actionMonitor_Array)
        self.menuTools.addAction(self.actionAnalyser)
        self.menuTools.addAction(self.actionRecord_Browser)
        self.menuTools.addAction(self.actionData_Transfer)
        self.menuFSA.addAction(self.actionNew_FSA)
        self.menuFSA.addAction(self.actionDuplicate_FSA)
        self.menuFSA.addAction(self.actionDelete_FSA)
        self.menuFSA.addSeparator()
        self.menuFSA.addAction(self.actionNew_Record)
        self.menuFSA.addAction(self.actionDelete_Record)
        self.menuFSA.addSeparator()
        self.menuFSA.addAction(self.actionLay_Out)
        self.menuFSA.addSeparator()
        self.menuFSA.addAction(self.actionData_Export)
        self.menuFSA.addSeparator()
        self.menuFSA.addAction(self.actionRun)

        self.setWindowTitle(QCoreApplication.translate("self", u"SmartMice 2", None))
        self.setStatusTip("")
        self.actionNew_Project.setText(QCoreApplication.translate("self", u"New Project", None))
        self.actionOpen_Project.setText(QCoreApplication.translate("self", u"Open Project ...", None))
        self.actionSave_Project.setText(QCoreApplication.translate("self", u"Save Project", None))
        self.actionClose_Project.setText(QCoreApplication.translate("self", u"Close Project", None))
        self.actionExit.setText(QCoreApplication.translate("self", u"Exit", None))
        self.actionUndo.setText(QCoreApplication.translate("self", u"Undo ...", None))
        self.actionRedo.setText(QCoreApplication.translate("self", u"Redo ...", None))
        self.actionResource_Manager.setText(QCoreApplication.translate("self", u"Resource Manager", None))
        self.actionFSA_Viewer.setText(QCoreApplication.translate("self", u"FSA Viewer", None))
        self.actionVariable_Manager.setText(QCoreApplication.translate("self", u"Variable Manager", None))
        self.actionMonitor_Array.setText(QCoreApplication.translate("self", u"Run and Record Window", None))
        self.actionAnalyser.setText(QCoreApplication.translate("self", u"Data Preprocess Toolkit", None))
        self.actionRecord_Browser.setText(u"Browse Records")
        self.actionData_Transfer.setText(QCoreApplication.translate("self", u"Data Transfer", None))
        self.actionNew_FSA.setText(QCoreApplication.translate("self", u"New FSA", None))
        self.actionDelete_FSA.setText(QCoreApplication.translate("self", u"Delete FSA", None))
        self.actionDuplicate_FSA.setText(QCoreApplication.translate("self", u"Duplicate Selected FSA", None))
        self.actionData_Export.setText(QCoreApplication.translate("self", u"Raw Data Export ...", None))
        self.actionNew_Record.setText(QCoreApplication.translate("self", u"New Record", None))
        self.actionDelete_Record.setText(QCoreApplication.translate("self", u"Remove Selected Record", None))
        self.actionLay_Out.setText(QCoreApplication.translate("self", u"Automatic Layout", None))
        self.actionFSA_Toolbar.setText(QCoreApplication.translate("self", u"FSA Toolbox", None))
        self.actionRun.setText(QCoreApplication.translate("self", u"Run...", None))
        self.menuFile.setTitle(QCoreApplication.translate("self", u"File", None))
        self.menuRecent_Project.setTitle(QCoreApplication.translate("self", u"Recent Project", None))
        self.menuEdit.setTitle(QCoreApplication.translate("self", u"Edit", None))
        self.menuTools.setTitle(QCoreApplication.translate("self", u"Tools", None))
        self.menuFSA.setTitle(QCoreApplication.translate("self", u"FSA", None))

        self.menu_list = [
            self.actionNew_Project, self.actionOpen_Project, self.menuRecent_Project, self.actionClose_Project,
            self.actionNew_FSA, self.actionDelete_FSA, self.actionNew_Record, self.actionData_Export,
            self.actionDuplicate_FSA, self.actionDelete_Record, self.actionDuplicate_FSA,
            self.actionLay_Out, self.actionRun, self.actionSave_Project, self.actionResource_Manager,
            self.actionFSA_Viewer, self.actionVariable_Manager, self.actionMonitor_Array, self.actionFSA_Toolbar
        ]

        # Set window state
        self.actionUndo.setEnabled(False)
        self.actionRedo.setEnabled(False)
        self.actionSave_Project.setEnabled(False)
        self.set_app_state(APP_STATE_BASIC, RUN_STATE_BASIC)

        self.recent_project_list = []
        self.recent_actions = []

        self._update_recent_list(None)

    def _update_recent_list(self, new_path, addition=True):
        if os.path.isfile("recent.mainConfig"):
            with open("recent.mainConfig", 'rb') as f:
                self.recent_project_list = pickle.load(f)
        else:
            self.recent_project_list = []
            with open("recent.mainConfig", 'wb') as f:
                pickle.dump(self.recent_project_list, f)

        if new_path is not None:
            if new_path in self.recent_project_list:
                self.recent_project_list.remove(new_path)
            if addition:
                self.recent_project_list = [new_path, ] + self.recent_project_list

        while self.recent_actions:
            self.menuRecent_Project.removeAction(self.recent_actions.pop())

        # update self.menuRecent_Project
        _id = 1
        for _path in self.recent_project_list:
            _new_action = QAction(f"{_id}. " + _path)
            _new_action.triggered.connect(partial(self._open_recent, _path))
            self.recent_actions.append(_new_action)
            self.menuRecent_Project.addAction(_new_action)
            _id += 1

        with open("recent.mainConfig", 'wb') as f:
            pickle.dump(self.recent_project_list, f)

    def _open_recent(self, _path):
        if not os.path.isfile(_path):
            self._update_recent_list(_path, addition=False)

        self.open_project(_path)

    def set_app_state(self, app_state, run_state):

        for menu_item in self.menu_list:
            menu_item.setEnabled(False)

        if app_state > APP_STATE_BASIC:
            self.actionResource_Manager.setEnabled(True)
            self.actionFSA_Viewer.setEnabled(True)
            self.actionVariable_Manager.setEnabled(True)
            self.actionMonitor_Array.setEnabled(True)
            self.actionFSA_Toolbar.setEnabled(True)

        if run_state < RUN_STATE_RUNNING:
            self.monitor_panel.runButton.setEnabled(False)
            self.monitor_panel.pauseButton.setEnabled(False)
            self.monitor_panel.continueButton.setEnabled(False)
            self.monitor_panel.terminateButton.setEnabled(False)
            self.resource_manager.setEnabled(True)
            self.variable_manager.setEnabled(True)
            self.fsa_toolbox.setEnabled(True)
            self.actionNew_Project.setEnabled(True)
            self.actionOpen_Project.setEnabled(True)
            self.menuRecent_Project.setEnabled(True)

            if not self.saved:
                self.actionSave_Project.setEnabled(True)

            if APP_STATE_PROJECT <= app_state:
                self.actionClose_Project.setEnabled(True)

                self.actionNew_FSA.setEnabled(True)
                self.actionNew_Record.setEnabled(True)

                self.actionData_Export.setEnabled(True)

            if app_state == APP_STATE_FSA_SELECTED:
                self.actionDuplicate_FSA.setEnabled(True)
                self.actionDelete_FSA.setEnabled(True)
                self.actionRun.setEnabled(True)
                self.actionLay_Out.setEnabled(True)
                self.monitor_panel.runButton.setEnabled(True)

            if app_state == APP_STATE_RECORD_SELECTED:
                self.actionDelete_Record.setEnabled(True)

            if not (not self.opened_fsa):
                self.actionLay_Out.setEnabled(True)

        elif run_state == RUN_STATE_RUNNING:
            self.monitor_panel.runButton.setEnabled(False)
            self.monitor_panel.pauseButton.setEnabled(True)
            self.monitor_panel.continueButton.setEnabled(False)
            self.monitor_panel.terminateButton.setEnabled(False)
            self.resource_manager.setEnabled(False)
            self.variable_manager.setEnabled(False)
            self.fsa_toolbox.setEnabled(False)

        elif run_state == RUN_STATE_PAUSING:
            self.monitor_panel.runButton.setEnabled(False)
            self.monitor_panel.pauseButton.setEnabled(False)
            self.monitor_panel.continueButton.setEnabled(True)
            self.monitor_panel.terminateButton.setEnabled(True)
            self.resource_manager.setEnabled(False)
            self.variable_manager.setEnabled(False)
            self.fsa_toolbox.setEnabled(False)

    def new_project(self):
        if self.project is not None:
            if not self.close_project():
                return

        _contact, _ = QInputDialog.getText(self, "New Project", "Please enter your name below before proceeding on: ")
        if not _contact:
            QMessageBox.warning(self, "New Project", "Illegal name")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "New Project", filter="SmartMice 2 Project File (*.sm2)")
        if not (not filepath):
            if os.path.isfile(filepath):
                dir_name = os.path.dirname(filepath)
                nodes_path = os.path.join(dir_name, "nodes")
                if os.path.isdir(nodes_path):
                    shutil.rmtree(nodes_path)

            self.interface = GUIInterface(self)
            self._finish_binding_project()
            self.project = Project(filepath, contact=_contact, interface=self.interface)
            self._update_recent_list(filepath)
            del self.history
            self.actionUndo.setEnabled(False)
            self.actionRedo.setEnabled(False)
            self.history = History(self)
            self.set_app_state(APP_STATE_PROJECT, RUN_STATE_BASIC)

    @staticmethod
    def toggle_window(target_menu: QAction, target_window: QWidget):
        if target_menu.isChecked():
            target_window.show()
        else:
            target_window.close()

    def open_project(self, filepath=None):
        _res = True
        if self.project is not None:
            _res = self.close_project()

        if _res:
            if filepath is None:
                filepath, _ = QFileDialog.getOpenFileName(self, "Open Project", filter="SmartMice 2 Project File (*.sm2)")
            if not (not filepath):
                if os.path.isfile(filepath):
                    self.interface = GUIInterface(self)
                    self._finish_binding_project()

                    try:
                        self.project = Project(filepath, interface=self.interface)
                        self._update_recent_list(filepath)
                    except Exception as e:
                        QMessageBox.warning(self, "Open Project Error", f"File may be damaged: {e.args}")
                        self._update_recent_list(filepath, False)
                        self.project = None
                        return
                    del self.history
                    self.actionUndo.setEnabled(False)
                    self.actionRedo.setEnabled(False)
                    self.history = History(self)
                    self.set_app_state(APP_STATE_PROJECT, RUN_STATE_BASIC)
                else:
                    QMessageBox.warning(self, "Open Project Error", f"File does not exist: {filepath}")

    def _finish_binding_project(self):
        self.interface.run_end.connect(self.run_terminated)

        self.resource_manager.close()
        del self.resource_manager
        self.resource_manager = ResourceManager(self)
        self.interface.resource_manager_project_renew.connect(self.resource_manager.renew_project)
        self.interface.resource_manager_property_renew.connect(self.resource_manager.renew_property_table)
        self.resource_manager.show()
        self.actionResource_Manager.setChecked(True)

        self.fsa_viewer.close()
        del self.fsa_viewer
        self.fsa_viewer = FSAViewer(self)
        self.interface.resource_manager_project_renew.connect(self.fsa_viewer.open_project)
        self.interface.update_fsa_toolbox.connect(self.fsa_viewer.update_node_image_pool)
        self.interface.update_variable_create_toolbox.connect(self.fsa_viewer.update_var_image_pool)
        self.interface.node_added.connect(self.fsa_viewer.node_added)
        self.interface.node_removed.connect(self.fsa_viewer.node_removed)
        self.interface.bulk_added.connect(self.fsa_viewer.bulk_added)
        self.interface.bulk_removed.connect(self.fsa_viewer.bulk_removed)
        self.interface.bulk_move.connect(self.fsa_viewer.bulk_node_move)
        self.interface.fsa_name_change.connect(self.fsa_viewer.fsa_name_change)
        self.interface.node_rename.connect(self.fsa_viewer.node_rename)
        self.interface.ph_set_var.connect(self.fsa_viewer.ph_set_var)
        self.interface.var_renamed.connect(self.fsa_viewer.var_renamed)
        self.interface.link_add.connect(self.fsa_viewer.link_added)
        self.interface.link_remove.connect(self.fsa_viewer.link_removed)
        self.interface.run_begin.connect(self.fsa_viewer.enter_run_mode)
        self.interface.run_evoke.connect(self.fsa_viewer.enter_node)
        self.interface.run_end.connect(self.fsa_viewer.exit_run_mode)
        self.fsa_viewer.show()
        self.actionFSA_Viewer.setChecked(True)

        self.fsa_toolbox.close()
        del self.fsa_toolbox
        self.fsa_toolbox = FSAToolbox(self)
        self.interface.update_fsa_toolbox.connect(self.fsa_toolbox.update_pages)
        self.fsa_toolbox.show()
        self.actionFSA_Toolbar.setChecked(True)

        self.variable_manager.close()
        del self.variable_manager
        self.variable_manager = GUIVariableManager(self)
        self.interface.update_variable_create_toolbox.connect(self.variable_manager.update_variable_list)
        self.interface.variable_renew.connect(self.variable_manager.renew_variables)
        self.variable_manager.show()
        self.actionVariable_Manager.setChecked(True)

        self.monitor_panel.close()
        del self.monitor_panel
        self.monitor_panel = MonitorPanel(self)
        self.interface.record_selected2.connect(self.monitor_panel.record_selected)
        self.interface.record_name_change.connect(self.monitor_panel.record_name_change)
        self.interface.record_logged.connect(self.monitor_panel.record_table_add_last_line)
        self.interface.tick.connect(self.monitor_panel.tick)
        self.monitor_panel.show()

    def close_project(self):
        if not self.saved:
            returned_message = QMessageBox.information(self, "Close Project", "Current project has not been saved. Save it?",
                                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if returned_message == QMessageBox.StandardButton.Yes:
                self.save_project()
            elif returned_message == QMessageBox.StandardButton.Cancel:
                return False

        self.project = None
        self.resource_manager.close()
        self.fsa_viewer.close()
        self.fsa_toolbox.close()
        self.variable_manager.close()
        self.monitor_panel.close()
        self.set_app_state(APP_STATE_BASIC, RUN_STATE_BASIC)
        del self.history
        self.actionUndo.setEnabled(False)
        self.actionRedo.setEnabled(False)
        self.history = History(self)
        return True

    def run(self, record_name):
        result = self.project.run(record_name)
        if result[0]:
            self.set_app_state(APP_STATE_FSA_SELECTED, RUN_STATE_RUNNING)
        else:
            QMessageBox.critical(self, "Compilation Error", "During compilation, an error encountered:" + result[1])

    def pause(self):
        self.project.runner.pause()
        self.set_app_state(APP_STATE_FSA_SELECTED, RUN_STATE_PAUSING)

    def run_terminated(self):
        self.set_app_state(APP_STATE_FSA_SELECTED, RUN_STATE_BASIC)

    def save_project(self):
        if self.project is not None:
            self.project.save()
            self.saved = True
            self.actionSave_Project.setEnabled(False)

    def closeEvent(self, a0: QCloseEvent):
        if self.project is not None and not self.saved:
            returned_message = QMessageBox.information(self, "Close Project", "Current project has not been saved. Save it?",
                                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if returned_message == QMessageBox.StandardButton.Yes:
                self.project.clear_memory()
                self.save_project()
                quit(0)
            elif returned_message == QMessageBox.StandardButton.Cancel:
                a0.ignore()
            else:
                quit(0)
        else:
            quit(0)

    def do(self, _type, *args):
        _do_func, _redo_func, _undo_func = self.do_redo_undo_func[_type]
        _success, _param = _do_func(*args)
        if _success:
            if _param is not None:
                self.history.push(
                    lambda: _redo_func(_param, *args),
                    lambda: _undo_func(_param, *args)
                )
            else:
                self.history.push(
                    lambda: _redo_func(*args),
                    lambda: _undo_func(*args)
                )
            self.saved = False
            self.actionSave_Project.setEnabled(True)
        else:
            QMessageBox.critical(self, "Error", str(_param))

    def _proj_prop_alter(self, key, value):
        return self.project.project_property_set(key, value)

    def _proj_prop_alter_redo(self, _, key, value):
        return self.project.project_property_set(key, value)

    def _proj_prop_alter_undo(self, param, key, _):
        return self.project.project_property_set(key, param)

    def _fsa_prop_alter(self, fsa_name, key, value):
        return self.project.fsa_set_property(fsa_name, key, value)

    def _fsa_prop_alter_redo(self, _, fsa_name, key, value):
        return self.project.fsa_set_property(fsa_name, key, value)

    def _fsa_prop_alter_undo(self, param, fsa_name, key, value):
        if key == "name":
            return self.project.fsa_set_property(value, key, param)
        else:
            return self.project.fsa_set_property(fsa_name, key, param)

    def _record_prop_alter(self, fsa_name, key, value):
        return self.project.record_set_property(fsa_name, key, value)

    def _record_prop_alter_redo(self, _, fsa_name, key, value):
        return self.project.record_set_property(fsa_name, key, value)

    def _record_prop_alter_undo(self, param, fsa_name, key, value):
        if key == "name":
            return self.project.record_set_property(value, key, param)
        else:
            return self.project.record_set_property(fsa_name, key, param)

    def _var_prop_alter(self, var_name, key, value):
        return self.project.var_set_property(var_name, key, value)

    def _var_prop_alter_redo(self, _, var_name, key, value):
        return self.project.var_set_property(var_name, key, value)

    def _var_prop_alter_undo(self, param, var_name, key, value):
        if key == "name":
            return self.project.var_set_property(value, key, param)
        else:
            return self.project.var_set_property(var_name, key, param)

    def _fsa_create(self):
        return self.project.fsa_new()

    def _fsa_delete(self, name):
        return self.project.fsa_remove(name)

    def _fsa_recover(self, name):
        return self.project.fsa_add(name)

    def _var_create(self, _type, _):
        return self.project.var_new(_type)

    def _var_delete(self, name, _type, _):
        return self.project.var_remove(name)

    def _var_recover(self, name, _type, _):
        return self.project.var_add(name, False)

    def _record_create(self):
        returned_directory = QFileDialog.getExistingDirectory(self, "Create Record")
        if returned_directory and returned_directory is not None:
            return self.project.record_new(returned_directory)
        else:
            return False, "Not a directory."

    def _record_delete(self, name):
        return self.project.record_remove(name)

    def _record_recover(self, name):
        return self.project.record_add(name)

    def _node_create(self, _node_type, _fsa_name, _x, _y):
        return self.project.node_new(_node_type, _fsa_name, x=_x, y=_y)

    def _node_delete(self, name, _t, _fsa_name, *args):
        return self.project.node_remove(name, _fsa_name)

    def _node_recover(self, name, _, _fsa_name, *args):
        return self.project.node_add(name, False, _fsa_name)

    def _bulk_delete(self, node, fsa_name, links):
        return self.project.bulk_remove(node, links, fsa_name)

    def _bulk_re_delete(self, additional_links, node, fsa_name, links):
        link = list(set(list(additional_links) + list(links)))
        return self.project.bulk_remove(node, link, fsa_name)

    def _bulk_recover(self, additional_links, node, fsa_name, links):
        link = list(set(list(additional_links) + list(links)))
        return self.project.bulk_add(node, False, link, fsa_name)

    def _bulk_move(self, selected_fsa, _nodes, _new_position):
        return self.project.bulk_node_move(_nodes, _new_position, selected_fsa)

    def bulk_move_forward(self, _, selected_fsa, _nodes, _new_position):
        return self.project.bulk_node_move(_nodes, _new_position, selected_fsa)

    def bulk_move_back(self, _old_position, selected_fsa, _nodes, _):
        return self.project.bulk_node_move(_nodes, _old_position, selected_fsa)

    def _node_rename(self, _old_name, _new_name, _fsa_name):
        return self.project.node_set_property(_old_name, "name", _new_name, _fsa_name)

    def _node_rename_redo(self, _prop, _old_name, _new_name, _fsa_name):
        return self.project.node_set_property(_old_name, "name", _new_name, _fsa_name)

    def _node_rename_undo(self, _prop, _old_name, _new_name, _fsa_name):
        return self.project.node_set_property(_new_name, "name", _old_name, _fsa_name)

    def _fill_ph(self, node_name, placeholder_name, var_name, fsa_name):
        return self.project.node_set_var(node_name, placeholder_name, var_name, fsa_name)

    def _fill_ph_redo(self, _, node_name, placeholder_name, var_name, fsa_name):
        return self.project.node_set_var(node_name, placeholder_name, var_name, fsa_name)

    def _fill_ph_undo(self, original_var_name, node_name, placeholder_name, _, fsa_name=None):
        return self.project.node_set_var(node_name, placeholder_name, original_var_name, fsa_name)

    def _link_create(self, fsa_name, node1, output_name, node2):
        return self.project.link_new(node1, output_name, node2, fsa_name)

    def _link_add(self, link_id, fsa_name, *args):
        return self.project.link_add(link_id[0], False, fsa_name)

    def _link_remove(self, link_id, fsa_name, *args):
        if link_id[1] is not None:
            return self.project.link_add(link_id[1], False, fsa_name)
        else:
            return self.project.link_remove(link_id[0], fsa_name)

    def _show_record_browser(self):
        if self.project is not None:
            self._browser = RecordBrowser(self.project, self)
            self._browser.show()
        else:
            QMessageBox.critical(self, "Record browser error", "Record browser can't be started, since no project is open.")
