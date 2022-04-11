from server_gui import Ui_MainWindow
from statistics import Ui_statistics
from settings import Ui_settings
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QTableWidgetItem
)


class StatisticsGui(QMainWindow, Ui_statistics):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class SettingsGui(QMainWindow, Ui_settings):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
    def accept(self):
        pass
    def reject(self):
        pass


class ServerGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.update_table()
        self.connect_signal_slots()

    def update_table(self):
        rows = [['user', "127.0.0.1", "8000", "24.02.2022"], ['user', "127.0.0.1", "8000", "24.02.2022"]]
        for row in rows:
            self.insert_row(*row)

    def insert_row(self, username: str, ip: str, port: str, login_time: str):
        row_position = self.table_active_clients.rowCount()
        self.table_active_clients.insertRow(row_position)
        self.table_active_clients.setItem(row_position, 0, QTableWidgetItem(username))
        self.table_active_clients.setItem(row_position, 1, QTableWidgetItem(ip))
        self.table_active_clients.setItem(row_position, 2, QTableWidgetItem(port))
        self.table_active_clients.setItem(row_position, 3, QTableWidgetItem(login_time))

    def connect_signal_slots(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ServerGui()
    win.show()
    stat = StatisticsGui()
    stat.show()
    sett = SettingsGui()
    sett.show()
    sys.exit(app.exec())
