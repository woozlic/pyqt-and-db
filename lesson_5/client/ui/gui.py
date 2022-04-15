from client_chat import Ui_MainWindow
from client_add_contact import Ui_form_add_contact
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem
)
from PyQt5.QtCore import pyqtSlot


class ChatGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.show()


class AddContactGui(QMainWindow, Ui_form_add_contact):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ChatGui()
    # add_contact = AddContactGui()
    sys.exit(app.exec())
