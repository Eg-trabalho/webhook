from django.urls import path
from .views import whatsapp_webhook, read_csv_and_send_messages, ver_numeros, del_numeros

urlpatterns = [
    path("v1/", whatsapp_webhook, name="whatsapp_webhook"),
    path("teste/", read_csv_and_send_messages, name="teste"),
    path("numeros/", ver_numeros, name="ver_numeros"),
    path("del_numeros/", del_numeros, name="del_numeros"),
]
