from django.test import TestCase
from .core import WebSocketProvider


class DjangoAPIGatewayWSTestCase(TestCase):

    def setUp(self):
        self.__app_key = "204036994"
        self.__app_secret = "V9pcE4wZksO7Mgg2Xd17VrGbeuqbRuiU"
        self.__notify_host = ""
        self.__notify_url = ""

    def test_001(self):
        app_key = "204036994"
        app_secret = "V9pcE4wZksO7Mgg2Xd17VrGbeuqbRuiU"
        notify_host = "93bbada9a26c41e7adfe1fdac253b397-cn-hangzhou.alicloudapi.com"
        notify_url = "/sendUserInfo/"
        client = WebSocketProvider(app_key, app_secret, notify_host, notify_url)
        client.post(notify_url, data={
            "from": 0,
            "message": "test"
        }, headers={
            "x-ca-deviceid": "XXX"
        })
