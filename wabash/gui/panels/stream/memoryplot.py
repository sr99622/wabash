import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, \
        QListWidget, QSplitter, QCheckBox, QComboBox, QLabel, QSpinBox
from PyQt6.QtCore import QSize, Qt, QSettings, QDir, QStandardPaths, QObject, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QCloseEvent, QIcon
import wabash
from enum import Enum
from pathlib import Path
from wabash.gui import Display
from loguru import logger
import pyqtgraph as pg
import importlib.metadata
import traceback
from collections import deque
import psutil
import time

class MemoryPlot(QWidget):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw
        self.sampleSizeKey = "MainWindow/sampleSize"
        self.memoryTypeKey = "MainWindow/memoryType"
        self.intervalKey = "MainWindow/interval"

        self.global_start_time = time.time()
        self.cycle_start_time = time.time()
        self.process = psutil.Process(os.getpid())
        self.blank_display = True
        self.line = None
        self.x = deque()
        self.rss = deque()
        self.uss = deque()
        self.vms = deque()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time', 'seconds')
        self.plot_widget.setLabel('left', 'Memory', 'MiB')
        self.cmbMemoryType = QComboBox()
        self.cmbMemoryType.addItems(["Unique", "Resident", "Virtual"])
        self.cmbMemoryType.setCurrentText(self.mw.settings.value(self.memoryTypeKey, "Unique"))
        self.cmbMemoryType.currentTextChanged.connect(self.cmbPlotDataChanged)
        self.spnSampleSize = QSpinBox()
        self.spnSampleSize.setMaximum(1000)
        self.spnSampleSize.setValue(int(self.mw.settings.value(self.sampleSizeKey, 120)))
        self.spnSampleSize.valueChanged.connect(self.spnSampleSizeChanged)
        self.spnInterval = QSpinBox()
        self.spnInterval.setMaximum(600)
        self.spnInterval.setValue(int(self.mw.settings.value(self.intervalKey, 5)))
        self.spnInterval.valueChanged.connect(self.spnIntervalChanged)
        pnlPlot = QWidget()
        lytPlot = QGridLayout(pnlPlot)
        lytPlot.addWidget(QLabel("Memory Type"),   0, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        lytPlot.addWidget(self.cmbMemoryType,      0, 1, 1, 1)
        lytPlot.addWidget(QLabel("Sample Size"),   0, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        lytPlot.addWidget(self.spnSampleSize,      0, 3, 1, 1)
        lytPlot.addWidget(QLabel("Interval"),      0, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
        lytPlot.addWidget(self.spnInterval,        0, 5, 1, 1)
        lytPlot.addWidget(self.plot_widget,        1, 0, 1, 6)
        lytPlot.setContentsMargins(0, 0, 0, 0)

        lytMain = QGridLayout(self)
        lytMain.addWidget(pnlPlot, 0, 0, 1, 1)
        lytMain.setContentsMargins(0, 0, 0, 0)

    def update(self):
        current_time = time.time()
        cycle_elapsed_time = current_time - self.cycle_start_time
        global_elapsed_time = current_time - self.global_start_time
        if cycle_elapsed_time > self.spnInterval.value():
            #print(f"time (seconds): {global_elapsed_time:.2f} memory (bytes): {self.process.memory_info().rss}")
            self.cycle_start_time = current_time
            if len(self.x) > self.spnSampleSize.value():
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

            if self.cmbMemoryType.currentText() == "Unique":
                dataset = self.uss
            elif self.cmbMemoryType.currentText() == "Resident":
                dataset = self.rss
            elif self.cmbMemoryType.currentText() == "Virtual":
                dataset = self.vms
            if self.line:
                self.line.setData(self.x, dataset)
            else:
                self.line = self.plot_widget.plot(self.x, dataset)

    def cmbPlotDataChanged(self, arg):
        print("cmbPlotDataChanged", arg)
        self.mw.settings.setValue(self.memoryTypeKey, arg)

    def spnSampleSizeChanged(self, arg):
        print("spnSampleSizeChanged", arg)
        self.mw.settings.setValue(self.sampleSizeKey, arg)

    def spnIntervalChanged(self, arg):
        self.mw.settings.setValue(self.intervalKey, arg)

