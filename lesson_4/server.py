import logging
import sys
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock
import select
import argparse

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from gui import StatisticsGui, ServerGui, SettingsGui
from common.utils import send_message, get_message
from common.variables import *
from common.decorators import log
from metaclasses import ServerVerifier
from lesson_2.descs import Port
from server_database import ServerStorage

logger = logging.getLogger('server')

lock = Lock()
new_client = True


class Server(Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self._host = host
        Server.port = port
        self.storage = ServerStorage()
        self._port = Server.port
        self.clients = []
        self.names = {}

        super().__init__()

    @log
    def process_client_message(self, message: dict, client) -> dict:
        answer_bad_request = {
            "response": RESP_WRONG_REQUEST,
            "error": "Bad Request"
        }
        if "action" in message and message['action'] == ACT_PRESENCE\
                and 'time' in message and 'user' in message:
            message["response"] = RESP_OK
            username = message['user']['account_name']
            self.names[username] = client
            send_message(client, message)
            client_host, client_port = client.getsockname()
            self.storage.user_login(username, client_host, client_port)
            global new_client
            with lock:
                new_client = True
            return message
        elif "action" in message and message['action'] == ACT_MESSAGE\
                and 'time' in message and 'user' in message and 'to' in message:
            if message['to'] not in self.names.keys():
                answer = {
                    "response": RESP_NOT_FOUND,
                    "error": "This user is not online!"
                }
                send_message(client, answer)
                return answer
            message["response"] = RESP_OK
            return message
        elif "action" in message and message['action'] == 'exit'\
                and 'time' in message and 'user' in message:
            username = message['user']['account_name']
            self.storage.user_logout(username)
            client_sock = self.names[username]
            self.clients.remove(client_sock)
            del self.names[username]
            client_sock.close()
            return message
        elif 'action' in message and message['action'] == ACT_GET_CONTACTS:
            username = message['user_login']
            if self.storage.is_user_exist(username):
                message["response"] = 202
            else:
                message["response"] = 400
            send_message(client, message)
            return message
        elif 'action' in message and message['action'] == ACT_ADD_CONTACT or message['action'] == ACT_DEL_CONTACT:
            user_from = message['user_login']
            user_to = message['user_id']
            if self.storage.is_user_exist(user_from) and self.storage.is_user_exist(user_to) and user_to != user_from:
                print(user_from, '->', user_to)
                message["response"] = 200
            else:
                message["response"] = 400
            send_message(client, message)
            return message
        else:
            logger.warning(f'Bad Request from {client.getpeername()}')
            return answer_bad_request

    def read_requests(self, r_clients):
        """Read requests from list of clients"""
        responses = {}
        for sock in r_clients:
            client_n = sock.fileno()
            client_peername = sock.getpeername()
            try:
                new_message = get_message(sock)
                print('NEW', new_message)
                responses[sock] = self.process_client_message(new_message, sock)
            except Exception as e:
                logger.exception('DISCONNECT')
                logger.info(f'Client {client_n} {client_peername} was disconnected.')
                self.clients.remove(sock)
                sock.close()
        return responses

    def write_responses(self, requests, w_clients):
        for sock in w_clients:
            if sock in requests:
                try:
                    client_message = requests[sock]
                    if 'msg' in client_message and 'to' in client_message:
                        to_client = self.names[client_message['to']]
                        if client_message['to'] in self.names.keys():
                            send_message(to_client, client_message)
                            logger.debug(f'Sending a message {client_message} to {to_client.getpeername()}')
                        else:
                            logger.debug('This user is not online!')
                except TypeError as e:
                    logger.exception(f'Is message a dict?')
                except Exception as e:
                    logger.debug(e)
                    logger.info(f'Client {sock.fileno()} {sock.getpeername()} was disconnected.')
                    sock.close()
                    self.clients.remove(sock)

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.bind((self._host, self._port))
            logger.info(f'Server is running on {self._host}:{str(self._port)}')
            s.listen(5)
            s.settimeout(0.2)
            while True:
                try:
                    client, addr = s.accept()
                except OSError:
                    pass
                else:
                    logger.debug(f'New client: {addr}')
                    self.clients.append(client)

                wait = 1
                r = []
                w = []
                try:
                    if self.clients:
                        r, w, e = select.select(self.clients, self.clients, [], wait)
                except OSError:
                    pass
                responses = self.read_requests(r)
                if responses:
                    self.write_responses(responses, w)


def main():
    parser = argparse.ArgumentParser(description='A server')
    parser.add_argument('-a', help='Server\'s address. Default: 127.0.0.1', default=HOST)
    parser.add_argument('-p', help='Server\'s port. Default: 7777', default=PORT)
    args = parser.parse_args()
    host = args.a
    port = int(args.p)

    server = Server(host, port)
    server.daemon = True
    server.start()
    storage = ServerStorage()

    main_window = QApplication(sys.argv)
    server_gui = ServerGui(storage)

    def list_update():
        global new_client
        if new_client:
            server_gui.update_from_db()
            with lock:
                new_client = False

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(500)

    sys.exit(main_window.exec())


if __name__ == '__main__':
    main()
