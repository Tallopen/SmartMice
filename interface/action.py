# -*- coding: utf-8 -*-
# created at: 2022/9/20 23:12
# author    : Gao Kai
# Email     : gaosimin1@163.com


class HistoryChainNode:

    def __init__(self, content):

        self.next = None
        self.last = None
        self.content = content


class History:

    def __init__(self, gui_main):

        self.current_ref = HistoryChainNode(None)
        self.gui_main = gui_main

        gui_main.actionRedo.disconnect()
        gui_main.actionUndo.disconnect()

        gui_main.actionRedo.triggered.connect(self.redo)
        gui_main.actionUndo.triggered.connect(self.undo)

    def push(self, _redo_action, _undo_action):

        _new_chain_node = HistoryChainNode((_redo_action, _undo_action))
        _new_chain_node.last = self.current_ref
        self.current_ref.next = _new_chain_node
        self.current_ref = self.current_ref.next
        self.gui_main.actionUndo.setEnabled(True)
        self.gui_main.actionRedo.setEnabled(False)

    def clear(self):

        self.current_ref = None

    def check_has_next(self):

        return not (self.current_ref.next is None)

    def check_has_last(self):

        return not (self.current_ref.last is None)

    def redo(self):

        if self.check_has_next():
            self.current_ref.next.content[0]()
            self.current_ref = self.current_ref.next
            self.gui_main.actionUndo.setEnabled(True)

        self.gui_main.actionRedo.setEnabled(self.check_has_next())
        self.gui_main.saved = False
        self.gui_main.actionSave_Project.setEnabled(True)

    def undo(self):

        if self.check_has_last():
            self.current_ref.content[1]()
            self.current_ref = self.current_ref.last
            self.gui_main.actionRedo.setEnabled(True)

        self.gui_main.actionUndo.setEnabled(self.check_has_last())
        self.gui_main.saved = False
        self.gui_main.actionSave_Project.setEnabled(True)
