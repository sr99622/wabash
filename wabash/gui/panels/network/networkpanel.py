import os
import sys
from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, \
        QGroupBox, QComboBox, QLineEdit, QLabel
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

        self.serverProtocols = ServerProtocols(self.mw)
        self.clientProtocols = ClientProtocols(self.mw)

        self.adapters = NetUtil().getAllAdapters()
        grpClient = QGroupBox("Client")
        self.btnClient = QPushButton("Client")
        self.btnClient.clicked.connect(self.btnClientClicked)
        self.clientAdapter = AdapterPanel(self.mw, self.adapters, ProtocolType.CLIENT)
        self.lblClient = QLabel("Client Command")
        self.txtClient = QLineEdit()
        self.txtClient.setText("GET CAMERA")

        lytClient = QGridLayout(grpClient)
        lytClient.addWidget(self.clientAdapter,  0, 0, 1, 1)
        lytClient.addWidget(self.lblClient,      1, 0, 1, 1)
        lytClient.addWidget(self.txtClient,      2, 0, 1, 1)
        lytClient.addWidget(self.btnClient,      3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        grpServer = QGroupBox("Server")
        self.btnStartServer = QPushButton("Server")
        self.btnStartServer.clicked.connect(self.btnStartServerClicked)
        self.serverAdapter = AdapterPanel(self.mw, self.adapters, ProtocolType.SERVER)

        lytServer = QGridLayout(grpServer)
        lytServer.addWidget(self.serverAdapter,   0, 0, 1, 1)
        lytServer.addWidget(self.btnStartServer,       1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

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
        lytListen.addWidget(self.btnListen,      1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        lytMain = QGridLayout(self)
        lytMain.addWidget(grpClient,    0, 0, 1, 1)
        lytMain.addWidget(grpServer,    0, 1, 1, 1)
        lytMain.addWidget(grpBroadcast, 1, 0, 1, 1)
        lytMain.addWidget(grpListen,    1, 1, 1, 1)

    def btnClientClicked(self):
        print("btnClientClicked")
        try:
            if not self.client:
                self.client = Client("127.0.0.1:8550")
                self.client.clientCallback = self.clientProtocols.callback
                self.client.errorCallback = self.clientProtocols.error
            print("self.txtClient", self.txtClient.text())
            self.client.transmit(f'{self.txtClient.text()}\n\n')
        except Exception as ex:
            print("Client init exception", ex)

    def btnStartServerClicked(self):
        print("btnStartServerClicked")
        print("len adapters", len(self.adapters))
        print("current adapter", self.serverAdapter.getAdapter())
        print("test")
        try:
            if not self.server:
                self.server = Server("", 8550)
                self.server.serverCallback = self.serverProtocols.callback
                self.server.errorCallback = self.serverProtocols.error
            if not self.server.running:
                self.server.start()
        except Exception as ex:
            print("Server init exception:", ex)

    def btnBroadcastClicked(self):
        print("btnBroadscastClicked")

    def btnListenClicked(self):
        print("btnListenClicked")
    