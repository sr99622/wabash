from PyQt6.QtWidgets import QLabel, QDialog, QGridLayout, QWidget
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal, QDir
from PyQt6.QtGui import QMovie, QIcon
import sys
import os
from pathlib import Path

class WaitDialogSignals(QObject):
    show = pyqtSignal(str)
    hide = pyqtSignal()
    update = pyqtSignal(str)

class WaitDialog(QDialog):
    def __init__(self, p):
        super().__init__(p)
        self.lblMessage = QLabel("Please wait")
        self.lblProgress = QLabel()
        self.movie = QMovie("image:spinner.gif")
        self.movie.setScaledSize(QSize(50, 50))
        self.lblProgress.setMovie(self.movie)
        self.lblInfo = QLabel()

        self.setWindowTitle("wabash")
        if sys.platform == "linux":
            self.setMinimumWidth(350)

        lytMain = QGridLayout(self)
        lytMain.addWidget(self.lblMessage,  0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        lytMain.addWidget(self.lblProgress, 1, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        lytMain.addWidget(self.lblInfo,     2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.movie.start()
        self.setModal(True)

        self.signals = WaitDialogSignals()
        self.signals.show.connect(self.show)
        self.signals.hide.connect(self.hide)
        self.signals.update.connect(self.update)

    def sizeHint(self):
        return QSize(300, 130)

    def show(self, msg):
        self.lblMessage.setText(msg)
        self.lblInfo.setText("Running...")
        super().show()

    def update(self, msg):
        self.lblInfo.setText(msg)



