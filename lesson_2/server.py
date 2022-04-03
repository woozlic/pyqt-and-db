import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import select
import argparse

from common.utils import send_message, get_message
from common.errors import UnsafePortError
from common.variables import *
from common.decorators import log
from log import server_log_config

logger = logging.getLogger('server')


class Server:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self._host = host
        self._port = port
        self.clients = []

    @log
    def process_client_message(self, message: dict, client, names: dict) -> dict:
        answer_bad_request = {
            "response": RESP_WRONG_REQUEST,
            "error": "Bad Request"
        }
        if "action" in message and message['action'] == 'presence'\
                and 'time' in message and 'user' in message:
            message["response"] = RESP_OK
            names[message['user']['account_name']] = client
            send_message(client, message)
            return message
        elif "action" in message and message['action'] == 'msg'\
                and 'time' in message and 'user' in message and 'to' in message:
            if message['to'] not in names.keys():
                answer = {
                    "response": RESP_NOT_FOUND,
                    "error": "This user is not online!"
                }
                send_message(client, answer)
                return answer
            message["response"] = RESP_OK
            return message
        else:
            logger.warning(f'Bad Request from {client.getpeername()}')
            return answer_bad_request

    def read_requests(self, r_clients, all_clients, names: dict):
        """Read requests from list of clients"""
        responses = {}
        for sock in r_clients:
            client_n = sock.fileno()
            client_peername = sock.getpeername()
            try:
                new_message = get_message(sock)
                print('NEW', new_message)
                responses[sock] = self.process_client_message(new_message, sock, names)
            except:
                logger.info(f'Client {client_n} {client_peername} was disconnected.')
                all_clients.remove(sock)
                sock.close()
        return responses

    def write_responses(self, requests, w_clients, all_clients, names: dict):
        for sock in w_clients:
            if sock in requests:
                try:
                    client_message = requests[sock]
                    if 'msg' in client_message and 'to' in client_message:
                        to_client = names[client_message['to']]
                        if client_message['to'] in names.keys():
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
                    all_clients.remove(sock)

    def run_main_loop(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.bind((self._host, self._port))
            logger.info(f'Server is running on {self._host}:{str(self._port)}')
            s.listen(5)
            s.settimeout(0.2)
            names = {}
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
                responses = self.read_requests(r, self.clients, names)
                if responses:
                    self.write_responses(responses, w, self.clients, names)


def main():
    parser = argparse.ArgumentParser(description='A server')
    parser.add_argument('-a', help='Server\'s address. Default: 127.0.0.1', default=HOST)
    parser.add_argument('-p', help='Server\'s port. Default: 7777', default=PORT)
    args = parser.parse_args()
    host = args.a
    port = int(args.p)
    # if not 1024 < port < 65536:
    #     logger.critical('Please, specify safe port (1024-65536)')
    #     raise UnsafePortError
    server = Server(host, port)
    server.run_main_loop()


if __name__ == '__main__':
    main()
