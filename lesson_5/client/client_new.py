import datetime
import logging
import time
from socket import AF_INET, SOCK_STREAM, socket
import argparse
import threading
import sys
import os

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.variables import PORT, ACT_PRESENCE, HOST, ACT_MESSAGE, ACT_ADD_CONTACT, ACT_DEL_CONTACT, ACT_GET_CONTACTS
from common.utils import get_unix_time_str, send_message, get_message, get_datetime_from_unix_str
from client_database import ClientStorage
from client_transport import ClientTransport
from ui.gui import ChatGui, AddContactGui
import log.client_log_config
from common.decorators import log


logger = logging.getLogger('client')


def get_args():
    """Returns Server\'s address, port and client\'s name from cmd args"""
    parser = argparse.ArgumentParser(description='A client')
    parser.add_argument("address", help='Server\'s address. Default: 127.0.0.1', nargs='?', default=HOST)
    parser.add_argument("port", help='Server\'s port. Default: 7777', nargs='?', default=PORT)
    parser.add_argument('-n', dest='name', default='guest', required=False)
    args = parser.parse_args()
    logger.debug(f'Args: {args.address}, {args.port} {args.name}')
    return args.address, args.port, args.name


def main():
    host, port, name = get_args()
    client_app = QApplication(sys.argv)

    # get client's name if not provided

    logger.info(f'Client {name} connected to {host}:{port}')

    storage = ClientStorage(name)

    try:
        transport = ClientTransport(host, port, storage, name)
    except ValueError as e:
        logger.error(e)
        exit(1)
    else:
        transport.daemon = True
        transport.start()

        chat_window = ChatGui(storage, transport)
        chat_window.make_connection(transport)
        client_app.exec_()

        transport.shutdown()
        transport.join()


if __name__ == '__main__':
    main()
