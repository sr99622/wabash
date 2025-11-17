import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget, QSplitter, QCheckBox, QComboBox, QLabel, QSpinBox
from PyQt6.QtCore import QSize, Qt, QSettings, QDir, QStandardPaths, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QGuiApplication, QCloseEvent, QIcon
import wabash
from enum import Enum
from pathlib import Path
from .manager import Manager
from wabash.gui import Display
from wabash.gui.components import FileSelector
from .memoryplot import MemoryPlot
from loguru import logger
import pyqtgraph as pg
import importlib.metadata
import traceback

class List(QListWidget):
    def __init__(self):
        super().__init__()

    def setCurrentText(self, text):
        if items := self.findItems(text, Qt.MatchFlag.MatchExactly):
            self.setCurrentItem(items[0])

class StreamPanel(QWidget):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw
        self.manager = Manager(self.mw)
        self.counter = 0
        QApplication.instance().aboutToQuit.connect(self.onClose)

        self.reconnectKey = "MainWindow/reconnect"
        self.inferKey = "MainWindow/infer"
        self.apiKey = "MainWindow/API"

        self.fileSelector = FileSelector(self.mw, "File")

        btnAdd = QPushButton("Add Stream")
        btnAdd.clicked.connect(self.btnAddClicked)

        btnEnd = QPushButton("End Stream")
        btnEnd.clicked.connect(self.btnEndClicked)

        btnCloseAll = QPushButton("Close All")
        btnCloseAll.clicked.connect(self.btnCloseAllClicked)

        btnStartNine = QPushButton("Start Nine")
        btnStartNine.clicked.connect(self.btnStartNineClicked)

        btnTest = QPushButton("Test")
        btnTest.clicked.connect(self.btnTestClicked)

        self.chkReconnect = QCheckBox("Reconnect")
        self.chkReconnect.setChecked(int(self.mw.settings.value(self.reconnectKey, 0)))
        self.chkReconnect.stateChanged.connect(self.chkReconnectChecked)

        self.cmbAPI = QComboBox()
        self.cmbAPI.addItems(["PyTorch", "OpenVINO", "rknn"])
        self.cmbAPI.setCurrentText(self.mw.settings.value(self.apiKey, "PyTorch"))
        self.cmbAPI.currentTextChanged.connect(self.cmbAPIChanged)

        self.chkInfer = QCheckBox("Infer")
        self.chkInfer.setChecked(int(self.mw.settings.value(self.inferKey, 0)))
        self.chkInfer.stateChanged.connect(self.chkInferChecked)

        pnlModel = QWidget()
        lytModel = QGridLayout(pnlModel)
        lytModel.addWidget(QLabel("Model API"), 0, 0, 1, 1)
        lytModel.addWidget(self.cmbAPI,         0, 1, 1, 1)
        lytModel.addWidget(self.chkInfer,       0, 2, 1, 1)
        lytModel.setContentsMargins(0, 0, 0, 0)
        lytModel.setColumnStretch(1, 10)

        self.list = List()
        self.memoryPlot = MemoryPlot(mw)

        control_split = QSplitter(Qt.Orientation.Vertical)
        control_split.addWidget(self.list)
        control_split.addWidget(self.memoryPlot)

        self.lblFeedback = QLabel("TESTING")
        pnlFeedback = QWidget()
        lytFeedback = QGridLayout(pnlFeedback)
        lytFeedback.addWidget(self.lblFeedback,   0, 0, 1, 1)

        pnlControl = QWidget()
        lytControl = QGridLayout(pnlControl)
        lytControl.addWidget(self.fileSelector, 0, 0, 1, 2)
        lytControl.addWidget(btnAdd,            1, 0 ,1, 1)
        lytControl.addWidget(btnEnd,            2, 0, 1, 1)
        lytControl.addWidget(btnCloseAll,       1, 1, 1, 1)
        lytControl.addWidget(btnStartNine,      2, 1, 1, 1)
        lytControl.addWidget(btnTest,           3, 0, 1, 1)
        lytControl.addWidget(self.chkReconnect, 3, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        lytControl.addWidget(pnlModel,          4, 0, 1, 2)
        lytControl.addWidget(pnlFeedback,       0, 2, 1, 1)
        lytControl.addWidget(control_split,     5, 0, 1, 3)

        lytMain = QGridLayout(self)
        lytMain.addWidget(pnlControl, 0, 0, 1, 1)

    def btnAddClicked(self):
        self.manager.startStream(self.name(), self.fileSelector.text())

    def btnEndClicked(self):
        if item := self.list.currentItem():
            self.manager.stopStream(item.text())

    def btnCloseAllClicked(self):
        self.manager.closeAllStreams()

    def btnStartNineClicked(self):
        for i in range(9):
            self.manager.startStream(self.name(), self.fileSelector.text())

    def chkReconnectChecked(self, state: int):
        self.mw.settings.setValue(self.reconnectKey, state)

    def cmbAPIChanged(self, arg):
        print("cmbAPIChanged", arg)
        self.mw.settings.setValue(self.apiKey, arg)

    def chkInferChecked(self, state: int):
        self.mw.settings.setValue(self.inferKey, state)
        if state:
            self.startModel()
    
    def name(self) -> str:
        result = f"thread_{self.counter:0{3}d}"
        self.counter += 1
        return result
    
    def showError(self, name: str, msgShow: str, msgLog: str, tag: wabash.ErrorTag):
        logger.error(f'{name} : {msgLog}')

        if tag == wabash.ErrorTag.NO_SUCH_FILE_OR_DIRECTORY:
            self.manager.lock()
            if thread := self.manager.threads.get(name):
                thread.reconnect = False
            self.manager.unlock()

        if len(msgShow):
            self.errorDialog.signals.show.emit(msgShow)

    def onClose(self):
        print("stream panel on close")
        self.manager.closeAllStreams()

    def btnTestClicked(self):
        print("btnTestClicked")
        #self.lblFeedback.setText("THINGY BOB")
        self.mw.waitDialog.signals.show.emit("THIS IS A TEST")
        timer = QTimer(self)
        timer.singleShot(1000, self.startModel)
