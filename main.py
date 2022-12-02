# -*- coding: utf-8 -*-
# created at: 2022/6/29 16:05
# author    : Gao Kai
# Email     : gaosimin1@163.com

"""
import core.project

p = core.project.Project("example\\test", contact="Gao Kai")
p.fsa_new(name="test")
p.node_new("StartNode", name="start1")
p.node_new("EvalNode", name="calc1")
p.node_new("IfNode", name="if1")
p.node_new("EndNode", name="end1")

p.link_new("start1", "Begin", "if1")
p.link_new("if1", "True", "calc1")
p.link_new("calc1", "Done", "if1")
p.link_new("if1", "False", "end1")

p.var_new("MExp", name="plusTest")
p.var_new("MExp", name="ifTest")
p.var_new("MNum", name="plusResult", logged=True, value=1)
p.var_set_property("plusTest", "value", "{plusResult}+1")
p.var_set_property("ifTest", "value", "{plusResult} < 2")

p.node_set_var("calc1", "meta expression", "plusTest")
p.node_set_var("calc1", "return", "plusResult")
p.node_set_var("if1", "meta expression", "ifTest")

p.record_new("example\\rcd", name="test_record")
p.run("test_record")

p.save()
"""

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QSplashScreen
    from PyQt6.QtGui import QPixmap
    from gui.guiMain import GUIMain

    app = QApplication([])

    splash = QSplashScreen(QPixmap("gui/ico/splash.png"))
    splash.show()

    ex = GUIMain()
    splash.finish(ex)
    splash.deleteLater()
    ex.show()

    sys.exit(app.exec())
