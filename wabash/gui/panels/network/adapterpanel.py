import os
import sys
from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, \
        QGroupBox, QComboBox, QDialog, QLabel, QLineEdit, QCheckBox, \
        QDialogButtonBox
from PyQt6.QtCore import Qt, QSize
from loguru import logger
from wabash import Client, Server, Broadcaster, Listener, NetUtil
from wabash.gui.panels.network.protocols import ClientProtocols, ServerProtocols, ListenProtocols, ProtocolType

class AdapterDialog(QDialog):
    def __init__(self, mw):
        super().__init__(mw)
        self.setModal(True)
        #self.setTitle("Adapter")
        self.txtIPAddress = QLineEdit()
        self.txtGateway = QLineEdit()
        self.txtNetmask = QLineEdit()
        self.txtDNS = QLineEdit()
        self.lblName = QLabel()
        self.lblType = QLabel()
        self.lblDescription = QLabel()
        self.lblMacAddress = QLabel()
        self.lblBroadcast = QLabel()
        self.lblState = QLabel()
        self.chkDHCP = QCheckBox("DHCP Enabled")
        self.txtPriority = QLineEdit()
        self.txtPriority.setMaximumWidth(40)
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)  # Connect OK to dialog's accept
        self.buttonBox.rejected.connect(self.reject)  # Connect Cancel to dialog's reject

        lytMain = QGridLayout(self)
        lytMain.addWidget(QLabel("Name"),        0, 0, 1, 1)
        lytMain.addWidget(self.lblName,          0, 1, 1, 1)
        lytMain.addWidget(QLabel("Type"),        1, 0, 1, 1)
        lytMain.addWidget(self.lblType,          1, 1, 1, 1)
        lytMain.addWidget(QLabel("Description"), 2, 0, 1, 1)
        lytMain.addWidget(self.lblDescription,   2, 1, 1, 1)
        lytMain.addWidget(self.chkDHCP,          3, 0, 1, 2)
        lytMain.addWidget(QLabel("IP Address"),  4, 0, 1, 1)
        lytMain.addWidget(self.txtIPAddress,     4, 1, 1, 1)
        lytMain.addWidget(QLabel("Gateway"),     5, 0, 1, 1)
        lytMain.addWidget(self.txtGateway,       5, 1, 1, 1)
        lytMain.addWidget(QLabel("DNS"),         6, 0, 1, 1)
        lytMain.addWidget(self.txtDNS,           6, 1, 1, 1)
        lytMain.addWidget(QLabel("Netmask"),     7, 0, 1, 1)
        lytMain.addWidget(self.txtNetmask,       7, 1, 1, 1)
        lytMain.addWidget(QLabel("Broadcast"),   8, 0, 1, 1)
        lytMain.addWidget(self.lblBroadcast,     8, 1, 1, 1)
        lytMain.addWidget(QLabel("MAC Address"), 9, 0, 1, 1)
        lytMain.addWidget(self.lblMacAddress,    9, 1, 1, 1)
        lytMain.addWidget(QLabel("State"),      10, 0, 1, 1)
        lytMain.addWidget(self.lblState,        10, 1, 1, 1)
        lytMain.addWidget(QLabel("Priority"),   11, 0, 1, 1)
        lytMain.addWidget(self.txtPriority,     11, 1, 1, 1)
        lytMain.addWidget(self.buttonBox,       12, 0, 1, 3)

    #def sizeHint(self):
    #    return QSize(400, 400)

    def setData(self, adapter):
        self.lblName.setText(adapter.name)
        self.lblType.setText(adapter.type)
        self.lblDescription.setText(adapter.description)
        self.txtIPAddress.setText(adapter.ip_address)
        self.txtGateway.setText(adapter.gateway)
        self.txtNetmask.setText(adapter.netmask)
        self.lblBroadcast.setText(adapter.broadcast)
        self.lblMacAddress.setText(adapter.mac_address)
        self.chkDHCP.setChecked(adapter.dhcp)
        dns = ""
        for i, d in enumerate(adapter.dns):
            dns += d
            if i < len(adapter.dns) - 1:
                dns += "; "
        self.txtDNS.setText(dns)
        if adapter.up:
            self.lblState.setText("UP")
        else:
            self.lblState.setText("DOWN")
        if adapter.priority < 0:
            self.txtPriority.setText("")
        else:
            self.txtPriority.setText(f'{adapter.priority}')

    def accept(self):
        #print("ACCEPT")
        self.hide()

    def reject(self):
        #print("REJECT")
        self.hide()
        
class AdapterPanel(QWidget):
    def __init__(self, mw, adapters, type):
        super().__init__(mw)
        self.mw = mw
        self.adapters = adapters
        self.dlgAdapter = AdapterDialog(self.mw)
        self.typeName = None
        self.type = type
        match type:
            case ProtocolType.SERVER:
                self.typeName = "Server"
            case ProtocolType.CLIENT:
                self.typeName = "Client"
            case ProtocolType.LISTEN:
                self.typeName = "Listen"
            case ProtocolType.BROADCAST:
                self.typeName = "Broadcast"
        self.chkOnlyActiveKey = f'AdapterPanel/{self.typeName}/chkOnlyActive'
        self.adapterKey = f'AdapterPanel/{self.typeName}/adapter'

        self.chkOnlyActive = QCheckBox("Only Show Active Adapters")
        self.chkOnlyActive.setChecked(int(self.mw.settings.value(self.chkOnlyActiveKey, 1)))
        self.chkOnlyActive.clicked.connect(self.chkOnlyActiveChecked)

        self.cmbAdapter = QComboBox()
        for adapter in self.adapters:
            if self.chkOnlyActive.isChecked():
                if adapter.up:
                    self.cmbAdapter.addItem(adapter.name)
            else:        
                self.cmbAdapter.addItem(adapter.name) 
        self.cmbAdapter.setCurrentText(self.mw.settings.value(self.adapterKey))
        self.cmbAdapter.currentTextChanged.connect(self.cmbAdapterCurrentTextChanged)

        self.btnInfo = QPushButton("...")
        self.btnInfo.clicked.connect(self.btnInfoClicked)

        lytMain = QGridLayout(self)
        lytMain.addWidget(self.chkOnlyActive,  0, 0, 1, 3)
        lytMain.addWidget(QLabel("Adapter"),   1, 0, 1, 1)
        lytMain.addWidget(self.btnInfo,        1, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        lytMain.addWidget(self.cmbAdapter,     1, 2, 1, 1)
        lytMain.setContentsMargins(0, 0, 0, 0)
        lytMain.setColumnStretch(2, 1)

    def btnInfoClicked(self):
        self.dlgAdapter.setData(self.getAdapter(self.cmbAdapter.currentText()))
        self.dlgAdapter.show()

    def getAdapter(self, name):
        for adapter in self.adapters:
            if adapter.name == name:
                return adapter

    def chkOnlyActiveChecked(self, state):
        self.mw.settings.setValue(self.chkOnlyActiveKey, str(int(state)))
        self.cmbAdapter.clear()
        for adapter in self.adapters:
            if state:
                if adapter.up:
                    self.cmbAdapter.addItem(adapter.name)
            else:
                self. cmbAdapter.addItem(adapter.name)        

    def cmbAdapterCurrentTextChanged(self, arg):
        self.mw.settings.setValue(self.adapterKey, arg)