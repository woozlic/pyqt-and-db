from server_gui import Ui_MainWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)


class ServerGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ServerGui()
    win.show()
    sys.exit(app.exec())
