import time
import json
import logging
from datetime import datetime
import locale

from .variables import BYTES_RECV_SIZE


logger = logging.getLogger('server')


def send_message(sock, message: dict, encoding='ascii'):
    if not isinstance(message, dict):
        raise TypeError
    message = json.dumps(message)
    sock.send(message.encode(encoding))


def get_message(sock, encoding='ascii') -> dict:
    response = sock.recv(BYTES_RECV_SIZE)
    if isinstance(response, bytes):
        json_response = response.decode(encoding)
        if json_response:
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError
        raise ValueError
    raise ValueError


def get_unix_time_str():
    unix_time_str = time.ctime(time.time()) + '\n'
    return unix_time_str


def get_datetime_from_unix_str(unix_str: str):
    locale.setlocale(locale.LC_TIME, 'en_US.utf8')
    return datetime.strptime(unix_str.strip(), "%a %b %d %H:%M:%S %Y")
