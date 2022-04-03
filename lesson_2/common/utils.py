import time
from .variables import BYTES_RECV_SIZE
import json
import logging


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
