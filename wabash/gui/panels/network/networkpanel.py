import os
import sys
from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, \
        QGroupBox, QComboBox
from PyQt6.QtCore import Qt
from loguru import logger
from .adapterpanel import AdapterPanel
from wabash import Client, Server, Broadcaster, Listener, NetUtil
from wabash.gui.panels.network.protocols import ClientProtocols, \
        ServerProtocols, ListenProtocols, ProtocolType

class NetworkPanel(QWidget):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw
        self.client = None
        self.server = None
        self.broadcaster = None
        self.listener = None
        self.netutil = None

        self.adapters = NetUtil().getAllAdapters()
        grpClient = QGroupBox("Client")
        self.btnClient = QPushButton("Client")
        self.btnClient.clicked.connect(self.btnClientClicked)
        self.clientAdapter = AdapterPanel(self.mw, self.adapters, ProtocolType.CLIENT)

        lytClient = QGridLayout(grpClient)
        lytClient.addWidget(self.clientAdapter,  0, 0, 1, 1)
        lytClient.addWidget(self.btnClient,      1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpServer = QGroupBox("Server")
        self.btnServer = QPushButton("Server")
        self.btnServer.clicked.connect(self.btnServerClicked)
        self.serverAdapter = AdapterPanel(self.mw, self.adapters, ProtocolType.SERVER)

        lytServer = QGridLayout(grpServer)
        lytServer.addWidget(self.serverAdapter,   0, 0, 1, 1)
        lytServer.addWidget(self.btnServer,       1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpBroadcast = QGroupBox("Broadcast")
        self.btnBroadcast = QPushButton("Broadcast")
        self.btnBroadcast.clicked.connect(self.btnBroadcastClicked)
        self.broadcastAdapter = AdapterPanel(self.mw, self.adapters, ProtocolType.BROADCAST)

        lytBroadcast = QGridLayout(grpBroadcast)
        lytBroadcast.addWidget(self.broadcastAdapter, 0, 0, 1, 1)
        lytBroadcast.addWidget(self.btnBroadcast,     1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpListen = QGroupBox("Listen")
        self.btnListen = QPushButton("Listen")
        self.btnListen.clicked.connect(self.btnListenClicked)
        self.listenAdapter = AdapterPanel(self.mw, self.adapters, ProtocolType.LISTEN)

        lytListen = QGridLayout(grpListen)
        lytListen.addWidget(self.listenAdapter,  0, 0, 1, 1)
        lytListen.addWidget(self.btnListen,         1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        lytMain = QGridLayout(self)
        lytMain.addWidget(grpClient,    0, 0, 1, 1)
        lytMain.addWidget(grpServer,    0, 1, 1, 1)
        lytMain.addWidget(grpBroadcast, 1, 0, 1, 1)
        lytMain.addWidget(grpListen,    1, 1, 1, 1)

    def btnClientClicked(self):
        print("btnClientClicked")

    def btnServerClicked(self):
        print("btnServerClicked")
        print("len adapters", len(self.adapters))
        print("current adapter", self.serverAdapter.getAdapter())

    def btnBroadcastClicked(self):
        print("btnBroadscastClicked")

    def btnListenClicked(self):
        print("btnListenClicked")
    