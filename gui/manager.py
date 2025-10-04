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
import wabash
from time import sleep

class Manager():
    def __init__(self, mw):
        self.threads = {}
        self.mw = mw
        self.ordinals = {}
        self.sizes = {}
        self.thread_lock = False

    def lock(self):
        while self.thread_lock:
            sleep(0.001)
        self.thread_lock = True

    def unlock(self):
        self.thread_lock = False

    def startThread(self, thread):
        self.lock()
        if not thread.name in self.ordinals.keys():
            ordinal = self.nextOrdinal()
            self.ordinals[thread.name] = ordinal
        self.threads[thread.name] = thread
        thread.start()
        self.mw.list.addItem(thread.name)
        self.unlock()

    def removeThread(self, name):
        reconnect = False
        self.lock()
        if name in self.threads:
            reconnect = self.threads[name].reconnect
            del self.threads[name]
            list = self.mw.list
            items = list.findItems(name, Qt.MatchFlag.MatchExactly)
            if len(items):
                list.takeItem(list.row(items[0]))
        self.unlock()

        if not reconnect:
            if name in self.ordinals:
                del self.ordinals[name]
        else:
            thread = wabash.Thread(name)
            thread.setPayload(320, 180, 3)
            thread.reconnect = True
            thread.finish = self.removeThread
            self.startThread(thread)

    def closeAllThreads(self):
        self.lock()
        for name in self.threads:
            self.threads[name].running = False
        self.unlock()

    def nextOrdinal(self):
        values = set(self.ordinals.values())
        size = len(values)
        for i in range(size):
            if not i in values:
                return i
        return size
        
    def computeRowsCols(self, size_canvas, aspect_ratio):
        num_cells = len(set(self.ordinals.values()))

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
            ratio = (size_canvas.width() / size_canvas.height()) / composite
            optimize = abs(1 - ratio)
            if first_pass:
                first_pass = False
                min_ratio = optimize
                index = i
            else:
                if optimize < min_ratio:
                    min_ratio = optimize
                    index = i

        if index == -1:
            return 0, 0
        
        return valid_layouts[index].width(), valid_layouts[index].height()

    def displayRect(self, uri, canvas_size):
        ar = 177 # assuming 16:9 aspect ratios
        
        num_rows, num_cols = self.computeRowsCols(canvas_size, ar / 100)
        if num_cols == 0:
            return QRectF(QPointF(0, 0), QSizeF(canvas_size))

        ordinal = -1
        if uri in self.ordinals.keys():
            ordinal = self.ordinals[uri]
        else:
            return QRectF(QPointF(0, 0), QSizeF(canvas_size))

        if ordinal > num_rows * num_cols - 1:
            ordinal = self.nextOrdinal()
            self.ordinals[uri] = ordinal
        
        col = ordinal % num_cols
        row = int(ordinal / num_cols)

        composite_size = QSizeF()
        if num_rows:
            composite_size = QSizeF(num_cols * ar / 100, num_rows)
            composite_size.scale(QSizeF(canvas_size), Qt.AspectRatioMode.KeepAspectRatio)

        cell_width = composite_size.width() / num_cols
        cell_height = composite_size.height() / num_rows

        image_size = QSizeF(ar, 100)
        if uri in self.sizes.keys():
            image_size = QSizeF(self.sizes[uri])

        image_size.scale(cell_width, cell_height, Qt.AspectRatioMode.KeepAspectRatio)
        w = image_size.width()
        h = image_size.height()

        x_offset = (canvas_size.width() - composite_size.width() + (cell_width - w)) / 2
        y_offset = (canvas_size.height() - composite_size.height() + (cell_height - h)) / 2
        
        x = (col * cell_width) + x_offset
        y = (row * cell_height) + y_offset

        return QRectF(x, y, w, h)
