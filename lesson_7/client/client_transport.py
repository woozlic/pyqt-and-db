from threading import Thread, Lock
import logging
import json
import socket
import sys
import os
import time

from PyQt5.QtCore import QObject, pyqtSignal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.variables import PORT, ACT_PRESENCE, HOST, ACT_MESSAGE, ACT_ADD_CONTACT, ACT_DEL_CONTACT, ACT_GET_CONTACTS, \
    ACT_EXIT, ACT_GET_CLIENTS
from common.utils import get_unix_time_str, send_message, get_message, get_datetime_from_unix_str
import log.client_log_config

logger = logging.getLogger('client')
socket_lock = Lock()


class ClientTransport(Thread, QObject):
    """Class for interaction with DB"""
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, host, port, database, name, password):
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.account_name = name
        self.password = password
        self.transport = None
        self.connection_init(port, host)

        self.running = True

    def run(self) -> None:
        """Main loop for this class. Getting messages and handle them"""
        logger.info('Getting new messages...')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет. Если не сделать тут задержку,
            # то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except ValueError:
                    pass
                except OSError as err:
                    if err.errno:
                        # выход по таймауту вернёт номер ошибки err.errno равный None
                        # поэтому, при выходе по таймауту мы сюда попросту не попадём
                        logger.critical(f'Lost connection to a server.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'Lost connection to a server.')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    logger.debug(f'Got new message from a server: {message}')
                    self.handle_answer(message)
                finally:
                    self.transport.settimeout(5)

    def shutdown(self):
        """Gracefully closes connections"""
        self.running = False
        with socket_lock:
            try:
                send_message(self.transport, self.create_exit_message())
            except OSError:
                pass
        logger.info('Exiting...')
        time.sleep(0.5)

    def connection_init(self, port, ip):
        """Trying to connect to a server"""
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)
        connected = False
        for i in range(5):
            logger.info(f'Trying to connect №{i + 1}/5')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            logger.critical('Can\'t connect to a server.')
            raise ValueError('Can\'t connect to a server.')

        logger.debug('Connected to a server!')

        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.handle_answer(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            logger.critical('Lost connection to a server.')
            raise ValueError('Lost connection to a server.')

        logger.info('Connected to a server!')

    def get_clients(self):
        """Returns clients list from a server"""
        with socket_lock:
            send_message(self.transport, self.create_get_clients_message())
            return self.handle_answer(get_message(self.transport))

    def add_contact(self, user):
        """Adds user to a contacts list"""
        if not self.database.is_contact_exists(user):
            self.database.add_contact(user)
            with socket_lock:
                send_message(self.transport, self.create_contact_edit_message(ACT_ADD_CONTACT, user))
                self.handle_answer(get_message(self.transport))
            print(f'You \'ve added {user} to friends!')
        else:
            print(f'You can\'t add {user} to friends!')

    def del_contact(self, user):
        """Deletes user from a contacts list"""
        if self.database.is_contact_exists(user):
            self.database.delete_contact(user)
            with socket_lock:
                send_message(self.transport, self.create_contact_edit_message(ACT_DEL_CONTACT, user))
                self.handle_answer(get_message(self.transport))
        else:
            print(f'You can\'t delete {user} from friends!')

    def send_message_to_user(self, username, text):
        """Sends message to a user"""
        with socket_lock:
            send_message(self.transport, self.create_message(text, username, self.account_name))
            self.handle_answer(get_message(self.transport))

    def handle_answer(self, answer):
        """Handle answer depending on the context"""
        try:
            if 'action' in answer and answer['action'] == ACT_MESSAGE and 'user' in answer and 'to' in answer and \
                    answer['to'] == self.account_name:
                print(f'NEW | From {answer["user"]["account_name"]} | {answer["msg"]}')
                text = answer['msg']
                timestamp = get_datetime_from_unix_str(answer['time'])
                from_ = answer['user']['account_name']
                to_ = answer['to']
                self.database.create_message(text, timestamp, from_, to_)
                self.new_message.emit(from_)
            elif 'action' in answer and answer['action'] == ACT_MESSAGE and 'user' in answer and 'to' in answer and \
                    answer['user']['account_name'] == self.account_name:
                text = answer['msg']
                timestamp = get_datetime_from_unix_str(answer['time'])
                from_ = answer['user']['account_name']
                to_ = answer['to']
                self.database.create_message(text, timestamp, from_, to_)
            elif 'action' in answer and answer['action'] == ACT_EXIT and 'user' in answer and answer['user'] == self.account_name:
                return
            elif 'action' in answer and answer['action'] == ACT_PRESENCE and 'user' in answer:
                logger.info('Status: Online!')
            elif 'action' in answer and answer['action'] == ACT_GET_CLIENTS and 'user' in answer and 'response' \
                    in answer and answer['response'] == 200:
                return answer['clients']
            elif 'action' in answer and answer['action'] == ACT_GET_CONTACTS and 'response' in answer\
                    and answer['response'] == 202:
                contacts = self.storage.get_contacts()
                print(f'Your contacts: {", ".join(contacts)}')
            elif 'action' in answer and answer['action'] == ACT_ADD_CONTACT and 'response' in answer \
                    and 'user_id' in answer:
                pass
            elif 'action' in answer and answer['action'] == ACT_DEL_CONTACT and 'response' in answer\
                    and 'user_id' in answer:
                pass
            elif "error" in answer:
                logger.error(answer['error'])
                exit(1)
            else:
                logger.error(answer)
                exit(1)
        except ValueError as e:
            logger.exception(e)

    def create_get_clients_message(self):
        message = {
            "action": ACT_GET_CLIENTS,
            "time": get_unix_time_str(),
            "type": "status",
            "user": {
                "account_name": self.account_name,
                "status": "online"
            }
        }
        return message

    def create_presence(self):
        presence = {
            "action": ACT_PRESENCE,
            "time": get_unix_time_str(),
            "type": "status",
            "user": {
                "account_name": self.account_name,
                "hashed_password": self.password,
                "status": "online"
            }
        }
        return presence

    def create_exit_message(self):
        return {
            'action': 'exit',
            'time': time.time(),
            'user': {
                'account_name': self.account_name,
                'status': 'offline'
            }
        }

    def create_contact_edit_message(self, action, username):
        message_dict = {
            "action": action,
            "time": get_unix_time_str(),
            "user_id": username,
            "user_login": self.account_name
        }
        return message_dict

    def create_get_contacts_message(self):
        message_dict = {
            "action": ACT_GET_CONTACTS,
            "time": get_unix_time_str(),
            "user_login": self.account_name
        }
        return message_dict

    def create_message(self, message: str, to: str, account_name: str = 'guest'):
        message_dict = {
            "action": ACT_MESSAGE,
            "time": get_unix_time_str(),
            "type": "status",
            "user": {
                "account_name": account_name,
                "status": "online"
            },
            "to": to,
            "msg": message,
        }
        logger.info(f'Created message {account_name} -> {to} | {message}')
        return message_dict

    def print_help(self):
        print('Type: m - start a new message, a - add contact, d - delete contact, c - print contacts, q - quit\n')
