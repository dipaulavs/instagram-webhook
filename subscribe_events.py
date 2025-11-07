#!/usr/bin/env python3
"""
Script para subscrever eventos do Instagram via API
Uso: python3 subscribe_events.py
"""
import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
PAGE_ACCESS_TOKEN = os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN')
PAGE_ID = os.getenv('INSTAGRAM_PAGE_ID')
GRAPH_API_VERSION = 'v18.0'

def get_instagram_account_id(page_id, page_token):
    """
    Obtém Instagram Business Account ID da página Facebook
    """
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}"
    params = {
        'fields': 'instagram_business_account',
        'access_token': page_token
    }

    print("📡 Buscando Instagram Business Account ID...")
    response = requests.get(url, params=params)
    data = response.json()

    if 'instagram_business_account' in data:
        ig_id = data['instagram_business_account']['id']
        print(f"✅ Instagram Account ID: {ig_id}")
        return ig_id
    else:
        print(f"❌ Erro: {data}")
        print("\n💡 Certifique-se de que:")
        print("   1. A página Facebook está conectada a uma conta Instagram Business")
        print("   2. O Page Access Token tem permissões corretas")
        return None

def subscribe_webhooks(ig_account_id, page_token, events):
    """
    Subscreve eventos de webhook
    """
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_account_id}/subscribed_apps"
    params = {
        'subscribed_fields': ','.join(events),
        'access_token': page_token
    }

    print(f"\n📡 Subscrevendo eventos: {', '.join(events)}...")
    response = requests.post(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Subscrição criada com sucesso!")
            return True
        else:
            print(f"⚠️  Resposta inesperada: {data}")
            return False
    else:
        print(f"❌ Erro na subscrição: {response.status_code}")
        print(response.json())
        return False

def get_active_subscriptions(ig_account_id, page_token):
    """
    Lista subscrições ativas
    """
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_account_id}/subscribed_apps"
    params = {'access_token': page_token}

    print("\n📡 Verificando subscrições ativas...")
    response = requests.get(url, params=params)
    data = response.json()

    if 'data' in data and len(data['data']) > 0:
        subscriptions = data['data'][0].get('subscribed_fields', [])
        print(f"✅ Eventos subscritos: {', '.join(subscriptions)}")
        return subscriptions
    else:
        print("⚠️  Nenhuma subscrição ativa")
        return []

def main():
    """
    Configuração completa de webhooks
    """
    print("=" * 60)
    print("🚀 CONFIGURAÇÃO DE WEBHOOKS - INSTAGRAM")
    print("=" * 60)

    # Validar configurações
    if not PAGE_ACCESS_TOKEN:
        print("\n❌ Erro: INSTAGRAM_PAGE_ACCESS_TOKEN não configurado")
        print("\n💡 Configure no arquivo .env:")
        print("   INSTAGRAM_PAGE_ACCESS_TOKEN=EAAxxxxx...")
        return

    if not PAGE_ID:
        print("\n❌ Erro: INSTAGRAM_PAGE_ID não configurado")
        print("\n💡 Configure no arquivo .env:")
        print("   INSTAGRAM_PAGE_ID=123456789")
        return

    print(f"\n📋 Configurações:")
    print(f"   Page ID: {PAGE_ID}")
    print(f"   Token: {PAGE_ACCESS_TOKEN[:20]}...")

    # 1. Obter Instagram Account ID
    print(f"\n{'=' * 60}")
    print("ETAPA 1: Obter Instagram Account ID")
    print("=" * 60)
    ig_id = get_instagram_account_id(PAGE_ID, PAGE_ACCESS_TOKEN)

    if not ig_id:
        print("\n❌ Falha ao obter Instagram Account ID")
        return

    # 2. Subscrever eventos
    print(f"\n{'=' * 60}")
    print("ETAPA 2: Subscrever Eventos")
    print("=" * 60)

    events = [
        'messages',              # Mensagens diretas
        'comments',              # Comentários em posts
        'mentions',              # Menções (@seu_usuario)
        'messaging_postbacks',   # Cliques em botões
        'messaging_handover',    # Transferência bot/humano
        'message_reactions',     # Reações em mensagens
        'messaging_seen'         # Status de leitura
    ]

    success = subscribe_webhooks(ig_id, PAGE_ACCESS_TOKEN, events)

    if not success:
        print("\n❌ Falha na subscrição")
        return

    # 3. Verificar subscrições
    print(f"\n{'=' * 60}")
    print("ETAPA 3: Verificar Subscrições")
    print("=" * 60)

    active = get_active_subscriptions(ig_id, PAGE_ACCESS_TOKEN)

    # Resumo final
    print(f"\n{'=' * 60}")
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"\n📋 Resumo:")
    print(f"   Instagram Account ID: {ig_id}")
    print(f"   Eventos subscritos: {len(active)}")
    print(f"   Lista: {', '.join(active)}")

    print(f"\n🌐 Próximos Passos:")
    print(f"   1. Webhook URL configurada no Meta Dashboard:")
    print(f"      https://instagram-webhook.loop9.com.br/webhook")
    print(f"   2. Testar enviando mensagem DM no Instagram")
    print(f"   3. Ver logs: ssh root@82.25.68.132")
    print(f"                docker service logs instagram-webhook_app -f")

if __name__ == '__main__':
    main()
