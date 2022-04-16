from server_gui import Ui_ServerWindow
from statistics_gui import Ui_statistics
from settings_gui import Ui_settings
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import pyqtSlot
from datetime import datetime


class StatisticsGui(QMainWindow, Ui_statistics):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()

    def update_table(self, rows):
        rows_count = self.table_history_clients.rowCount()
        for row in range(rows_count):
            self.table_history_clients.removeRow(row)
        for row in rows:
            username = row[0]
            ip = row[2]
            port = str(row[3])
            login_time = row[1].strftime('%d.%m.%Y %H:%M:%S')
            self.insert_row(username, ip, port, login_time)

    def insert_row(self, username: str, ip: str, port: str, login_time: str):
        row_position = self.table_history_clients.rowCount()
        self.table_history_clients.insertRow(row_position)
        self.table_history_clients.setItem(row_position, 0, QTableWidgetItem(username))
        self.table_history_clients.setItem(row_position, 1, QTableWidgetItem(ip))
        self.table_history_clients.setItem(row_position, 2, QTableWidgetItem(port))
        self.table_history_clients.setItem(row_position, 3, QTableWidgetItem(login_time))

    def initUi(self):
        self.show()


class SettingsGui(QMainWindow, Ui_settings):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.show()

    def accept(self):
        pass

    def reject(self):
        pass


class ServerGui(QMainWindow, Ui_ServerWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()
        self.connect_signal_slots()
        self.statistics_window = None
        self.settings_window = None
        self.db = db

    @pyqtSlot()
    def open_statistics(self):
        self.statistics_window = StatisticsGui()
        login_history = self.db.get_login_history()
        self.statistics_window.update_table(login_history)

    @pyqtSlot()
    def open_settings(self):
        self.settings_window = SettingsGui()

    def initUi(self):
        self.menuClients_history.addAction('History', self.open_statistics)
        self.menuServer_settings.addAction('Settings', self.open_settings)
        self.show()

    def update_from_db(self):
        users = self.db.get_active_users_list()
        print(users)
        self.update_table(users)

    def update_table(self, rows):
        rows_count = self.table_active_clients.rowCount()
        for row in range(rows_count):
            self.table_active_clients.removeRow(row)
        for row in rows:
            username = row[0]
            ip = row[1]
            port = str(row[2])
            login_time = row[3].strftime('%d.%m.%Y %H:%M:%S')
            self.insert_row(username, ip, port, login_time)

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
    # win = ServerGui()
    stat = StatisticsGui()
    # sett = SettingsGui()
    sys.exit(app.exec())
