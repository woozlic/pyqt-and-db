import logging
import argparse
import sys
import os

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.variables import PORT, ACT_PRESENCE, HOST, ACT_MESSAGE, ACT_ADD_CONTACT, ACT_DEL_CONTACT, ACT_GET_CONTACTS
from client_database import ClientStorage
from client_transport import ClientTransport
from ui.gui import ChatGui, LoginGui
import log.client_log_config


logger = logging.getLogger('client')


def get_args():
    """Returns Server\'s address, port and client\'s name from cmd args
    Example: python client.py 127.0.0.1 8000 -n NAME
    """
    parser = argparse.ArgumentParser(description='A client')
    parser.add_argument("address", help='Server\'s address. Default: 127.0.0.1', nargs='?', default=HOST)
    parser.add_argument("port", help='Server\'s port. Default: 7777', nargs='?', default=PORT)
    parser.add_argument('-n', dest='name', default=None, required=False)
    parser.add_argument('-p', dest='password', default=None, required=False)
    args = parser.parse_args()
    logger.debug(f'Args: {args.address}, {args.port} {args.name} {args.password}')
    return args.address, args.port, args.name, args.password


def prompt_login_password():
    """QT Window for prompting username and password from a user
    """
    login_qapp = QApplication(sys.argv)
    login = LoginGui()
    login_qapp.exec_()
    name, password = login.username, login.password
    return name, password


def main():
    """Main loop for client that obtains cmd args, prompts username and password, sets db connection and GUI"""
    host, port, name, password = get_args()
    if not (name and password):
        name, password = prompt_login_password()

    main_qapp = QApplication(sys.argv)

    while True:
        logger.info(f'Client {name} trying to connect to {host}:{port}')
        storage = ClientStorage(name)

        try:
            transport = ClientTransport(host, port, storage, name, password)
        except ValueError as e:
            logger.error(e)
            exit(1)
        else:
            break

    transport.daemon = True
    transport.start()

    chat_window = ChatGui(storage, transport)
    chat_window.make_connection(transport)

    main_qapp.exec_()

    transport.shutdown()
    transport.join()


if __name__ == '__main__':
    main()
