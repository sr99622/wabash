#********************************************************************
# wabash/gui/display.py
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

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget, QLabel
from PyQt6.QtCore import QSize, Qt, QRect, QRectF, QPointF, QTimer
from PyQt6.QtGui import QImage, QPainter, QColorConstants, QPixmap, QPen, QFont
import wabash
import numpy as np
from time import sleep

class Display(QLabel):
    def __init__(self, mw, size):
        super().__init__()
        self.mw = mw
        self.image = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.start(10)

    def timeout(self):
        self.image = QImage(self.size(), QImage.Format.Format_ARGB32)
        if self.image.isNull():
            return
        painter = QPainter(self.image)
        if not painter.isActive():
            return
        painter.fillRect(self.image.rect(), QColorConstants.Black)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(QFont("Arial", 20))

        self.mw.manager.lock()
        for thread in self.mw.manager.threads.values():
            if not thread.payload or not thread.running:
                continue
            ary = np.array(thread.payload, copy = False)
            ary = np.ascontiguousarray(ary)
            if len(ary.shape) < 3:
                continue
            h = ary.shape[0]
            w = ary.shape[1]
            d = ary.shape[2]
            data = QImage(ary.data, w, h, d * w, QImage.Format.Format_RGB888)
            if data.isNull():
                continue

            rect = self.mw.manager.displayRect(thread.name, self.size())
            painter.drawImage(rect, data)
            
            painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine))
            textRect = self.getTextRect(painter, thread.name)
            textRect.moveCenter(QPointF(rect.center()))
            painter.drawText(textRect, Qt.AlignmentFlag.AlignCenter, thread.name)
            painter.setPen(QPen(Qt.GlobalColor.lightGray, 2, Qt.PenStyle.SolidLine))
            painter.drawRect(rect)
            if self.mw.list.currentItem() and thread.name == self.mw.list.currentItem().text():
                painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine))
                painter.drawRect(rect.adjusted(2, 2, -2, -2))
        self.mw.manager.unlock()

        self.setPixmap(QPixmap.fromImage(self.image))

    def sizeHint(self):
        return QSize(480,480)

    def getTextRect(self, painter, text):
        # to get exact bounding box, first estimate
        estimate = painter.fontMetrics().boundingRect(text)
        return painter.fontMetrics().boundingRect(estimate, 0, text).toRectF()

    def mousePressEvent(self, event):
        self.mw.manager.lock()
        for name in self.mw.manager.threads:
            rect = self.mw.manager.displayRect(name, self.size())
            if rect.contains(event.position()):
                self.mw.list.setCurrentText(name)
                break
        self.mw.manager.unlock()
