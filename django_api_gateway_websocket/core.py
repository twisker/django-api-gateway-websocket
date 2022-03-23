import base64
import hashlib
import hmac
import json as json_lib
import time
import urllib.parse
import uuid
from urllib.parse import parse_qs, urlsplit
from requests import Request, Session, PreparedRequest
from .models import WebSocketOnlineDevice


SYSTEM_HEADERS = (
    X_CA_SIGNATURE, X_CA_SIGNATURE_HEADERS, X_CA_TIMESTAMP, X_CA_NONCE, X_CA_KEY, X_CA_SIGNATURE_METHOD
) = (
    'X-Ca-Signature', 'X-Ca-Signature-Headers', 'X-Ca-Timestamp', 'X-Ca-Nonce', 'X-Ca-Key', 'X-Ca-Signature-Method'
)

HTTP_HEADERS = (
    HTTP_HEADER_ACCEPT, HTTP_HEADER_CONTENT_MD5,
    HTTP_HEADER_CONTENT_TYPE, HTTP_HEADER_USER_AGENT, HTTP_HEADER_DATE
) = (
    'Accept', 'Content-MD5',
    'Content-Type', 'User-Agent', 'Date'
)

HTTP_PROTOCOL = (
    HTTP, HTTPS
) = (
    'http', 'https'
)

HTTP_METHOD = (
    GET, POST, PUT, DELETE, HEADER
) = (
    'GET', 'POST', 'PUT', 'DELETE', 'HEADER'
)

CONTENT_TYPE = (
    CONTENT_TYPE_FORM, CONTENT_TYPE_STREAM,
    CONTENT_TYPE_JSON, CONTENT_TYPE_XML, CONTENT_TYPE_TEXT
) = (
    'application/x-www-form-urlencoded', 'application/octet-stream',
    'application/json', 'application/xml', 'application/text'
)

BODY_TYPE = (
    FORM, STREAM
) = (
    'FORM', 'STREAM'
)


def _build_resource(uri="", body={}):
    if "?" in uri:
        uri_array = uri.split("?")
        uri = uri_array[0]
        query_str = uri_array[1]
        if not body:
            body = {}
        if query_str:
            query_str_array = query_str.split("&")
            for query in query_str_array:
                query_array = query.split("=")
                if query_array[0] not in body:
                    body[query_array[0]] = query_array[1]

    resource = [uri]
    if body:
        resource.append("?")
        param_list = list(body.keys())
        param_list.sort()
        first = True
        for key in param_list:
            if not first:
                resource.append("&")
            first = False

            if body[key]:
                resource.append(key)
                resource.append("=")
                resource.append(body[key])
            else:
                resource.append(key)

    if resource is None:
        return ''

    return "".join(str(x) for x in resource)


def _format_header(headers={}):
    lf = '\n'
    temp_headers = []
    if len(headers) > 0:
        header_list = list(headers.keys())
        header_list.sort()
        signature_headers = []
        for k in header_list:
            if k.lower().startswith("x-ca-"):
                temp_headers.append(k)
                temp_headers.append(":")
                temp_headers.append(str(headers[k]))
                temp_headers.append(lf)
                signature_headers.append(k)
        headers[X_CA_SIGNATURE_HEADERS] = ','.join(signature_headers)
    return ''.join(temp_headers)


def _sign(source: str, secret: str):
    h = hmac.new(secret.encode("utf-8"), source.encode("utf-8"), hashlib.sha256)
    signature = base64.encodebytes(h.digest()).strip()
    return signature.decode("ascii")


def _md5(content):
    m = hashlib.md5()
    m.update(content)
    return base64.encodebytes(m.digest()).strip().decode("ascii")


class WebSocketProvider(object):

    def __init__(self, app_key, app_secret, notify_url):
        self.__AG_NOTIFY_URL = notify_url
        self.__AG_APP_KEY = app_key
        self.__AG_APP_SECRET = app_secret
    
    @classmethod
    def build_sign_str(cls, uri=None, method=None, headers=None, body=None):

        body_dict = {}

        lf = '\n'
        string_to_sign = []
        string_to_sign.append(method)

        string_to_sign.append(lf)
        if HTTP_HEADER_ACCEPT in headers and headers[HTTP_HEADER_ACCEPT]:
            string_to_sign.append(headers[HTTP_HEADER_ACCEPT])

        string_to_sign.append(lf)
        if HTTP_HEADER_CONTENT_MD5 in headers and headers[HTTP_HEADER_CONTENT_MD5]:
            string_to_sign.append(headers[HTTP_HEADER_CONTENT_MD5])

        string_to_sign.append(lf)
        if HTTP_HEADER_CONTENT_TYPE in headers and headers[HTTP_HEADER_CONTENT_TYPE]:
            string_to_sign.append(headers[HTTP_HEADER_CONTENT_TYPE])
            if headers[HTTP_HEADER_CONTENT_TYPE] == CONTENT_TYPE_FORM:
                body_dict = parse_qs(body)

        string_to_sign.append(lf)
        if HTTP_HEADER_DATE in headers and headers[HTTP_HEADER_DATE]:
            string_to_sign.append(headers[HTTP_HEADER_DATE])

        string_to_sign.append(lf)
        string_to_sign.append(_format_header(headers=headers))
        string_to_sign.append(_build_resource(uri=uri, body=body_dict))

        return ''.join(string_to_sign)

    def build_signature(self, request: PreparedRequest):
        request.headers[X_CA_TIMESTAMP] = str(int(time.time() * 1000))
        request.headers[X_CA_KEY] = self.__AG_APP_KEY
        request.headers[X_CA_NONCE] = str(uuid.uuid4())
        if not HTTP_HEADER_CONTENT_TYPE in request.headers:
            request.headers[HTTP_HEADER_CONTENT_TYPE] = CONTENT_TYPE_JSON
        if not HTTP_HEADER_ACCEPT in request.headers:
            request.headers[HTTP_HEADER_ACCEPT] = CONTENT_TYPE_JSON
        request.headers[X_CA_SIGNATURE_METHOD] = "HmacSHA256"
        if request.body is not None and len(request.body) > 0 and \
                not request.headers[HTTP_HEADER_CONTENT_TYPE] == CONTENT_TYPE_FORM:
            request.headers[HTTP_HEADER_CONTENT_MD5] = _md5(request.body)
        str_to_sign = self.build_sign_str(uri=request.path_url, method=request.method,
                                          headers=request.headers, body=request.body)
        # print("==============================================")
        # print(str_to_sign)
        # print("==============================================")
        request.headers[X_CA_SIGNATURE] = _sign(str_to_sign, self.__AG_APP_SECRET)

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

    def post(self, url, data=None, json=None, headers=None):
        # return self.__post_with_sdk(url, data=data, json=json, headers=headers)
        return self.__post_with_requests(url, data=data, json=json, headers=headers)

    def __post_with_sdk(self, url, data=None, json=None, headers=None):
        from .sdk.http import request
        from .sdk import client
        cli = client.DefaultClient(app_key=self.__AG_APP_KEY, app_secret=self.__AG_APP_SECRET)
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)
        url = path
        if query is not None and len(query) > 0:
            url += f"?{query}"
        if fragment is not None and len(fragment) > 0:
            url += f"#{fragment}"
        req_post = request.Request(host=netloc, protocol=HTTP, url=url, method="POST", time_out=30000, headers=headers)
        body = {}
        if data is not None:
            body = data
        elif json is not None:
            body = json
        req_post.set_body(bytearray(source=json_lib.dumps(body), encoding="utf8"))
        req_post.set_content_type(CONTENT_TYPE_STREAM)
        return cli.execute(req_post)

    def __post_with_requests(self, url, data=None, json=None, headers=None):
        session = Session()
        req_post = Request(POST, url=url, json=json, data=data, headers=headers)
        prepared = req_post.prepare()
        self._logging(prepared)
        self.build_signature(prepared)
        self._logging(prepared)
        resp = session.send(prepared, timeout=3000, verify=False)
        return resp

    def _logging(self, request):
        for k, v in request.headers.items():
            print(k, v)
        print(request.body)

    def send_to_online_device_instance(self, instance, message, from_id):
        if instance is None:
            return False
        try:
            result = self.post(self.__AG_NOTIFY_URL,
                               json={
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
