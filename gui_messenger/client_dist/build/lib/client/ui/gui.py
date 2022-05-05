import hashlib

from .client_chat import Ui_MainWindow
from .client_add_contact import Ui_form_add_contact
from .login import Ui_Form
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor


class ChatGui(QMainWindow, Ui_MainWindow):

    is_authenticated = pyqtSignal()

    def __init__(self, storage, transport, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.transport = transport
        self.contacts_model = None
        self.current_chat = None
        self.add_contact_gui = None
        self.history_model = None
        self.login_window = None
        self.alert = QMessageBox()
        self.setupUi(self)
        self.clients_list_update()
        self.initUi()

    def grant_send_message(self, grant: bool):
        self.btn_send_message.setEnabled(grant)
        self.edit_message.setEnabled(grant)

    def initUi(self):
        self.grant_send_message(False)
        self.list_contacts.clicked.connect(self.select_contact)
        self.btn_add_contact.clicked.connect(self.open_add_contact_gui)
        self.btn_del_contact.clicked.connect(self.del_contact)
        self.btn_send_message.clicked.connect(self.send_message)
        self.show()

    def open_add_contact_gui(self):
        all_clients = self.transport.get_clients()
        self.add_contact_gui = AddContactGui(all_clients)
        self.add_contact_gui.btn_add.clicked.connect(self.add_contact)
        self.add_contact_gui.btn_cancel.clicked.connect(self.add_contact_gui.close)

    def add_contact(self):
        item = self.add_contact_gui.select_user
        new_contact = str(item.currentText())
        self.transport.add_contact(new_contact)
        self.clients_list_update()

    def del_contact(self):
        self.transport.del_contact(self.current_chat)
        self.clients_list_update()

    def select_contact(self):
        self.current_chat = self.list_contacts.currentIndex().data()
        self.grant_send_message(True)
        self.messages_list_update()

    def send_message(self):
        message_text = self.edit_message.text()
        if not message_text:
            return
        alert = self.transport.send_message_to_user(self.current_chat, message_text)
        if alert:
            self.alert.warning(self, 'Oops', 'It seems that user is not online. Try later.')
        self.messages_list_update()
        self.edit_message.setText('')

    def messages_list_update(self):
        history = self.storage.get_history(self.current_chat)

        self.history_model = QStandardItemModel()
        self.list_messages.setModel(self.history_model)

        self.history_model.clear()
        length = len(history)
        start_index = 0

        if length > 20:
            start_index = length - 20

        for i in range(start_index, length):
            item = history[i]
            print(item)
            if item[1] != self.current_chat:
                mess = QStandardItem(f'{item[2]}\nВходящее от {item[0]}\n{item[3]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'{item[2]}\nИсходящее от {item[0]}\n{item[3]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.list_messages.scrollToBottom()

    def make_connection(self, obj):
        obj.new_message.connect(self.message)
        obj.connection_lost.connect(self.connection_lost)

    @pyqtSlot(str)
    def message(self, sender):
        self.alert.information(self, 'Info', f'New message from {sender}!')
        self.messages_list_update()
        self.clients_list_update()

    def connection_lost(self):
        self.alert.critical(self, 'Oops', 'Lost connection to a server.')

    def clients_list_update(self):
        contacts_list = self.storage.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.list_contacts.setModel(self.contacts_model)


class AddContactGui(QMainWindow, Ui_form_add_contact):
    def __init__(self, clients, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.clients = clients
        self.clients_model = None
        self.initUi()

    def initUi(self):
        self.clients_list_update()
        self.show()

    def clients_list_update(self):
        print(self.clients)
        self.clients_model = QStandardItemModel()
        for i in sorted(self.clients):
            item = QStandardItem(i)
            self.clients_model.appendRow(item)
        self.select_user.setModel(self.clients_model)


class LoginGui(QMainWindow, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.initUi()
        self.username = None
        self.password = None
        self.messages = QMessageBox()

    def initUi(self):
        self.btn_login.clicked.connect(self.authenticate)
        self.show()

    def authenticate(self):
        self.username = self.edit_username.text().strip()
        self.password = self.edit_password.text().strip()
        if not (self.username and self.password):
            self.messages.critical(self, 'Error', 'You should enter username and password both!')
        else:
            hashed_password = hashlib.pbkdf2_hmac('sha256', self.password.encode('utf-8'),
                                                  self.username.lower().encode('utf-8'), 100000)
            self.password = str(hashed_password)
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # win = ChatGui(None, None)
    # add_contact = AddContactGui()
    login = LoginGui()
    sys.exit(app.exec())
