
from .models import WebSocketOnlineDevice
from .sdk.client import DefaultClient
from .sdk.http.request import Request
from .sdk.common import constant


class WebSocketProvider(object):

    def __init__(self, app_key, app_secret, notify_host, notify_url):
        self.__AG_NOTIFY_URL = notify_url
        self.__AG_NOTIFY_HOST = notify_host
        self.__AG_APP_KEY = app_key
        self.__AG_APP_SECRET = app_secret
        self.__AG_CLIENT = DefaultClient(app_key=self.__AG_APP_KEY, app_secret=self.__AG_APP_SECRET)

    @classmethod
    def get_all_online_users(cls, channel=""):
        return WebSocketOnlineDevice.objects.filter(channel=channel)

    @classmethod
    def register(cls, device_id, user_id, channel=""):
        instance = WebSocketOnlineDevice.objects.get_or_create(
            device_id=device_id,
            channel=channel
        )
        instance.user_id = user_id
        instance.save()
        return instance

    def post(self, host, url, data=None, headers=None):
        req_post = Request(host=host, url=url, protocol=constant.HTTP, method="POST", time_out=30000)
        if data is not None:
            if type(data) is str:
                data = data.encode("utf-8")
            if type(data) is dict:
                kv_pairs = {}
                for k, v in data.items():
                    if type(k) is str:
                        k = k.encode("utf-8")
                    if type(v) is str:
                        v = v.encode("utf-8")
                    kv_pairs[k] = v
                data = kv_pairs
            req_post.set_body(data)
        if headers is not None:
            req_post.set_headers(headers)
        req_post.set_content_type(constant.CONTENT_TYPE_JSON)
        return self.__AG_CLIENT.execute(req_post)

    def send_to_online_device_instance(self, instance, message, from_id):
        if instance is None:
            return False
        try:
            result = self.post(self.__AG_NOTIFY_HOST, self.__AG_NOTIFY_URL,
                               data={
                                    "from": from_id,
                                    "message": message
                               },
                               headers={
                                    "x-ca-deviceid": instance.device_id
                               })
            instance.save()
            return True
        except Exception:
            instance.delete()
            return False

    def send_to_device(self, device_id, message, from_id, channel=""):
        instance = self.get_all_online_users(channel=channel).filter(device_id=device_id).first()
        self.send_to_online_device_instance(instance, message, from_id)

    def send_to_user(self, user_id, message, from_id, channel=""):
        for instance in self.get_all_online_users(channel=channel).exclude(device_id=from_id).filter(user_id=user_id):
            self.send_to_online_device_instance(instance, message, from_id)

    def send_to_all(self, message, from_id, channel=""):
        for instance in self.get_all_online_users(channel=channel).exclude(device_id=from_id):
            self.send_to_online_device_instance(instance, message, from_id)

    def destroy(self, channel=""):
        for instance in self.get_all_online_users(channel=channel):
            # todo 是否需要先通知这个device？
            instance.delete()
