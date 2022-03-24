from django.contrib import admin
from .models import WebSocketOnlineDevice


class WebSocketOnlineDeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "device_id", "user_id", "channel", "registered_datetime", "last_active_datetime")
    list_display_links = ("id", "device_id",)
    list_filter = ("channel", "registered_datetime", )
    search_fields = ("device_id", "user_id", "channel",)


admin.site.register(WebSocketOnlineDevice)
