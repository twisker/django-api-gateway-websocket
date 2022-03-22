from django.test import TestCase
from .core import WebSocketProvider


class DjangoAPIGatewayWSTestCase(TestCase):

    def setUp(self):
        self.__app_key = "204036994"
        self.__app_secret = "V9pcE4wZksO7Mgg2Xd17VrGbeuqbRuiU"
        self.__notify_url = "http://93bbada9a26c41e7adfe1fdac253b397-cn-hangzhou.alicloudapi.com/sendUserInfo/"

    def test_001(self):
        app_key = "204036994"
        app_secret = "V9pcE4wZksO7Mgg2Xd17VrGbeuqbRuiU"
        notify_url = "http://93bbada9a26c41e7adfe1fdac253b397-cn-hangzhou.alicloudapi.com/sendUserInfo/"
        client = WebSocketProvider(app_key, app_secret, notify_url)
        client.post(notify_url, json={
            "from": 0,
            "message": "test"
        }, headers={
            "x-ca-deviceid": "6690A727-4E9A-4611-9022-47FD28909831@10025591"
        })
