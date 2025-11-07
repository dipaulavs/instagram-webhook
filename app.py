#!/usr/bin/env python3
"""
Instagram Webhook Server
Recebe e processa webhooks do Instagram (mensagens, comentários, menções)
"""
import os
import hmac
import hashlib
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Configurações
PORT = int(os.getenv('PORT', 8080))
VERIFY_TOKEN = os.getenv('INSTAGRAM_VERIFY_TOKEN', 'meu_token_secreto_123')
APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET', '')

# Logs
def log(message):
    """Log com timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# Validação de Signature
def verify_signature(payload, signature):
    """
    Verifica assinatura do webhook para garantir autenticidade
    """
    if not APP_SECRET:
        log("⚠️  APP_SECRET não configurado - pulando validação")
        return True

    expected_signature = 'sha256=' + hmac.new(
        APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

# Healthcheck
@app.route('/health', methods=['GET'])
def health():
    """Endpoint de healthcheck"""
    return jsonify({
        'status': 'healthy',
        'service': 'instagram-webhook',
        'timestamp': datetime.now().isoformat()
    })

# Validação do Webhook (GET)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Instagram envia GET request para validar o webhook
    Parâmetros: hub.mode, hub.verify_token, hub.challenge
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    log(f"📥 Validação recebida - Mode: {mode}, Token válido: {token == VERIFY_TOKEN}")

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        log("✅ Webhook validado com sucesso!")
        return challenge, 200
    else:
        log("❌ Erro na validação do webhook")
        return 'Erro na validação', 403

# Receber Webhooks (POST)
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """
    Recebe webhooks do Instagram
    Eventos: messages, comments, mentions, etc
    """
    try:
        # Validar signature
        signature = request.headers.get('X-Hub-Signature-256', '')
        if APP_SECRET and not verify_signature(request.data, signature):
            log("❌ Assinatura inválida!")
            return 'Assinatura inválida', 403

        # Parse payload
        data = request.json

        if not data:
            log("⚠️  Payload vazio")
            return 'OK', 200

        log(f"📨 Webhook recebido: {data.get('object', 'unknown')}")

        # Processar eventos do Instagram
        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                process_entry(entry)

        return 'OK', 200

    except Exception as e:
        log(f"❌ Erro ao processar webhook: {e}")
        return 'OK', 200  # Sempre retornar 200 para Instagram não reenviar

def process_entry(entry):
    """
    Processa cada entry do webhook
    """
    entry_id = entry.get('id')
    entry_time = entry.get('time')

    log(f"🔄 Processando entry {entry_id}")

    # Processar mensagens
    if 'messaging' in entry:
        for messaging_event in entry['messaging']:
            if 'message' in messaging_event:
                handle_message(messaging_event)
            elif 'postback' in messaging_event:
                handle_postback(messaging_event)
            elif 'reaction' in messaging_event:
                handle_reaction(messaging_event)
            elif 'read' in messaging_event:
                handle_read(messaging_event)

    # Processar comentários/menções/stories
    if 'changes' in entry:
        for change in entry['changes']:
            field = change.get('field')
            value = change.get('value')

            if field == 'comments':
                handle_comment(value)
            elif field == 'mentions':
                handle_mention(value)
            elif field == 'story_insights':
                handle_story_insights(value)

def handle_message(event):
    """
    Processa mensagem recebida
    """
    sender_id = event['sender']['id']
    recipient_id = event['recipient']['id']
    timestamp = event['timestamp']
    message = event.get('message', {})

    message_text = message.get('text', '')
    attachments = message.get('attachments', [])

    log(f"💬 Mensagem de {sender_id}: {message_text}")

    # Sua lógica de resposta aqui
    # Ex: Chamar IA, processar comando, salvar no banco, etc
    # send_message(sender_id, "Recebi sua mensagem!")

def handle_comment(comment_data):
    """
    Processa comentário em post
    """
    comment_id = comment_data.get('id')
    comment_text = comment_data.get('text')
    from_user = comment_data.get('from', {})
    username = from_user.get('username', 'unknown')

    log(f"💬 Comentário de @{username}: {comment_text}")

    # Sua lógica de resposta aqui
    # Ex: Responder comentário, moderar, etc
    # reply_to_comment(comment_id, "Obrigado pelo comentário!")

def handle_mention(mention_data):
    """
    Processa menção (@seu_usuario)
    """
    media_id = mention_data.get('media_id')
    comment_id = mention_data.get('comment_id')

    log(f"📢 Menção recebida - Media: {media_id}, Comment: {comment_id}")

    # Sua lógica aqui
    # Ex: Buscar detalhes do comentário na Graph API

def handle_postback(event):
    """
    Processa clique em botão
    """
    sender_id = event['sender']['id']
    postback = event.get('postback', {})
    payload = postback.get('payload')

    log(f"🔘 Postback de {sender_id}: {payload}")

    # Sua lógica de fluxo aqui
    # Ex: Processar ação do botão

def handle_reaction(event):
    """
    Processa reação em mensagem
    """
    sender_id = event['sender']['id']
    reaction = event.get('reaction', {})
    emoji = reaction.get('emoji', '')

    log(f"❤️ Reação de {sender_id}: {emoji}")

def handle_read(event):
    """
    Processa status de leitura
    """
    sender_id = event['sender']['id']
    log(f"👁️  Mensagem lida por {sender_id}")

def handle_story_insights(insights_data):
    """
    Processa métricas de story
    """
    media_id = insights_data.get('media_id')
    impressions = insights_data.get('impressions')
    reach = insights_data.get('reach')

    log(f"📊 Story {media_id} - Impressões: {impressions}, Alcance: {reach}")

# Página inicial
@app.route('/', methods=['GET'])
def index():
    """Informações do serviço"""
    return jsonify({
        'service': 'Instagram Webhook Server',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'webhook_validation': '/webhook (GET)',
            'webhook_events': '/webhook (POST)'
        },
        'events_supported': [
            'messages',
            'comments',
            'mentions',
            'postbacks',
            'reactions',
            'story_insights'
        ],
        'environment': 'Docker Swarm + Traefik',
        'url': 'https://instagram-webhook.loop9.com.br'
    })

if __name__ == '__main__':
    log(f"🚀 Instagram Webhook Server iniciando na porta {PORT}...")
    log(f"🔑 Verify Token: {VERIFY_TOKEN[:10]}...")
    log(f"🔒 App Secret: {'Configurado' if APP_SECRET else 'Não configurado (validação desabilitada)'}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
