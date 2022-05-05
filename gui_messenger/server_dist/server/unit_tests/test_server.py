from unittest import TestCase, main
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import process_client_message


class TestServer(TestCase):
    answer_ok = {
        "response": 200
    }
    answer_wrong = {
        "response": 400,
        "error": "Bad Request"
    }

    def test_process_client_message_ok(self):
        message = {
            "action": "presence",
            "time": 1,
            "user": "guest"
        }
        self.assertEqual(process_client_message(message), self.answer_ok)

    def test_process_client_message_wrong(self):
        message = {
            "action": "nothing",
            "time": 1,
            "user": "guest"
        }
        self.assertEqual(process_client_message(message), self.answer_wrong)


if __name__ == '__main__':
    main()
