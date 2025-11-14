from PyQt6.QtWidgets import QLabel, QMessageBox, QGridLayout, QWidget
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal
import sys

class ErrorDialogSignals(QObject):
    show = pyqtSignal(str)
    hide = pyqtSignal()

class ErrorDialog(QMessageBox):
    def __init__(self, p):
        super().__init__(QMessageBox.Icon.Critical, "wabash", "", QMessageBox.StandardButton.Ok, p)
        if sys.platform == "linux":
            self.setMinimumWidth(350)

        self.signals = ErrorDialogSignals()
        self.signals.show.connect(self.show)
        self.signals.hide.connect(self.hide)

    def sizeHint(self):
        return QSize(300, 100)

    def show(self, msg):
        self.setText(msg)
        super().show()


