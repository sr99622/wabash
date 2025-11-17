import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget, QSplitter, QCheckBox, QComboBox, QLabel, QSpinBox, QGroupBox
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

class NetworkPanel(QWidget):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw

        grpClient = QGroupBox("Client")
        self.btnConnect = QPushButton("Connect")
        self.btnConnect.clicked.connect(self.btnConnectClicked)
        
        lytClient = QGridLayout(grpClient)
        lytClient.addWidget(self.btnConnect,    0, 0, 1, 1)

        grpServer = QGroupBox("Server")
        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.btnStartClicked)

        lytServer = QGridLayout(grpServer)
        lytServer.addWidget(self.btnStart, 0, 0, 1, 1)


        lytMain = QGridLayout(self)
        lytMain.addWidget(grpClient,   0, 0, 1, 1)
        lytMain.addWidget(grpServer,   1, 0, 1, 1)

    def btnConnectClicked(self):
        print("btnConnectClicked")

    def btnStartClicked(self):
        print("btnStgartClicekdc")