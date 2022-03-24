from django.urls import path
from .views import api_register

urlpatterns = [
    path('register/', api_register, name="ws_api_register"),
]
