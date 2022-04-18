from PyQt5.QtCore import QObject, pyqtSignal
from threading import Thread, Lock
import logging
import json
import socket
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.variables import PORT, ACT_PRESENCE, HOST, ACT_MESSAGE, ACT_ADD_CONTACT, ACT_DEL_CONTACT, ACT_GET_CONTACTS, \
    ACT_EXIT
from common.utils import get_unix_time_str, send_message, get_message, get_datetime_from_unix_str
from client_database import ClientStorage
import log.client_log_config
from common.decorators import log
import time

logger = logging.getLogger('client')
socket_lock = Lock()


class ClientTransport(Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal

    def __init__(self, host, port, database, username):
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.account_name = username
        self.transport = None
        self.connection_init(port, host)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Lost connection to a server.')
                raise ValueError('Lost connection to a server.')
            logger.error('Timeout by refreshing client\'s contacts.')
        except json.JSONDecodeError:
            logger.critical(f'Lost connection to a server.')
            raise ValueError('Lost connection to a server.')

        self.running = True

    def user_list_update(self):
        pass

    def contacts_list_update(self):
        pass

    def shutdown(self):
        self.running = False
        with socket_lock:
            try:
                send_message(self.transport, self.create_exit_message())
            except OSError:
                pass
        logger.info('Exiting...')
        time.sleep(0.5)

    def connection_init(self, port, ip):
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

    def handle_answer(self, answer):
        try:
            if 'action' in answer and answer['action'] == ACT_MESSAGE and 'user' in answer and 'to' in answer and \
                    answer['to'] == self.account_name:
                print(f'NEW | From {answer["user"]["account_name"]} | {answer["msg"]}')
                text = answer['msg']
                timestamp = get_datetime_from_unix_str(answer['time'])
                logger.info(timestamp)
                from_ = answer['user']['account_name']
                to_ = answer['to']
                self.storage.create_message(text, timestamp, from_, to_)
            elif 'action' in answer and answer['action'] == ACT_MESSAGE and 'user' in answer and 'to' in answer and \
                    answer['user']['account_name'] == self.account_name:
                print(answer)
                text = answer['msg']
                timestamp = answer['time']
                from_ = answer['user']['account_name']
                to_ = answer['to']
                self.storage.create_message(text, timestamp, from_, to_)
            elif 'action' in answer and answer['action'] == ACT_EXIT and 'user' in answer and answer['user'] == self.account_name:
                return
            elif 'action' in answer and answer['action'] == ACT_PRESENCE and 'user' in answer:
                logger.info('Status: Online!')
            elif 'action' in answer and answer['action'] == ACT_GET_CONTACTS and 'response' in answer\
                    and answer['response'] == 202:
                contacts = self.storage.get_contacts()
                print(f'Your contacts: {", ".join(contacts)}')
            elif 'action' in answer and answer['action'] == ACT_ADD_CONTACT and 'response' in answer \
                    and 'user_id' in answer:
                user = answer['user_id']
                if answer['response'] == 200:
                    if not self.storage.is_contact_exists(user):
                        self.storage.add_contact(user)
                        print(f'You \'ve added {user} to friends!')
                    else:
                        print(f'You can\'t add {user} to friends!')
                else:
                    print(f'You can\'t add {user} to friends!')
            elif 'action' in answer and answer['action'] == ACT_DEL_CONTACT and 'response' in answer\
                    and 'user_id' in answer:
                user = answer['user_id']
                if answer['response'] == 200:
                    if self.storage.is_contact_exists(user):
                        self.storage.delete_contact(user)
                        print(f'You \'ve deleted {user} from friends')
                    else:
                        print(f'You can\'t delete {user} from friends!')
                else:
                    print(f'You can\'t delete {user} from friends!')
            else:
                print(answer)
                logger.error(answer)
        except ValueError as e:
            logger.exception(e)

    def create_presence(self, account_name='guest'):
        presence = {
            "action": ACT_PRESENCE,
            "time": get_unix_time_str(),
            "type": "status",
            "user": {
                "account_name": account_name,
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
        return message_dict

    def print_help(self):
        print('Type: m - start a new message, a - add contact, d - delete contact, c - print contacts, q - quit\n')
