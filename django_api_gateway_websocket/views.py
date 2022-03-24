from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from .core import WebSocketProvider


ws_provider = None

try:
    ws_provider = WebSocketProvider(
        settings.WS_APP_KEY,
        settings.WS_APP_SECRET,
        settings.WS_NOTIFY_URL
    )
except Exception:
    pass


@csrf_exempt
def api_register(request):
    if ws_provider is None:
        return HttpResponseNotFound("WS_ Settings Not Found")
    if "x-ca-deviceid" not in request.headers:
        return HttpResponseBadRequest("Required Header x-ca-deviceid Not Found")
    user_id = request.GET.get("user_id", None)
    if user_id is None:
        return HttpResponseBadRequest("user_id required")
    device_id = request.headers["x-ca-deviceid"]
    channel = request.GET.get("channel", "")
    ws_provider.register(device_id, user_id, channel)
    return JsonResponse({
        "success": True,
        "device_id": device_id
    })
