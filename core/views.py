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

    print(f"Mensagem enviada para {nickname}, Número: {phone_number}")


@csrf_exempt
def read_csv_and_send_messages(request):
    try:
        # Verificar se o arquivo CSV existe
        csv_file_path = os.path.join(settings.BASE_DIR, "csv_files", "contatos.csv")
        if not os.path.exists(csv_file_path):
            return JsonResponse({"error": f"O arquivo CSV não foi encontrado em: {csv_file_path}"}, status=400)
        
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            # Garantir que o reader tem dados
            rows = list(reader)
            if not rows:
                return JsonResponse({"error": "O arquivo CSV está vazio!"}, status=400)
            
            # Limitar para os primeiros 100 (ou o tamanho do CSV, se for menor que 100)
            cnt = 0
            for idx in range(min(100, len(rows))):
                nickname = rows[idx].get("Escort Nickname *")
                phone_number = rows[idx].get("WhatsApp Mobile Number (with country code 351) *")
                
                if not nickname or not phone_number:
                    print(f"Erro ao processar a linha {idx+1}: {rows[idx]}")
                    continue

                # Remover espaços do número de telefone
                cnt +=1
                phone_number = phone_number.replace(" ", "")
                
                # Chamar a função de envio de mensagem
                send_interactive_message(phone_number, nickname)

        return JsonResponse({"status": "success", "message": f"{cnt} Mensagens simuladas enviadas com sucesso!"}, status=200)

    except Exception as e:
        print("Erro durante a leitura ou envio de mensagens:", str(e))
        return JsonResponse({"error": "Erro interno do servidor", "details": str(e)}, status=500)