from django.urls import path
from .views import whatsapp_webhook, read_csv_and_send_messages, ver_numeros, del_numeros, ver_csv, ver_csv_inteiro

urlpatterns = [
    path("v1/", whatsapp_webhook, name="whatsapp_webhook"),
    path("teste/", read_csv_and_send_messages, name="teste"),
    path("numeros/", ver_numeros, name="ver_numeros"),
    path("del_numeros/", del_numeros, name="del_numeros"),
    path("csv/", ver_csv, name="ver_csv"),
    path("csv_inteiro/", ver_csv_inteiro, name="ver_csv_inteiro"),
]
