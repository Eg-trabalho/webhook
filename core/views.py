import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        # Validação do Webhook
        VERIFY_TOKEN = "seu_token_de_verificacao"
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return JsonResponse({"hub.challenge": challenge})
        else:
            return JsonResponse({"error": "Token de verificação inválido"}, status=403)

    elif request.method == "POST":
        # Receber notificações do WhatsApp
        try:
            payload = json.loads(request.body)
            print("Recebido:", payload)
            
            # Processar a mensagem recebida
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        messages = change["value"]["messages"]
                        for message in messages:
                            resposta_message(message)

            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            print("Erro:", str(e))
            return JsonResponse({"error": "Erro no processamento"}, status=500)

def resposta_message(message):
    """
    Lógica para processar mensagens recebidas.
    """
    from_number = message["from"]  # Número do remetente
    text = message.get("text", {}).get("body", "")  # Conteúdo da mensagem
    print(f"Mensagem recebida de {from_number}: {text}")
    # Adicione lógica para responder à mensagem aqui
