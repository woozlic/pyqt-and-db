import json
from unittest import TestCase, main
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ENCODING
from common.utils import send_message, get_message, get_unix_time_str


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message: dict):
        json_text_message = json.dumps(self.test_dict)
        self.encoded_message = json_text_message.encode(ENCODING)
        self.received_message = message

    def recv(self, max_bytes):
        json_text_message = json.dumps(self.test_dict)
        return json_text_message.encode(ENCODING)


class TestUtils(TestCase):
    test_dict_send = {
        "action": "presence",
        "time": 1,
        "type": "status",
        "user": {
            "account_name": "Not a guest",
            "status": "online"
        }
    }

    def test_send_message_ok(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_send_message_type_error(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertRaises(TypeError, send_message, test_socket, "wrong_dict")

    def test_get_message(self):
        test_socket = TestSocket(self.test_dict_send)
        received_message = get_message(test_socket)
        self.assertEqual(received_message, self.test_dict_send)


if __name__ == '__main__':
    main()
