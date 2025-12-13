#********************************************************************
# onvif-gui/onvif_gui/protocols/client.py
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
#*********************************************************************/

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import pyqtSignal, QObject
from loguru import logger

class ClientProtocolSignals(QObject):
    error = pyqtSignal(str)

class ClientProtocols():
    def __init__(self, mw):
        self.mw = mw
        self.signals = ClientProtocolSignals()
        self.signals.error.connect(self.showMsgBox)

    def callback(self, msg):
        configs = msg.split("\r\n")
        cmd = configs.pop(0)
        print("client recvd string", cmd)

    def error(self, msg):
        logger.error(f'Client protocol error: {msg}')
        self.signals.error.emit(msg)

    def showMsgBox(self, msg):
        QMessageBox.critical(self.mw, "Unable to complete request", msg)
