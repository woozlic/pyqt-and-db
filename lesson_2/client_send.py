import logging
from socket import AF_INET, SOCK_STREAM, socket
import argparse

from common.variables import PORT, ACT_PRESENCE, HOST, ACT_MESSAGE
from common.utils import get_unix_time_str, send_message, get_message
import log.client_log_config
from common.decorators import log

logger = logging.getLogger('client')


@log
def handle_answer(message):
    RESPONSES = {
        200: 'All right'
    }
    resp = message['response']
    if resp in RESPONSES:
        logger.info(f'Response: {message["msg"]}')


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

@log
def create_message(message: str, account_name='guest'):

    message_dict = {
        "action": ACT_MESSAGE,
        "time": get_unix_time_str(),
        "type": "status",
        "user": {
            "account_name": account_name,
            "status": "online"
        },
        "msg": message,
    }
    return message_dict


def main():
    parser = argparse.ArgumentParser(description='A client')
    parser.add_argument("address", help='Server\'s address. Default: 127.0.0.1', nargs='?', default=HOST)
    parser.add_argument("port", help='Server\'s port. Default: 7777', nargs='?', default=PORT)
    args = parser.parse_args()
    logger.debug(f'Args: {args.address}, {args.port}')
    with socket(AF_INET, SOCK_STREAM) as s:
        host = args.address
        port = int(args.port)
        try:
            s.connect((host, port))
            logger.debug(f'Connected to {host}:{port}')
            print('SENDING MOD')
            while True:
                message_input = input(f"Enter a message: ")
                if not message_input:
                    break
                message = create_message(message_input)
                logger.debug(f'Created message: {message}, sending...')
                send_message(s, message)
                # answer = get_message(s)
                # logger.debug(f'Got an answer from server: {answer}')
                # handle_answer(answer)
        except ConnectionRefusedError:
            logger.error('Can\'t connect to a server')


if __name__ == '__main__':
    main()
