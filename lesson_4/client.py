import logging
import time
from socket import AF_INET, SOCK_STREAM, socket
import argparse
import threading

from common.variables import PORT, ACT_PRESENCE, HOST, ACT_MESSAGE, ACT_ADD_CONTACT, ACT_DEL_CONTACT, ACT_GET_CONTACTS
from common.utils import get_unix_time_str, send_message, get_message
from client_database import ClientStorage
import log.client_log_config
from common.decorators import log

logger = logging.getLogger('client')


@log
def handle_answer(message):
    GOOD_RESPONSES = {
        200: 'Status: Online!'
    }
    BAD_RESPONSES = (400, 404, 500)
    if message['response'] in BAD_RESPONSES:
        logger.info(message['error']['error'])
    elif message['response'] in GOOD_RESPONSES.keys():
        logger.info(GOOD_RESPONSES[message['response']])
    else:
        logger.error(f'Wrong message: {str(message)}')


@log
def create_presence(account_name='guest'):

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


class ClientReader(threading.Thread):
    def __init__(self, account_name, sock, storage):
        self.account_name = account_name
        self.sock = sock
        self.storage = storage
        super().__init__()

    def run(self):
        while True:
            try:
                answer = get_message(self.sock)
                logger.debug(f'Got an answer from server: {answer}')
                if 'action' in answer and answer['action'] == 'msg' and 'user' in answer and 'to' in answer and \
                        answer['to'] == self.account_name:
                    print(f'NEW | From {answer["user"]["account_name"]} | {answer["msg"]}')
                elif 'action' in answer and answer['action'] == 'exit' and 'user' in answer and answer['user'] == self.account_name:
                    break
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
                    break
            except ValueError as e:
                print(e)
                break


class ClientSender(threading.Thread):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

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

    @log
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

    def run(self):
        self.print_help()
        message = self.create_get_contacts_message()
        logger.debug(f'Created message: {message}, sending...')
        send_message(self.sock, message)
        while True:
            user_input = input(f"-> ")
            if user_input == 'm':
                new_message = input('Enter text message: ')
                to = input('Enter receiver\'s name: ')

                message = self.create_message(new_message, to, self.account_name)
                print(f'SENT | To {to} | {new_message}')
                logger.debug(f'Created message: {message}, sending...')
                send_message(self.sock, message)
            elif user_input == 'a':
                input_contact = input('Enter username to add to contact list: ')
                message = self.create_contact_edit_message(ACT_ADD_CONTACT, input_contact)
                logger.debug(f'Created message: {message}, sending...')
                send_message(self.sock, message)
            elif user_input == 'd':
                input_contact = input('Enter username to delete from contact list: ')
                message = self.create_contact_edit_message(ACT_DEL_CONTACT, input_contact)
                logger.debug(f'Created message: {message}, sending...')
                send_message(self.sock, message)
            elif user_input == 'c':
                message = self.create_get_contacts_message()
                send_message(self.sock, message)
            else:
                print('Exiting...')
                message = self.create_exit_message()
                send_message(self.sock, message)
                time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='A client')
    parser.add_argument("address", help='Server\'s address. Default: 127.0.0.1', nargs='?', default=HOST)
    parser.add_argument("port", help='Server\'s port. Default: 7777', nargs='?', default=PORT)
    parser.add_argument('-n', dest='name', default='guest', required=False)
    args = parser.parse_args()
    logger.debug(f'Args: {args.address}, {args.port} {args.name}')
    with socket(AF_INET, SOCK_STREAM) as s:
        host = args.address
        port = int(args.port)
        try:
            s.connect((host, port))
            logger.debug(f'Connected to {host}:{port}')

            send_message(s, create_presence(args.name))
            answer = get_message(s)
            handle_answer(answer)

            print(f'Hello, client {args.name}!')
            print('Your address is', s.getsockname())
        except ConnectionRefusedError:
            logger.error('Can\'t connect to a server')
        except Exception as e:
            logger.exception('Error occured by attempting to log in')
            logger.error(e)
        else:
            storage = ClientStorage(args.name)
            reading = ClientReader(args.name, s, storage)
            reading.daemon = True
            reading.start()

            writing = ClientSender(args.name, s)
            writing.daemon = True
            writing.start()

            while True:
                time.sleep(1)
                if reading.is_alive() and writing.is_alive():
                    continue
                break


if __name__ == '__main__':
    main()
