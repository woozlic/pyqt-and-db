from unittest import TestCase, main
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import create_presence


class TestClient(TestCase):
    def test_create_presence_guest(self):
        presence = {
            "action": "presence",
            "time": 1,
            "type": "status",
            "user": {
                "account_name": "guest",
                "status": "online"
            }
        }
        answer = create_presence()
        answer["time"] = 1
        self.assertEqual(presence, answer)

    def test_create_presence_not_guest(self):
        presence = {
            "action": "presence",
            "time": 1,
            "type": "status",
            "user": {
                "account_name": "Not a guest",
                "status": "online"
            }
        }
        answer = create_presence("Not a guest")
        answer["time"] = 1
        self.assertEqual(presence, answer)


if __name__ == '__main__':
    main()
