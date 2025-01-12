from django.urls import path
from .views import whatsapp_webhook, read_csv_and_send_messages

urlpatterns = [
    path("v1/", whatsapp_webhook, name="whatsapp_webhook"),
    path("teste/", read_csv_and_send_messages, name="teste"),
]
