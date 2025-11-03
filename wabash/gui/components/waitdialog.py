from PyQt6.QtWidgets import QLabel, QDialog, QGridLayout, QWidget
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal
from PyQt6.QtGui import QMovie
import sys

class WaitDialogSignals(QObject):
    show = pyqtSignal(str)
    hide = pyqtSignal()

class WaitDialog(QDialog):
    def __init__(self, p):
        super().__init__(p)
        self.lblMessage = QLabel("Please wait")
        self.lblProgress = QLabel()
        self.movie = QMovie("image:spinner.gif")
        self.movie.setScaledSize(QSize(50, 50))
        self.lblProgress.setMovie(self.movie)
        self.setWindowTitle("wabash")
        if sys.platform == "linux":
            self.setMinimumWidth(350)

        lytMain = QGridLayout(self)
        lytMain.addWidget(self.lblMessage,  0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        lytMain.addWidget(self.lblProgress, 1, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.movie.start()
        self.setModal(True)

        self.signals = WaitDialogSignals()
        self.signals.show.connect(self.show)
        self.signals.hide.connect(self.hide)

    def sizeHint(self):
        return QSize(300, 100)

    def show(self, msg):
        self.lblMessage.setText(msg)
        super().show()


