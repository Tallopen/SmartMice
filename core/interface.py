# -*- coding: utf-8 -*-
# created at: 2022/6/29 16:10
# author    : Gao Kai
# Email     : gaosimin1@163.com

from PyQt6.QtCore import *


class GUIInterface(QObject):

    resource_manager_project_renew = pyqtSignal(str, dict)
    resource_manager_property_renew = pyqtSignal(str, dict)
    update_fsa_toolbox = pyqtSignal(str, dict)
    update_variable_create_toolbox = pyqtSignal(str, dict)
    project_property_change = pyqtSignal(str, str)
    project_name_change = pyqtSignal(str)
    fsa_added = pyqtSignal(str)
    fsa_removed = pyqtSignal(str)
    fsa_selected = pyqtSignal(str)
    fsa_property_change = pyqtSignal(str, str, str)
    fsa_name_change = pyqtSignal(str, str)
    record_added = pyqtSignal(str)
    record_removed = pyqtSignal(str)
    record_selected = pyqtSignal(str)
    record_selected2 = pyqtSignal(str)
    record_property_change = pyqtSignal(str, str, str)
    record_name_change = pyqtSignal(str, str)
    variable_renew = pyqtSignal(dict)
    var_added = pyqtSignal(str, str)
    var_removed = pyqtSignal(str)
    var_renamed = pyqtSignal(str, str)
    var_property_change = pyqtSignal(str, str, str)
    node_added = pyqtSignal(str, str, dict)
    node_removed = pyqtSignal(str, str, list)
    bulk_added = pyqtSignal(str, list, dict, list, dict)
    bulk_removed = pyqtSignal(str, list, list)
    bulk_move = pyqtSignal(str, list, list, list)
    node_rename = pyqtSignal(str, str, str)
    ph_set_var = pyqtSignal(str, str, str, str)
    link_add = pyqtSignal(int, list, str)
    link_remove = pyqtSignal(int, str)
    run_begin = pyqtSignal()
    run_evoke = pyqtSignal(str)
    run_end = pyqtSignal()
    record_logged = pyqtSignal(list)
    tick = pyqtSignal(float)

    def __init__(self, gui_main, *args, **kwargs):
        super(GUIInterface, self).__init__(*args, **kwargs)
        self.guiMain = gui_main
