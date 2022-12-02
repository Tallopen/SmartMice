# -*- coding: utf-8 -*-
# created at: 2022/9/21 21:53
# author    : Gao Kai
# Email     : gaosimin1@163.com


from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from gui.utilities import get_record_name


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, _w, _s, _m):
        return None


class MonitorPanel(QWidget):

    def __init__(self, gui_main):

        super(MonitorPanel, self).__init__()

        self.guiMain = gui_main

        self.resize(430, 295)
        self.move(0, 492)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.runButton = QToolButton(self)
        self.runButton.clicked.connect(self.run)
        self.runButton.setObjectName(u"toolButton_2")

        self.horizontalLayout.addWidget(self.runButton)

        self.pauseButton = QToolButton(self)
        self.pauseButton.setObjectName(u"toolButton_3")

        self.horizontalLayout.addWidget(self.pauseButton)

        self.continueButton = QToolButton(self)
        self.continueButton.setObjectName(u"toolButton")

        self.horizontalLayout.addWidget(self.continueButton)

        self.terminateButton = QToolButton(self)
        self.terminateButton.setObjectName(u"toolButton_4")

        self.horizontalLayout.addWidget(self.terminateButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.lcdNumber = QLCDNumber(self)
        self.lcdNumber.setObjectName(u"lcdNumber")
        self.lcdNumber.setMinimumSize(QSize(60, 0))
        self.lcdNumber.setMaximumSize(QSize(60, 16777215))
        self.lcdNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.lcdNumber.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.horizontalLayout.addWidget(self.lcdNumber)

        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.lcdNumber_2 = QLCDNumber(self)
        self.lcdNumber_2.setObjectName(u"lcdNumber_2")
        self.lcdNumber_2.setMinimumSize(QSize(28, 0))
        self.lcdNumber_2.setMaximumSize(QSize(28, 16777215))
        self.lcdNumber_2.setDigitCount(2)
        self.lcdNumber_2.setFrameShape(QFrame.Shape.NoFrame)
        self.lcdNumber_2.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)

        self.horizontalLayout.addWidget(self.lcdNumber_2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableWidget = QTableWidget(self)

        self.tableWidget.setColumnCount(4)

        _time_col = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, _time_col)
        _type_col = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, _type_col)
        _name_col = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, _name_col)
        _value_col = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, _value_col)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout.addWidget(self.tableWidget)

        self.setWindowTitle(QCoreApplication.translate("Form", u"Run and Record", None))
        self.continueButton.setToolTip(QCoreApplication.translate("Form", u"Continue", None))
        self.continueButton.setIcon(QIcon("gui\\src\\Continue.png"))
        self.runButton.setToolTip(QCoreApplication.translate("Form", u"Run", None))
        self.runButton.setIcon(QIcon("gui\\src\\Run.png"))
        self.pauseButton.setToolTip(QCoreApplication.translate("Form", u"Pause", None))
        self.pauseButton.setIcon(QIcon("gui\\src\\Pause.png"))
        self.terminateButton.setToolTip(QCoreApplication.translate("Form", u"Terminate", None))
        self.terminateButton.setIcon(QIcon("gui\\src\\Terminate.png"))
        self.label_2.setText(QCoreApplication.translate("Form", u"Elapsed Time:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u":", None))

        _time_col = self.tableWidget.horizontalHeaderItem(0)
        _time_col.setText(QCoreApplication.translate("Form", u"Relative Time", None))
        _type_col = self.tableWidget.horizontalHeaderItem(1)
        _type_col.setText(QCoreApplication.translate("Form", u"Message Type", None))
        _name_col = self.tableWidget.horizontalHeaderItem(2)
        _name_col.setText(QCoreApplication.translate("Form", u"Message Name", None))
        _value_col = self.tableWidget.horizontalHeaderItem(3)
        _value_col.setText(QCoreApplication.translate("Form", u"Value", None))

        self.tableWidget.setItemDelegate(EmptyDelegate(self.tableWidget))

        self.record_name = None

    def run(self):
        _brand_new_record = self.guiMain.project.get_brand_new_records()
        designated_record = get_record_name(_brand_new_record)[0]
        if designated_record:
            self.guiMain.run(designated_record)

    def record_selected(self, record_name):
        self.record_name = record_name
        self.setWindowTitle(f"Run and Record ({self.record_name})")

        self.record_table_thorough_renew(record_name)

    def record_name_change(self, old_name, new_name):
        if self.record_name == old_name:
            self.record_name = new_name
            self.setWindowTitle(f"Run and Record ({self.record_name})")

    def record_deleted(self, name):
        if self.record_name == name:
            self.record_name = None
            self.setWindowTitle(f"Run and Record ()")

    def record_table_thorough_renew(self, name):

        for row_id in range(self.tableWidget.rowCount())[::-1]:
            self.tableWidget.removeRow(row_id)

        # record content
        if name:
            _record_content = self.guiMain.project.record_content_load(name)
            if _record_content[0]:
                if _record_content[1] is not None:
                    for _item_id, _item in enumerate(_record_content[1]["record"]):
                        self.tableWidget.insertRow(_item_id)
                        self.tableWidget.setRowHeight(_item_id, 6)
                        for _i in range(4):
                            self.tableWidget.setItem(_item_id, _i, QTableWidgetItem(str(_item[_i])))

                    self.tableWidget.scrollToBottom()

                # LCD
                _record_last_time = self.guiMain.project.record_get_properties(name)["length"]
                self.lcdNumber.display(_record_last_time // 60)
                self.lcdNumber_2.display(int(_record_last_time % 60))

    def record_table_add_last_line(self, content):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        _item_id = self.tableWidget.rowCount()-1
        for _i in range(4):
            self.tableWidget.setItem(_item_id, _i, QTableWidgetItem(str(content[_i])))

    def tick(self, _time):
        self.lcdNumber.display(_time // 60)
        self.lcdNumber_2.display(int(_time % 60))

    def show(self):
        super(MonitorPanel, self).show()
        self.guiMain.actionMonitor_Array.setChecked(True)

    def closeEvent(self, a0: QCloseEvent) -> None:
        super(MonitorPanel, self).closeEvent(a0)
        self.guiMain.actionMonitor_Array.setChecked(False)
