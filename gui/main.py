#********************************************************************
# wabash/gui/main.py
#
# Copyright (c) 2025  Stephen Rhodes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#*********************************************************************

import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget, QSplitter, QCheckBox
from PyQt6.QtCore import QSize, Qt, QSettings, QDir
from PyQt6.QtGui import QGuiApplication
import wabash
from enum import Enum
from pathlib import Path
from display import Display
from manager import Manager
from loguru import logger

class Style(Enum):
    DARK = 0
    LIGHT = 1

class List(QListWidget):
    def __init__(self):
        super().__init__()

    def setCurrentText(self, text):
        items = self.findItems(text, Qt.MatchFlag.MatchExactly)
        if items:
            self.setCurrentItem(items[0])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.manager = Manager(self)

        QDir.addSearchPath("image", self.getLocation() + "/gui/resources/")
        self.settings = QSettings("wabash", "gui")
        #self.settings.clear()
        logger.debug(f'Settings loaded from file {self.settings.fileName()} using format {self.settings.format()}')
        self.geometryKey = "MainWindow/geometry"
        self.splitKey = "MainWindow/split"
        self.reconnectKey = "MainWindow/reconnect"

        self.setWindowTitle("Threads Example")
        self.setMinimumSize(QSize(320, 240))

        btnAdd = QPushButton("Add Thread")
        btnAdd.clicked.connect(self.btnAddClicked)

        btnEnd = QPushButton("End Thread")
        btnEnd.clicked.connect(self.btnEndClicked)

        btnCloseAll = QPushButton("Close All")
        btnCloseAll.clicked.connect(self.btnCloseAllClicked)

        btnStartNine = QPushButton("Start Nine")
        btnStartNine.clicked.connect(self.btnStartNineClicked)    

        btnTest = QPushButton("Test")
        btnTest.clicked.connect(self.btnTestClicked)

        self.chkReconnect = QCheckBox("Reconnect")
        self.chkReconnect.setChecked(int(self.settings.value(self.reconnectKey, 0)))
        self.chkReconnect.stateChanged.connect(self.chkReconnectChecked)

        size = QSize(self.height(), self.height())
        self.display = Display(self, size)

        self.list = List()

        pnlControl = QWidget()
        lytControl = QGridLayout(pnlControl)
        lytControl.addWidget(btnAdd,            0, 0 ,1, 1)
        lytControl.addWidget(btnEnd,            1, 0, 1, 1)
        lytControl.addWidget(btnCloseAll,       0, 1, 1, 1)
        lytControl.addWidget(btnStartNine,      1, 1, 1, 1)
        lytControl.addWidget(btnTest,           2, 0, 1, 1)
        lytControl.addWidget(self.chkReconnect, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        lytControl.addWidget(self.list,         3, 0, 1, 2)

        self.split = QSplitter()
        self.split.addWidget(pnlControl)
        self.split.addWidget(self.display)
        self.split.setStretchFactor(1, 10)
        self.split.splitterMoved.connect(self.splitterMoved)
        if splitterState := self.settings.value(self.splitKey):
            self.split.restoreState(splitterState)
        self.setCentralWidget(self.split)

        self.setStyleSheet(self.style(Style.DARK))        
        if rect := self.settings.value(self.geometryKey):
            if screen := QGuiApplication.screenAt(rect.topLeft()):
                self.setGeometry(rect)

    def startThread(self, name=None):
        if not name:
            name = self.name()
        try:
            thread = wabash.Thread(name)
            thread.setPayload(320, 180, 3)
            thread.finish = self.manager.removeThread
            thread.reconnect = self.chkReconnect.isChecked()
            self.manager.startThread(thread)
        except Exception as ex:
            logger.error(ex)

    def splitterMoved(self, pos, index):
        self.settings.setValue(self.splitKey, self.split.saveState())

    def btnAddClicked(self):
        self.startThread()

    def btnEndClicked(self):
        if item := self.list.currentItem():
            if thread := self.manager.threads.get(item.text()):
                thread.running = False

    def btnCloseAllClicked(self):
        self.manager.closeAllThreads()

    def btnStartNineClicked(self):
        for i in range(9):
            self.startThread()

    def btnTestClicked(self):
        for name in self.manager.threads:
            rect = self.manager.displayRect(name, self.display.size()).toRect()
            ordinal = self.manager.ordinals[name]
            width, height = self.manager.computeRowsCols(self.display.size(), 1.77)
            print(name, width, height, ordinal, rect)

    def chkReconnectChecked(self, state):
        self.settings.setValue(self.reconnectKey, state)

    def name(self):
        result = f"thread_{self.counter:0{3}d}"
        self.counter += 1
        return result
    
    def closeEvent(self, event):
        self.manager.closeAllThreads()
        self.settings.setValue(self.geometryKey, self.geometry())
        super().closeEvent(event)

    def getLocation(self):
        path = Path(os.path.dirname(__file__))
        return str(path.parent.absolute())
    
    def style(self, appearance):
        path = Path(os.path.dirname(__file__))
        filename = str(path.parent.absolute()) + "/gui/resources/darkstyle.qss"
        with open(filename, 'r') as file:
            strStyle = file.read()

        match appearance:
            case Style.DARK:
                blDefault = "#5B5B5B"
                bmDefault = "#4B4B4B"
                bdDefault = "#3B3B3B"
                flDefault = "#C6D9F2"
                fmDefault = "#9DADC2"
                fdDefault = "#808D9E"
                slDefault = "#FFFFFF"
                smDefault = "#DDEEFF"
                sdDefault = "#306294"
                isDefault = "#323232"
                strStyle = strStyle.replace("background_light",  blDefault)
                strStyle = strStyle.replace("background_medium", bmDefault)
                strStyle = strStyle.replace("background_dark",   bdDefault)
                strStyle = strStyle.replace("foreground_light",  flDefault)
                strStyle = strStyle.replace("foreground_medium", fmDefault)
                strStyle = strStyle.replace("foreground_dark",   fdDefault)
                strStyle = strStyle.replace("selection_light",   slDefault)
                strStyle = strStyle.replace("selection_medium",  smDefault)
                strStyle = strStyle.replace("selection_dark",    sdDefault)
                strStyle = strStyle.replace("selection_item",    isDefault)
            case Style.LIGHT:
                blDefault = "#AAAAAA"
                bmDefault = "#CCCCCC"
                bdDefault = "#FFFFFF"
                flDefault = "#111111"
                fmDefault = "#222222"
                fdDefault = "#999999"
                slDefault = "#111111"
                smDefault = "#222222"
                sdDefault = "#999999"
                isDefault = "#888888"
                strStyle = strStyle.replace("background_light",  blDefault)
                strStyle = strStyle.replace("background_medium", bmDefault)
                strStyle = strStyle.replace("background_dark",   bdDefault)
                strStyle = strStyle.replace("foreground_light",  flDefault)
                strStyle = strStyle.replace("foreground_medium", fmDefault)
                strStyle = strStyle.replace("foreground_dark",   fdDefault)
                strStyle = strStyle.replace("selection_light",   slDefault)
                strStyle = strStyle.replace("selection_medium",  smDefault)
                strStyle = strStyle.replace("selection_dark",    sdDefault)
                strStyle = strStyle.replace("selection_item",    isDefault)

        return strStyle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
