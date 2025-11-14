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
        QListWidget, QSplitter, QCheckBox, QComboBox, QLabel, QSpinBox
from PyQt6.QtCore import QSize, Qt, QSettings, QDir, QStandardPaths, QObject, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QCloseEvent, QIcon
import wabash
from enum import Enum
from pathlib import Path
from wabash.gui import Display, Manager
from wabash.gui.components import FileSelector, WaitDialog, ErrorDialog
from loguru import logger
import pyqtgraph as pg
import importlib.metadata
import traceback

class Style(Enum):
    DARK = 0
    LIGHT = 1

class List(QListWidget):
    def __init__(self):
        super().__init__()

    def setCurrentText(self, text):
        if items := self.findItems(text, Qt.MatchFlag.MatchExactly):
            self.setCurrentItem(items[0])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.logger_id = logger.add(self.getCachePath() / "logs" / "log.txt", rotation="1 MB")
            self.counter = 0
            self.manager = Manager(self)
            self.model = None

            QDir.addSearchPath("image", str(Path(__file__).parent.parent / "gui" / "resources"))
            self.settings = QSettings("wabash", "gui")
            self.setWindowIcon(QIcon('image:wabash.png'))
            #self.settings.clear()
            logger.debug(f'Settings loaded from file {self.settings.fileName()} using format {self.settings.format()}')
            self.geometryKey = "MainWindow/geometry"
            self.splitKey = "MainWindow/split"
            self.reconnectKey = "MainWindow/reconnect"
            self.inferKey = "MainWindow/infer"
            self.apiKey = "MainWindow/API"
            self.sampleSizeKey = "MainWindow/sampleSize"
            self.memoryTypeKey = "MainWindow/memoryType"
            self.intervalKey = "MainWindow/interval"

            self.setWindowTitle(f"wabash version {self.getVersion()}")
            self.setMinimumSize(QSize(320, 240))

            self.fileSelector = FileSelector(self, "File")
            self.waitDialog = WaitDialog(self)
            self.errorDialog = ErrorDialog(self)

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

            self.cmbAPI = QComboBox()
            self.cmbAPI.addItems(["PyTorch", "OpenVINO", "rknn"])
            self.cmbAPI.setCurrentText(self.settings.value(self.apiKey, "PyTorch"))
            self.cmbAPI.currentTextChanged.connect(self.cmbAPIChanged)

            self.chkInfer = QCheckBox("Infer")
            self.chkInfer.setChecked(int(self.settings.value(self.inferKey, 0)))
            self.chkInfer.stateChanged.connect(self.chkInferChecked)

            pnlModel = QWidget()
            lytModel = QGridLayout(pnlModel)
            lytModel.addWidget(QLabel("Model API"), 0, 0, 1, 1)
            lytModel.addWidget(self.cmbAPI,         0, 1, 1, 1)
            lytModel.addWidget(self.chkInfer,       0, 2, 1, 1)
            lytModel.setContentsMargins(0, 0, 0, 0)
            lytModel.setColumnStretch(1, 10)

            self.display = Display(self)
            self.list = List()

            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setLabel('bottom', 'Time', 'seconds')
            self.plot_widget.setLabel('left', 'Memory', 'MiB')
            self.cmbMemoryType = QComboBox()
            self.cmbMemoryType.addItems(["Unique", "Resident", "Virtual"])
            self.cmbMemoryType.setCurrentText(self.settings.value(self.memoryTypeKey, "Unique"))
            self.cmbMemoryType.currentTextChanged.connect(self.cmbPlotDataChanged)
            self.spnSampleSize = QSpinBox()
            self.spnSampleSize.setMaximum(1000)
            self.spnSampleSize.setValue(int(self.settings.value(self.sampleSizeKey, 120)))
            self.spnSampleSize.valueChanged.connect(self.spnSampleSizeChanged)
            self.spnInterval = QSpinBox()
            self.spnInterval.setMaximum(600)
            self.spnInterval.setValue(int(self.settings.value(self.intervalKey, 5)))
            self.spnInterval.valueChanged.connect(self.spnIntervalChanged)
            pnlPlot = QWidget()
            lytPlot = QGridLayout(pnlPlot)
            lytPlot.addWidget(QLabel("Memory Type"),   0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            lytPlot.addWidget(self.cmbMemoryType,        0, 1, 1, 1)
            lytPlot.addWidget(QLabel("Sample Size"),   0, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
            lytPlot.addWidget(self.spnSampleSize,      0, 3, 1, 1)
            lytPlot.addWidget(QLabel("Interval"),      0, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
            lytPlot.addWidget(self.spnInterval,        0, 5, 1, 1)
            lytPlot.addWidget(self.plot_widget,        1, 0, 1, 6)
            lytPlot.setContentsMargins(0, 0, 0, 0)

            control_split = QSplitter(Qt.Orientation.Vertical)
            control_split.addWidget(self.list)
            control_split.addWidget(pnlPlot)

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
            lytControl.addWidget(control_split,     5, 0, 1, 2)

            self.split = QSplitter()
            self.split.addWidget(pnlControl)
            self.split.addWidget(self.display)
            if splitterState := self.settings.value(self.splitKey):
                self.split.restoreState(splitterState)
            self.split.splitterMoved.connect(self.splitterMoved)
            self.setCentralWidget(self.split)

            self.setStyleSheet(self.style(Style.DARK))        
            if rect := self.settings.value(self.geometryKey):
                if screen := QGuiApplication.screenAt(rect.topLeft()):
                    self.setGeometry(rect)

        except Exception as ex:
            logger.error(f"Initialization Error: {ex}")
            logger.debug(traceback.format_exc())

    def startModel(self):
        try:
            if not self.model:
                logger.debug(f'starting model using api: {self.cmbAPI.currentText()}')
                #if api == "rknn":
                #    from rockchip import Model
                #else:
                #    from wabash.gui.model import Model
                from wabash.gui.model import Model
                self.model = Model(self)
        except Exception as ex:
            logger.error(f'Error starting model: {ex}')
            logger.debug(traceback.format_exc())

    def getVersion(self) -> str:
        try:
            path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if path.exists() and sys.version_info >= (3, 11):
                import tomllib
                with open(path, "rb") as f:
                    data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
            
            return importlib.metadata.version('wabash')

        except Exception as ex:
            logger.error(f'getVersion error: {ex}')
            logger.debug(traceback.format_exc())
        return "Unknown"

    def showError(self, name: str, msgShow: str, msgLog: str, tag: wabash.ErrorTag):
        logger.error(f'{name} : {msgLog}')

        if tag == wabash.ErrorTag.NO_SUCH_FILE_OR_DIRECTORY:
            self.manager.lock()
            if thread := self.manager.threads.get(name):
                thread.reconnect = False
            self.manager.unlock()

        if len(msgShow):
            self.errorDialog.signals.show.emit(msgShow)

    def splitterMoved(self, pos: int, index: int):
        self.settings.setValue(self.splitKey, self.split.saveState())

    def btnAddClicked(self):
        self.manager.startThread(self.name(), self.fileSelector.text())

    def btnEndClicked(self):
        if item := self.list.currentItem():
            if thread := self.manager.threads.get(item.text()):
                thread.running = False

    def btnCloseAllClicked(self):
        self.manager.closeAllThreads()

    def btnStartNineClicked(self):
        for i in range(9):
            self.manager.startThread(self.name(), self.fileSelector.text())

    def btnTestClicked(self):
        print("btnTestClicked")

    def chkReconnectChecked(self, state: int):
        self.settings.setValue(self.reconnectKey, state)

    def cmbAPIChanged(self, arg):
        print("cmbAPIChanged", arg)
        self.settings.setValue(self.apiKey, arg)

    def chkInferChecked(self, state: int):
        self.settings.setValue(self.inferKey, state)
        if state:
            self.startModel()
    
    def cmbPlotDataChanged(self, arg):
        print("cmbPlotDataChanged", arg)
        self.settings.setValue(self.memoryTypeKey, arg)

    def spnSampleSizeChanged(self, arg):
        print("spnSampleSizeChanged", arg)
        self.settings.setValue(self.sampleSizeKey, arg)

    def spnIntervalChanged(self, arg):
        self.settings.setValue(self.intervalKey, arg)

    def name(self) -> str:
        result = f"thread_{self.counter:0{3}d}"
        self.counter += 1
        return result
    
    def closeEvent(self, event: QCloseEvent):
        self.manager.closeAllThreads()
        self.settings.setValue(self.geometryKey, self.geometry())
        super().closeEvent(event)

    def getCachePath(self) -> Path:
        return Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.HomeLocation)[0]) / ".cache" / "wabash"

    def style(self, appearance: Style) -> str:
        filename = Path(__file__).parent.parent / "gui" / "resources" / "darkstyle.qss"
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
    
def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()