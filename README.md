# 📸 Instagram Webhook Server

Servidor para receber e processar webhooks do Instagram (mensagens, comentários, menções).

**Deployed em:** https://instawebhook.loop9.com.br

---

## 🚀 Quick Start

### 1. Configurar Variáveis (.env)

```bash
# Copiar template
cp .env.example .env

# Editar com suas credenciais
nano .env
```

**Variáveis obrigatórias:**
- `INSTAGRAM_VERIFY_TOKEN` - Token secreto (você define)
- `INSTAGRAM_APP_SECRET` - App Secret do Meta Dashboard
- `INSTAGRAM_PAGE_ACCESS_TOKEN` - Token de acesso da página
- `INSTAGRAM_PAGE_ID` - ID da página Facebook conectada

### 2. Testar Localmente (Opcional)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### 3. Deploy na VPS

```bash
# SSH na VPS
ssh root@82.25.68.132

# Clone repositório (primeira vez)
cd /opt/swarm/automations
git clone git@github.com:SEU-USUARIO/instagram-webhook.git
cd instagram-webhook

# Configurar .env
nano .env
# (adicionar tokens reais)

# Deploy no Swarm
docker stack deploy -c docker-compose.yml instagram-webhook

# Verificar
docker service logs instagram-webhook_app -f
```

### 4. Configurar Meta Dashboard

1. Acessar: https://developers.facebook.com/apps/
2. Webhooks → Editar subscrição
3. **Callback URL:** `https://instagram-webhook.loop9.com.br/webhook`
4. **Verify Token:** (mesmo do .env)
5. **Verificar e salvar**

### 5. Subscrever Eventos

```bash
# Local
python3 subscribe_events.py
```

### 6. Testar

Enviar mensagem DM no Instagram → Ver logs:
```bash
ssh root@82.25.68.132
docker service logs instagram-webhook_app -f
```

---

## 📡 Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Info do serviço |
| `/health` | GET | Healthcheck |
| `/webhook` | GET | Validação do webhook |
| `/webhook` | POST | Recebe eventos |

---

## 🎯 Eventos Suportados

- ✅ **messages** - Mensagens diretas
- ✅ **comments** - Comentários em posts
- ✅ **mentions** - Menções (@seu_usuario)
- ✅ **postbacks** - Cliques em botões
- ✅ **reactions** - Reações em mensagens
- ✅ **messaging_seen** - Status de leitura
- ✅ **story_insights** - Métricas de stories

---

## 🔧 Customização

### Adicionar Lógica de Resposta

Edite `app.py`:

```python
def handle_message(event):
    sender_id = event['sender']['id']
    message_text = event['message'].get('text', '')

    # Sua lógica aqui
    response = process_with_ai(message_text)
    send_message(sender_id, response)
```

### Integrar com N8N

```python
import requests

def send_to_n8n(data):
    url = "https://n8n.loop9.com.br/webhook/instagram-event"
    requests.post(url, json=data)
```

---

## 📊 Logs

```bash
# Tempo real
ssh root@82.25.68.132
docker service logs instagram-webhook_app -f

# Últimas 100 linhas
docker service logs instagram-webhook_app --tail 100
```

---

## 🔐 Segurança

- ✅ Validação de signature (X-Hub-Signature-256)
- ✅ Verify token para validação inicial
- ✅ SSL automático (Let's Encrypt via Traefik)
- ✅ Mesma rede overlay dos serviços (loop9Net)

---

## 🔄 Atualizar Código

```bash
# 1. LOCAL: Editar e commit
git add .
git commit -m "feat: adicionar nova funcionalidade"
git push origin main

# 2. VPS: Pull e re-deploy
ssh root@82.25.68.132
cd /opt/swarm/automations/instagram-webhook
git pull origin main
docker stack deploy -c docker-compose.yml instagram-webhook
```

---

## ❌ Troubleshooting

### Webhook não valida

- Verifique `INSTAGRAM_VERIFY_TOKEN` no .env
- Deve ser EXATAMENTE o mesmo no Meta Dashboard
- Ver logs: `docker service logs instagram-webhook_app`

### Eventos não chegam

- Verificar subscrição: `python3 subscribe_events.py`
- Verificar URL configurada no Meta Dashboard
- Testar enviando mensagem DM real

### Signature inválida

- Verificar `INSTAGRAM_APP_SECRET` no .env
- Obter no Meta Dashboard > Configurações > Básico

---

## 📚 Documentação Relacionada

- **Webhooks Instagram:** [DOCS-API/instagram-webhooks/DOCUMENTACAO-COMPLETA.md](../../../DOCS-API/instagram-webhooks/DOCUMENTACAO-COMPLETA.md)
- **Configuração:** [DOCS-API/instagram-webhooks/CONFIGURACAO-WEBHOOK.md](../../../DOCS-API/instagram-webhooks/CONFIGURACAO-WEBHOOK.md)
- **SWARM:** [SWARM/README.md](../../README.md)

---

**Criado em:** 2025-11-06
**Stack:** Docker Swarm + Traefik + Flask
**URL:** https://instagram-webhook.loop9.com.br
