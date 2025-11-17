import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget, QSplitter, QCheckBox, QComboBox, QLabel, QSpinBox
from PyQt6.QtCore import QSize, Qt, QSettings, QDir, QStandardPaths, QObject, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QCloseEvent, QIcon
import wabash
from enum import Enum
from pathlib import Path
from wabash.gui import Display, Manager
from wabash.gui.components import FileSelector, WaitDialog, ErrorDialog, Theme, Style
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
        self.counter = 0

        self.reconnectKey = "MainWindow/reconnect"
        self.inferKey = "MainWindow/infer"
        self.apiKey = "MainWindow/API"
        self.sampleSizeKey = "MainWindow/sampleSize"
        self.memoryTypeKey = "MainWindow/memoryType"
        self.intervalKey = "MainWindow/interval"

        self.fileSelector = FileSelector(self.mw, "File")
        self.waitDialog = WaitDialog(self.mw)
        self.errorDialog = ErrorDialog(self.mw)

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

        #self.display = Display(self)
        self.list = List()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time', 'seconds')
        self.plot_widget.setLabel('left', 'Memory', 'MiB')
        self.cmbMemoryType = QComboBox()
        self.cmbMemoryType.addItems(["Unique", "Resident", "Virtual"])
        self.cmbMemoryType.setCurrentText(self.mw.settings.value(self.memoryTypeKey, "Unique"))
        self.cmbMemoryType.currentTextChanged.connect(self.cmbPlotDataChanged)
        self.spnSampleSize = QSpinBox()
        self.spnSampleSize.setMaximum(1000)
        self.spnSampleSize.setValue(int(self.mw.settings.value(self.sampleSizeKey, 120)))
        self.spnSampleSize.valueChanged.connect(self.spnSampleSizeChanged)
        self.spnInterval = QSpinBox()
        self.spnInterval.setMaximum(600)
        self.spnInterval.setValue(int(self.mw.settings.value(self.intervalKey, 5)))
        self.spnInterval.valueChanged.connect(self.spnIntervalChanged)
        pnlPlot = QWidget()
        lytPlot = QGridLayout(pnlPlot)
        lytPlot.addWidget(QLabel("Memory Type"),   0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        lytPlot.addWidget(self.cmbMemoryType,      0, 1, 1, 1)
        lytPlot.addWidget(QLabel("Sample Size"),   0, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        lytPlot.addWidget(self.spnSampleSize,      0, 3, 1, 1)
        lytPlot.addWidget(QLabel("Interval"),      0, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
        lytPlot.addWidget(self.spnInterval,        0, 5, 1, 1)
        lytPlot.addWidget(self.plot_widget,        1, 0, 1, 6)
        lytPlot.setContentsMargins(0, 0, 0, 0)

        control_split = QSplitter(Qt.Orientation.Vertical)
        control_split.addWidget(self.list)
        control_split.addWidget(pnlPlot)

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
        self.mw.manager.startStream(self.name(), self.fileSelector.text())

    def btnEndClicked(self):
        if item := self.list.currentItem():
            self.mw.manager.stopStream(item.text())

    def btnCloseAllClicked(self):
        self.mw.manager.closeAllStreams()

    def btnStartNineClicked(self):
        for i in range(9):
            self.mw.manager.startStream(self.name(), self.fileSelector.text())

    def btnTestClicked(self):
        print("btnTestClicked")
        self.lblFeedback.setText("THINGY BOB")

    def chkReconnectChecked(self, state: int):
        self.mw.settings.setValue(self.reconnectKey, state)

    def cmbAPIChanged(self, arg):
        print("cmbAPIChanged", arg)
        self.mw.settings.setValue(self.apiKey, arg)

    def chkInferChecked(self, state: int):
        self.mw.settings.setValue(self.inferKey, state)
        if state:
            self.startModel()
    
    def cmbPlotDataChanged(self, arg):
        print("cmbPlotDataChanged", arg)
        self.mw.settings.setValue(self.memoryTypeKey, arg)

    def spnSampleSizeChanged(self, arg):
        print("spnSampleSizeChanged", arg)
        self.mw.settings.setValue(self.sampleSizeKey, arg)

    def spnIntervalChanged(self, arg):
        self.mw.settings.setValue(self.intervalKey, arg)

    def name(self) -> str:
        result = f"thread_{self.counter:0{3}d}"
        self.counter += 1
        return result
    
