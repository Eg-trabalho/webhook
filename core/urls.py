from django.urls import path
from .views import whatsapp_webhook

urlpatterns = [
    path("v1/", whatsapp_webhook, name="whatsapp_webhook"),
]
