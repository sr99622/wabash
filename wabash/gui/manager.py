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
from wabash import Thread
from time import sleep
from loguru import logger
import traceback

class Manager():
    def __init__(self, mw: QMainWindow):
        self.threads = {}
        self.mw = mw
        self.ordinals = {}
        self.thread_lock = False

    def lock(self):
        while self.thread_lock:
            sleep(0.001)
        self.thread_lock = True

    def unlock(self):
        self.thread_lock = False

    def startThread(self, name: str, filename: str):
        self.lock()
        try:
            thread = Thread(name, filename)
            thread.finish = self.removeThread
            thread.reconnect = self.mw.chkReconnect.isChecked()
            thread.showError = self.mw.showError
            thread.foolish = self.mw.foolish
            if not thread.name in self.ordinals.keys():
                ordinal = self.nextOrdinal()
                self.ordinals[thread.name] = ordinal
            self.threads[thread.name] = thread
            thread.start()
            self.mw.list.addItem(thread.name)
        except Exception as ex:
            logger.error(f'Error starting thread: {ex}')
            logger.debug(traceback.format_exc())
        self.unlock()

    def removeThread(self, name: str):
        reconnect = False
        filename = self.mw.fileSelector.text()
        self.lock()
        if thread := self.threads.get(name):
            reconnect = thread.reconnect
            filename = thread.filename
            list = self.mw.list
            items = list.findItems(name, Qt.MatchFlag.MatchExactly)
            if len(items):
                list.takeItem(list.row(items[0]))
            del self.threads[name]
        self.unlock()

        if not reconnect:
            if name in self.ordinals:
                del self.ordinals[name]
        else:
            self.startThread(name, filename)

    def closeAllThreads(self):
        self.lock()
        for name in self.threads:
            self.threads[name].reconnect = False
            self.threads[name].running = False
        self.unlock()
        while len(self.threads):
            sleep(0.001)

    def nextOrdinal(self) -> int:
        values = set(self.ordinals.values())
        length = len(values)
        for i in range(length):
            if not i in values:
                return i
        return length
        
    def computeRowsCols(self, canvas_size: QSize, aspect_ratio: float) -> tuple[int, int]:
        # build a list of all possible combinations of rows and columns that can accommodate the number of
        # cells required to display all streams, then optimize by finding the least amount of blank space
        num_cells = len(set(self.ordinals.values()))
        if not num_cells:
            return 0, 0

        valid_layouts = []
        for i in range(1, num_cells+1):
            for j in range(num_cells, 0, -1):
                if ((i * j) >= num_cells):
                    if (((i-1)*j) < num_cells) and ((i*(j-1)) < num_cells):
                        valid_layouts.append(QSize(i, j))

        index = -1
        min_ratio = 0
        first_pass = True
        for i, layout in enumerate(valid_layouts):
            composite = (aspect_ratio * layout.height()) / layout.width()
            ratio = (canvas_size.width() / canvas_size.height()) / composite
            optimize = abs(1 - ratio)
            if first_pass:
                first_pass = False
                min_ratio = optimize
                index = i
            else:
                if optimize < min_ratio:
                    min_ratio = optimize
                    index = i

        return valid_layouts[index].width(), valid_layouts[index].height()

    def getBlankSpace(self, canvas_size: QSize, aspect_ratio: float) -> list[QRectF]:
        # after determining the size of the composite image which is the aggregate containing all streams, 
        # compute the rectangles required to fill out the blank space not occupied by any current stream
        blanks = []
        num_rows, num_cols = self.computeRowsCols(canvas_size, aspect_ratio)
        if not num_rows:
            blanks.append(QRectF(QPointF(0, 0), QSizeF(canvas_size)))
            return blanks
        
        composite_size = QSizeF(num_cols * aspect_ratio, num_rows)
        composite_size.scale(QSizeF(canvas_size), Qt.AspectRatioMode.KeepAspectRatio)
        im_w = composite_size.toSize().width()
        im_h = composite_size.toSize().height()
        cv_w = canvas_size.width()
        cv_h = canvas_size.height()
        if im_h == cv_h:
            blank_w = (cv_w - im_w)/2
            blanks.append(QRectF(0, 0, blank_w, im_h))
            blanks.append(QRectF(im_w + blank_w, 0, blank_w, im_h))
        if im_w == cv_w:
            blank_h = (cv_h - im_h)/2
            blanks.append(QRectF(0, 0, im_w, blank_h))
            blanks.append(QRectF(0, im_h + blank_h, im_w, blank_h))
        for i in range(num_rows * num_cols):
            if i not in self.ordinals.values():
                blanks.append(self.rectForOrdinal(i, canvas_size, aspect_ratio, num_rows, num_cols))
        return blanks

    def rectForOrdinal(self, ordinal: int, canvas_size: QSize, aspect_ratio: float, num_rows: int, num_cols: int) -> QRectF:
        if not num_rows or ordinal < 0:
            return QRectF(QPointF(0, 0, QSizeF(canvas_size)))

        col = ordinal % num_cols
        row = int(ordinal / num_cols)

        composite_size = QSizeF(num_cols * aspect_ratio, num_rows)
        composite_size.scale(QSizeF(canvas_size), Qt.AspectRatioMode.KeepAspectRatio)

        cell_width = composite_size.width() / num_cols
        cell_height = composite_size.height() / num_rows

        image_size = QSizeF(aspect_ratio, 1)
        image_size.scale(cell_width, cell_height, Qt.AspectRatioMode.KeepAspectRatio)
        w = image_size.width()
        h = image_size.height()

        x_offset = (canvas_size.width() - composite_size.width() + (cell_width - w)) / 2
        y_offset = (canvas_size.height() - composite_size.height() + (cell_height - h)) / 2
        
        x = (col * cell_width) + x_offset
        y = (row * cell_height) + y_offset

        return QRectF(x, y, w, h)

    def displayRect(self, uri: str, canvas_size: QSize, aspect_ratio: float) -> QRectF:
        num_rows, num_cols = self.computeRowsCols(canvas_size, aspect_ratio)
        if not num_rows:
            return QRectF(QPointF(0, 0), QSizeF(canvas_size))

        ordinal = -1
        if uri in self.ordinals.keys():
            ordinal = self.ordinals[uri]
            # if the number of streams has decreased, the ordinal might be over the rows * cols limit
            if ordinal > num_rows * num_cols - 1:
                ordinal = self.nextOrdinal()
                self.ordinals[uri] = ordinal

        return self.rectForOrdinal(ordinal, canvas_size, aspect_ratio, num_rows, num_cols)        
