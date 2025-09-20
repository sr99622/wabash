#/********************************************************************
# wabash/test/thread.py
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

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget
from PyQt6.QtCore import QSize, Qt
import wabash
import numpy as np
from time import sleep

class Manager():
    def __init__(self, window):
        self.threads = {}
        self.window = window

    def startThread(self, thread):
        self.threads[thread.name] = thread
        thread.start()
        self.window.list.addItem(thread.name)

    def removeThread(self, name):
        if name in self.threads:
            del self.threads[name]
            list = self.window.list
            items = list.findItems(name, Qt.MatchFlag.MatchExactly)
            if len(items):
                list.takeItem(list.row(items[0]))

    def closeAllThreads(self):
        for name in self.threads:
            thread = self.threads[name]
            thread.running = False
        while len(self.threads):
            sleep(0.001)

class ThreadList(QListWidget):
    def __init__(self):
        super().__init__()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.manager = Manager(self)

        self.setWindowTitle("Threads Example")
        self.setMinimumSize(QSize(320, 240))

        btnAdd = QPushButton("Add Thread")
        btnAdd.clicked.connect(self.btnAddClicked)

        btnEnd = QPushButton("End Thread")
        btnEnd.clicked.connect(self.btnEndClicked)

        btnCloseAll = QPushButton("Close All")
        btnCloseAll.clicked.connect(self.btnCloseAllClicked)

        btnStartTen = QPushButton("Start Ten")
        btnStartTen.clicked.connect(self.btnStartTenClicked)    

        self.list = ThreadList()

        panel = QWidget()
        layout = QGridLayout(panel)
        layout.addWidget(btnAdd,      0, 0 ,1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btnEnd,      1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btnCloseAll, 0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(btnStartTen, 1, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.list,   2, 0, 1, 2)
        self.setCentralWidget(panel)

    def btnAddClicked(self):
        try:
            thread = wabash.Thread(self.name())
            #thread.setPayload(2, 2, 2)
            thread.callback = self.callback
            thread.finish = self.finish
            self.manager.startThread(thread)
        except Exception as ex:
            print(ex)

    def btnEndClicked(self):
        if item := self.list.currentItem():
            if thread := self.manager.threads.get(item.text()):
                thread.running = False

    def btnCloseAllClicked(self):
        self.manager.closeAllThreads()

    def btnStartTenClicked(self):
        for i in range(10):
            self.btnAddClicked()

    def callback(self, payload, arg):
        ary = np.array(payload, copy = False)

        if len(ary.shape) < 3:
            return
        h = ary.shape[0]
        w = ary.shape[1]
        d = ary.shape[2]
        print(ary)
        #payload.show()
        #ary.fill(17)
        #payload.show()
        print("python callback", arg, h, w, d)
        #return True

    def finish(self, arg):
        self.manager.removeThread(arg)

    def name(self):
        result = f"thread_{self.counter:0{3}d}"
        self.counter += 1
        return result
    
    def closeEvent(self, event):
        self.manager.closeAllThreads()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
