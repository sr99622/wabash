import os
import sys
from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, \
        QGroupBox
from PyQt6.QtCore import Qt
from loguru import logger
from wabash import Client, Server, Broadcaster, Listener, NetUtil
from wabash.gui.panels.network.protocols import ClientProtocols, ServerProtocols, ListenProtocols

class NetworkPanel(QWidget):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw
        self.client = None
        self.server = None
        self.broadcaster = None
        self.listener = None
        self.netutil = None

        grpClient = QGroupBox("Client")
        self.btnClient = QPushButton("Client")
        self.btnClient.clicked.connect(self.btnClientClicked)
        
        lytClient = QGridLayout(grpClient)
        lytClient.addWidget(self.btnClient,    0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpServer = QGroupBox("Server")
        self.btnServer = QPushButton("Server")
        self.btnServer.clicked.connect(self.btnServerClicked)

        lytServer = QGridLayout(grpServer)
        lytServer.addWidget(self.btnServer,    0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

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

    def btnClientClicked(self):
        print("btnClientClicked")

    def btnServerClicked(self):
        print("btnServerClicked")
        self.netutil = NetUtil()
        ip = self.netutil.getIPAddress()
        print("IP:", ip)
        dt = self.netutil.getActiveNetworkInterfaces()
        print("DT:", dt)

    def btnBroadcastClicked(self):
        print("btnBroadscastClicked")

    def btnListenClicked(self):
        print("btnListenClicked")

    