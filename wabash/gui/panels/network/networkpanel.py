import os
import sys
from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, \
        QGroupBox
from PyQt6.QtCore import Qt
from loguru import logger
from wabash import Client, Server, Broadcaster, Listener
from wabash.gui.panels.network.protocols import ClientProtocols, ServerProtocols, ListenProtocols

class NetworkPanel(QWidget):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw
        self.client = None
        self.server = None
        self.broadcaster = None
        self.listener = None

        grpClient = QGroupBox("Client")
        self.btnConnect = QPushButton("Connect")
        self.btnConnect.clicked.connect(self.btnConnectClicked)
        
        lytClient = QGridLayout(grpClient)
        lytClient.addWidget(self.btnConnect,    0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpServer = QGroupBox("Server")
        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.btnStartClicked)

        lytServer = QGridLayout(grpServer)
        lytServer.addWidget(self.btnStart,    0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpBroadcast = QGroupBox("Broadcast")
        self.btnBroadcast = QPushButton("Broadcast")
        self.btnBroadcast.clicked.connect(self.btnBroadcastClicked)

        lytBroadcast = QGridLayout(grpBroadcast)
        lytBroadcast.addWidget(self.btnBroadcast,    0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpListen = QGroupBox("Listen")
        self.btnListen = QPushButton("Listen")
        self.btnListen.clicked.connect(self.btnListenClicked)

        lytListen = QGridLayout(grpListen)
        lytListen.addWidget(self.btnListen,    0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        lytMain = QGridLayout(self)
        lytMain.addWidget(grpClient,    0, 0, 1, 1)
        lytMain.addWidget(grpServer,    0, 1, 1, 1)
        lytMain.addWidget(grpBroadcast, 1, 0, 1, 1)
        lytMain.addWidget(grpListen,    1, 1, 1, 1)

    def btnConnectClicked(self):
        print("btnConnectClicked")

    def btnStartClicked(self):
        print("btnStartClicked")

    def btnBroadcastClicked(self):
        print("btnBroadscastClicked")

    def btnListenClicked(self):
        print("btnListenClicked")

    