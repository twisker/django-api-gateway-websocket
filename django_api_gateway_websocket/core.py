
from .models import WebSocketOnlineDevice


class WebSocketProvider(object):

    def __init__(self, app_key, app_secret, notify_url):
        self.__AG_NOTIFY_URL = notify_url
        self.__AG_APP_KEY = app_key
        self.__AG_APP_SECRET = app_secret
        self.__AG_CLIENT = None
        self.__provider_id = id(self)

    @property
    def all_online_users(self):
        return WebSocketOnlineDevice.objects.filter(provider_id=self.__provider_id)

    def register(self, device_id, user_id):
        instance = WebSocketOnlineDevice.objects.get_or_create(
            device_id=device_id,
            provider_id=self.__provider_id
        )
        instance.user_id = user_id
        instance.save()

    def send_to_online_device_instance(self, instance, message, from_id):
        if instance is None:
            return False
        try:
            result = self.__AG_CLIENT.post(self.__AG_NOTIFY_URL, {
                "data": {
                    "from": from_id,
                    "message": message
                },
                "headers": {
                    "x-ca-deviceid": instance.device_id
                }
            })
            instance.save()
            return True
        except Exception:
            instance.delete()
            return False

    def send_to_device(self, device_id, message, from_id):
        instance = self.all_online_users.filter(device_id=device_id).first()
        self.send_to_online_device_instance(instance, message, from_id)

    def send_to_user(self, user_id, message, from_id):
        for instance in self.all_online_users.exclude(device_id=from_id).filter(user_id=user_id):
            self.send_to_online_device_instance(instance, message, from_id)

    def send_to_all(self, message, from_id):
        for instance in self.all_online_users.exclude(device_id=from_id):
            self.send_to_online_device_instance(instance, message, from_id)

    def destroy(self):
        for instance in self.all_online_users:
            # todo 是否需要先通知这个device？
            instance.delete()


