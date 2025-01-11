import csv
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        VERIFY_TOKEN = "seu_token_de_verificacao"
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return JsonResponse({"hub.challenge": challenge})
        else:
            return JsonResponse({"error": "Token de verificação inválido"}, status=403)

    elif request.method == "POST":
        try:
            payload = json.loads(request.body)
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        messages = change["value"]["messages"]
                        for message in messages:
                            process_incoming_message(message)
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            print("Erro:", str(e))
            return JsonResponse({"error": "Erro no processamento"}, status=500)


def process_incoming_message(message):
    from_number = message["from"]
    text = message.get("text", {}).get("body", "")
    print(f"Mensagem recebida de {from_number}: {text}")
    # Responda com lógica baseada no texto recebido


def send_interactive_message(phone_number, nickname):
    # Simulação do envio de mensagem (sem requisição real)
   

    return {
        "phone_number": phone_number,
        "nickname": nickname
    }
    # Aqui, em vez de enviar para o WhatsApp, só exibimos a simulação no console
    # Adicionar qualquer lógica extra para simulação aqui

def read_csv_and_send_messages():
    csv_file_path = os.path.join(settings.BASE_DIR, "csv_files", "contatos.csv")
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for idx in range(0, 4):
            send_interactive_message(reader[idx]["Escort Nickname *"], reader[idx]["WhatsApp Mobile Number (with country code 351) *"])