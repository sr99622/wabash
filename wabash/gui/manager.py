#********************************************************************
# wabash/gui/manager.py
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

from PyQt6.QtCore import QSize, QSizeF, Qt, QRectF, QPointF
from PyQt6.QtWidgets import QMainWindow
from wabash import Stream
from wabash.gui.components import Layout
from time import sleep
from loguru import logger
import traceback

class Manager():
    def __init__(self, mw: QMainWindow):
        self.streams = {}
        self.mw = mw
        self.ordinals = {}
        self.layout = Layout(mw)
        self.stream_lock = False

    def lock(self):
        while self.stream_lock:
            sleep(0.001)
        self.stream_lock = True

    def unlock(self):
        self.stream_lock = False

    def startStream(self, name: str, filename: str):
        self.lock()
        try:
            stream = Stream(name, filename)
            stream.finish = self.removeStream
            stream.reconnect = self.mw.chkReconnect.isChecked()
            stream.showError = self.mw.showError
            stream.foolish = self.mw.foolish
            self.layout.addOrdinal(stream.name)
            self.streams[stream.name] = stream
            stream.start()
            self.mw.list.addItem(stream.name)
        except Exception as ex:
            logger.error(f'Error starting stream: {ex}')
            logger.debug(traceback.format_exc())
        self.unlock()

    def stopStream(self, name: str):
        self.lock()
        if stream := self.streams.get(name):
            stream.running = False
        self.unlock()

    def removeStream(self, name: str):
        reconnect = False
        filename = self.mw.fileSelector.text()
        self.lock()
        if stream := self.streams.get(name):
            reconnect = stream.reconnect
            filename = stream.filename
            list = self.mw.list
            items = list.findItems(name, Qt.MatchFlag.MatchExactly)
            if len(items):
                list.takeItem(list.row(items[0]))
            del self.streams[name]
        self.unlock()

        if not reconnect:
            self.layout.removeOrdinal(name)
        else:
            self.startStream(name, filename)

    def closeAllStreams(self):
        self.lock()
        for name in self.streams:
            self.streams[name].reconnect = False
            self.streams[name].running = False
        self.unlock()
        while len(self.streams):
            sleep(0.001)

