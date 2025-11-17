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

from PyQt6.QtWidgets import QLabel, QMainWindow
from PyQt6.QtCore import QSize, Qt, QPointF, QTimer, QRectF, QMargins
from PyQt6.QtGui import QImage, QPainter, QColorConstants, QPixmap, QPen, \
        QFont, QMouseEvent
import numpy as np
from collections import deque
import time
import os
import psutil
import traceback
from loguru import logger

class Display(QLabel):
    def __init__(self, mw: QMainWindow):
        super().__init__()
        self.mw = mw
        self.image = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.start(10)
        self.image = QImage(self.size(), QImage.Format.Format_ARGB32)
        self.stream_aspect_ratio = 16/9
        self.global_start_time = time.time()
        self.cycle_start_time = time.time()
        self.process = psutil.Process(os.getpid())
        self.blank_display = True
        self.line = None
        self.x = deque()
        self.rss = deque()
        self.uss = deque()
        self.vms = deque()

    def timeout(self):
        try:
            current_time = time.time()
            cycle_elapsed_time = current_time - self.cycle_start_time
            global_elapsed_time = current_time - self.global_start_time
            if cycle_elapsed_time > self.mw.streamPanel.spnInterval.value():
                #print(f"time (seconds): {global_elapsed_time:.2f} memory (bytes): {self.process.memory_info().rss}")
                self.cycle_start_time = current_time
                if len(self.x) > self.mw.streamPanel.spnSampleSize.value():
                    print("trimming data", len(self.x))
                    self.x.popleft()
                    self.rss.popleft()
                    self.uss.popleft()
                    self.vms.popleft()
                self.x.append(global_elapsed_time)
                MB = 1024 * 1024
                self.rss.append(self.process.memory_info().rss / MB)
                self.uss.append(self.process.memory_full_info().uss / MB)
                self.vms.append(self.process.memory_info().vms / MB)

                if self.mw.streamPanel.cmbMemoryType.currentText() == "Unique":
                    dataset = self.uss
                elif self.mw.streamPanel.cmbMemoryType.currentText() == "Resident":
                    dataset = self.rss
                elif self.mw.streamPanel.cmbMemoryType.currentText() == "Virtual":
                    dataset = self.vms
                if self.line:
                    self.line.setData(self.x, dataset)
                else:
                    self.line = self.mw.streamPanel.plot_widget.plot(self.x, dataset)

            if self.image.isNull():
                return

            resized = False
            if self.image.size() != self.size():
                self.image = QImage(self.size(), QImage.Format.Format_ARGB32)
                resized = True

            painter = QPainter(self.image)
            if not painter.isActive():
                return
            
            if resized:
                painter.fillRect(self.image.rect(), QColorConstants.Black)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setFont(QFont("Arial", 20))

            self.mw.manager.lock()
            
            for stream in self.mw.manager.streams.values():
                if not stream.running:
                    continue
                if stream.frame.is_null():
                    continue

                # only write the image to the pixmap if the frame is new
                if stream.last_pts == stream.frame.pts():
                    continue
                
                ary = np.array(stream.frame, copy = False)
                ary = np.ascontiguousarray(ary)

                if len(ary.shape) < 3:
                    continue
                h = ary.shape[0]
                w = ary.shape[1]
                d = ary.shape[2]
                data = QImage(ary.data, w, h, d * w, QImage.Format.Format_RGB888)
                if data.isNull():
                    continue

                # interestingly, the stream cannot be written to until after the ary is assigned
                stream.last_pts = stream.frame.pts()

                if stream.counter > 3:
                    if self.mw.streamPanel.chkInfer.isChecked():
                        if not self.mw.model:
                            self.mw.startModel()
                        if self.mw.model.loaded:
                            boxes = self.mw.model(ary)
                            if boxes is not None:
                                stream.detections = boxes
                    stream.counter = 0

                # draw stream image
                rect = self.mw.manager.layout.displayRect(stream.name, self.image.size(), self.stream_aspect_ratio)
                painter.drawImage(rect, data)
                
                # draw stream name
                painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine))
                textRect = self.getTextRect(painter, stream.name)
                textRect.moveCenter(QPointF(rect.center()))
                painter.drawText(textRect, Qt.AlignmentFlag.AlignCenter, stream.name)
                
                # draw stream detections
                scalex = rect.width() / w
                scaley = rect.height() / h
                for box in stream.detections:
                    p = (box[0] * scalex + rect.x())
                    q = (box[1] * scaley + rect.y())
                    r = (box[2] - box[0]) * scalex
                    s = (box[3] - box[1]) * scaley
                    painter.drawRect(QRectF(p, q, r, s).intersected(rect))

                # draw stream border
                painter.setPen(QPen(Qt.GlobalColor.lightGray, 2, Qt.PenStyle.SolidLine))
                painter.drawRect(rect)
                if self.mw.streamPanel.list.currentItem() and stream.name == self.mw.streamPanel.list.currentItem().text():
                    painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine))
                    painter.drawRect(rect.adjusted(2, 2, -2, -2))

            if len(self.mw.manager.streams) or self.blank_display:
                blanks = self.mw.manager.layout.getBlankSpace(self.image.size(), self.stream_aspect_ratio)
                for blank in blanks:
                    painter.fillRect(blank, QColorConstants.Black)
                self.setPixmap(QPixmap.fromImage(self.image))
                self.blank_display = False
            else:
                self.blank_display = True

            self.mw.manager.unlock()
        except Exception as ex:
            logger.debug(f'Display Refresh Error: {ex}')
            logger.debug(traceback.format_exc())
            self.mw.manager.unlock()

    def sizeHint(self) -> QSize:
        return QSize(480,480)
    
    def resizeEvent(self, event):
        self.image = QImage(event.size().shrunkBy(QMargins(5, 5, 5, 5)), QImage.Format.Format_ARGB32)
        return super().resizeEvent(event)

    def getTextRect(self, painter: QPainter, text: str) -> QRectF:
        # to get exact bounding box, first estimate
        estimate = painter.fontMetrics().boundingRect(text)
        return painter.fontMetrics().boundingRect(estimate, 0, text).toRectF()

    def mousePressEvent(self, event: QMouseEvent):
        self.mw.manager.lock()
        for name in self.mw.manager.streams:
            rect = self.mw.manager.layout.displayRect(name, self.size(), self.stream_aspect_ratio)
            if rect.contains(event.position()):
                self.mw.list.setCurrentText(name)
                break
        self.mw.manager.unlock()
