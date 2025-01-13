import csv
import json
import os
import time
import requests
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import garota


logging.basicConfig(
    level=logging.INFO,       # Nível mínimo de mensagens a serem registradas
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato da mensagem
    datefmt="%d-%m-%Y %H:%M:%S"  # Formato da data
)


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        VERIFY_TOKEN = "1234"
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            logging.info("Webhook verificado com sucesso.")
            return HttpResponse(challenge, content_type="text/plain", status=200)
        else:
            logging.warning("Token de verificação inválido. Token recebido: %s", token)
            return JsonResponse({"error": "Token de verificação inválido"}, status=403)

    elif request.method == "POST":
        try:
            payload = json.loads(request.body)
            logging.info("Payload recebido: %s", payload)
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        messages = change["value"].get("messages", [])
                        for message in messages:
                            process_incoming_message(message)
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            logging.error("Erro no processamento do webhook: %s", e, exc_info=True)
            return JsonResponse({"error": "Erro no processamento"}, status=500)


def process_incoming_message(message):
    from_number = message.get("from", "número desconhecido")  # Número do cliente que enviou a mensagem
    text = message.get("text", {}).get("body", "")  # Conteúdo da mensagem

    logging.info(f"Mensagem recebida de {from_number}: {text}")

    try:
    # Respostas baseadas no texto recebido
        if text == "Yes":
            send_text_message(from_number, "Ótimo, nosso site está à sua espera! Acesse www.exclusivegirls.net para começar.")
        elif text == "No":
            send_text_message(from_number, "Que pena! Se mudar de ideia, estaremos aqui para te ajudar.")
        else:
            send_text_message(from_number, "Desculpe, não entendi sua resposta. Por favor, escolha uma das opções disponíveis.")
    except Exception as e:
        logging.error(f"Erro ao processar a mensagem de {from_number}: {e}")

def send_text_message(phone_number, text):
    """
    Função para enviar uma mensagem de texto simples via WhatsApp.
    """
    url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": text},
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info("Mensagem enviada para %s. Status: %s", phone_number, response.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Erro ao enviar mensagem para %s: %s", phone_number, e, exc_info=True)

def send_interactive_message(phone_number, nickname):
    url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages" 
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data ={
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "5585991389624", 
        "type": "template",
        "template": {
            "name": "msg_botoes",
            "language": {
                "code": "en_US" 
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        { "type": "text", "text": "Davi" },  
                        { "type": "text", "text": "CS Mutual" }, 
                        { "type": "text", "text": "suspicious" },  
                        { "type": "text", "text": "CS Mutual debit" }, 
                        { "type": "text", "text": "1234" },  
                        { "type": "text", "text": "Jan 1, 2024" },  
                        { "type": "text", "text": "Jasper's Market" },  
                        { "type": "text", "text": "$12.34" } 
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao enviar mensagem para {phone_number}: {e}")
        return False

    # Se a mensagem foi enviada com sucesso (status 200)
    if response.status_code == 200:
        # Salvar no banco de dados
        garota.objects.get_or_create(phone_number=phone_number, defaults={"nickname": nickname})


    logging.info(f"Mensagem enviada para {phone_number}. Status: {response.status_code}, Resposta: {response.text}")


@csrf_exempt
def read_csv_and_send_messages(request):
    try:
        # Verificar se o arquivo CSV existe
        csv_file_path = os.path.join(settings.BASE_DIR, "csv_files", "contatos.csv")
        if not os.path.exists(csv_file_path):
            logging.error("Arquivo CSV não encontrado em: %s", csv_file_path)
            return JsonResponse({"error": f"O arquivo CSV não foi encontrado em: {csv_file_path}"}, status=400)
        
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

            if not rows:
                logging.warning("O arquivo CSV está vazio.")
                return JsonResponse({"error": "O arquivo CSV está vazio!"}, status=400)

            # Limitar para os primeiros 100 (ou o tamanho do CSV, se menor que 100)
            to_process = rows[:2]
            remaining_contacts = rows[2:]  # Contatos que não serão processados agora
            processed_successfully = []  # Lista para contatos enviados com sucesso

            for idx, contact in enumerate(to_process):
                nickname = contact.get("Escort Nickname *")
                phone_number = contact.get("WhatsApp Mobile Number (with country code 351) *")

                if not nickname or not phone_number:
                    logging.warning(f"Dados ausentes na linha {idx+1}: {contact}")
                    continue

                # Remover espaços no número de telefone
                phone_number = phone_number.replace(" ", "")

                try:
                    # Enviar a mensagem
                    if send_interactive_message(phone_number, nickname):
                        logging.info(f"Mensagens enviadas com sucesso {len(processed_successfully)}/{len(to_process)} para {phone_number}")
                        processed_successfully.append(contact)  # Adicionar à lista de sucesso
                except Exception as e:
                    logging.error(f"Erro ao enviar mensagem para {phone_number}: {e}")

                time.sleep(1)

            # Atualizar o arquivo CSV com os contatos restantes
            contacts_to_keep = remaining_contacts + [
                contact for contact in to_process if contact not in processed_successfully
            ]

            try:
                with open(csv_file_path, "w", encoding="utf-8", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writer.writerows(contacts_to_keep)
            except IOError as e:
                logging.error(f"Erro ao salvar o arquivo CSV: {e}")
                return JsonResponse({"error": "Erro ao atualizar o arquivo CSV"}, status=500)
        
        
        return JsonResponse({
            "status": "success",
            "message": f"Mensagens enviadas com sucesso {len(processed_successfully)}/{len(to_process)} para {phone_number}"
        }, status=200)

    except Exception as e:
        logging.critical("Erro durante a leitura ou envio de mensagens: %s", e, exc_info=True)
        return JsonResponse({"error": "Erro interno do servidor", "details": str(e)}, status=500)