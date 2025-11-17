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
        QListWidget, QSplitter, QCheckBox, QComboBox, QLabel, QSpinBox, QTabWidget
from PyQt6.QtCore import QSize, Qt, QSettings, QDir, QStandardPaths, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QGuiApplication, QCloseEvent, QIcon
import wabash
from enum import Enum
from pathlib import Path
from wabash.gui import Display
from wabash.gui.panels import StreamPanel, NetworkPanel
from wabash.gui.components import FileSelector, WaitDialog, ErrorDialog, Theme, Style
from loguru import logger
import pyqtgraph as pg
import importlib.metadata
import traceback
from time import sleep
import threading

class MainWindowSignals(QObject):
    feedback = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            QDir.addSearchPath("image", str(Path(__file__).parent.parent / "gui" / "resources"))
            self.logger_id = logger.add(self.getCachePath() / "logs" / "log.txt", rotation="1 MB")
            self.model = None
            self.model_starting = False
            self.waitDialog = WaitDialog(self)
            self.errorDialog = ErrorDialog(self)
            self.signals = MainWindowSignals()
            self.signals.feedback.connect(self.foolUpdate)

            self.settings = QSettings("wabash", "gui")
            self.setWindowIcon(QIcon('image:wabash.png'))
            self.setWindowTitle(f"wabash version {self.getVersion()}")
            self.setMinimumSize(QSize(320, 240))

            #self.settings.clear()
            logger.debug(f'Settings loaded from file {self.settings.fileName()} using format {self.settings.format()}')
            self.geometryKey = "MainWindow/geometry"
            self.splitKey = "MainWindow/split"

            self.streamPanel = StreamPanel(self)
            self.networkPanel = NetworkPanel(self)
            self.tab = QTabWidget(self)
            self.tab.setContentsMargins(0, 0, 0, 0)
            self.tab.addTab(self.streamPanel, "Stream")
            self.tab.addTab(self.networkPanel, "Network")

            self.display = Display(self)

            self.split = QSplitter()
            self.split.setContentsMargins(0, 0, 0, 0)
            self.split.addWidget(self.tab)
            self.split.addWidget(self.display)
            if splitterState := self.settings.value(self.splitKey):
                self.split.restoreState(splitterState)
            self.split.splitterMoved.connect(self.splitterMoved)

            self.setContentsMargins(0, 0, 0, 0)
            self.setCentralWidget(self.split)

            theme = Theme(self)
            self.setStyleSheet(theme.style(Style.DARK))        
            if rect := self.settings.value(self.geometryKey):
                if screen := QGuiApplication.screenAt(rect.topLeft()):
                    self.setGeometry(rect)

        except Exception as ex:
            logger.error(f"Initialization Error: {ex}")
            logger.debug(traceback.format_exc())

    def initializeModel(self):
        self.waitDialog.signals.update.emit("Loading Python libraries")
        from wabash.gui.model import Model
        self.waitDialog.signals.update.emit("Starting model load")
        self.model = Model(self)

    def startModel(self):
        try:
            if not self.model and not self.model_starting:
                self.model_starting = True
                self.waitDialog.signals.show.emit("Please wait while the model is initialized")
                thread = threading.Thread(target=self.initializeModel)
                thread.start()
                logger.debug(f'starting model using api: {self.streamPanel.cmbAPI.currentText()}')
                #if api == "rknn":
                #    from rockchip import Model
                #else:
                #    from wabash.gui.model import Model
                #from wabash.gui.model import Model
                #self.model = Model(self)
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

    def foolUpdate(self, msg: str):
        self.lblFeedback.setText(msg)

    def foolish(self, name: str, pts: int):
        #print("foolish", name, pts)
        #self.signals.feedback.emit(f'{name} - {pts}')
        ...

    def splitterMoved(self, pos: int, index: int):
        self.settings.setValue(self.splitKey, self.split.saveState())

    def closeEvent(self, event: QCloseEvent):
        self.settings.setValue(self.geometryKey, self.geometry())
        super().closeEvent(event)

    def getCachePath(self) -> Path:
        return Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.HomeLocation)[0]) / ".cache" / "wabash"

def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()