# 📘 Guia Completo de Deploy - Instagram Webhook

## ✅ Status Atual

- ✅ Código desenvolvido e testado
- ✅ Repositório criado no GitHub
- ✅ Credenciais configuradas localmente
- ⏳ Aguardando deploy na VPS

---

## 🚀 DEPLOY NA VPS (Passo a Passo)

### Método 1: Script Automático (Recomendado)

```bash
cd /Users/felipemdepaula/Desktop/ClaudeCode-Workspace/SWARM/automations/instagram-webhook
./DEPLOY.sh
```

**O script irá:**
1. Conectar na VPS
2. Clonar repositório
3. Pedir para você configurar o .env
4. Fazer deploy no Swarm
5. Mostrar logs

---

### Método 2: Manual (Passo a Passo)

#### PASSO 1: SSH na VPS

```bash
ssh root@82.25.68.132
```

#### PASSO 2: Clonar Repositório

```bash
# Criar diretório
mkdir -p /opt/swarm/automations
cd /opt/swarm/automations

# Clonar (repositório é público agora)
git clone https://github.com/dipaulavs/instagram-webhook.git
cd instagram-webhook
```

#### PASSO 3: Configurar .env

```bash
nano .env
```

**Cole este conteúdo:**

```env
# Configurações da Aplicação
AUTOMATION_NAME=instagram-webhook
SUBDOMAIN=instagram-webhook
PORT=8080

# Instagram Webhook Config
INSTAGRAM_VERIFY_TOKEN=meu_token_secreto_123
INSTAGRAM_APP_SECRET=

# Instagram API (para subscrever eventos)
INSTAGRAM_PAGE_ACCESS_TOKEN=EAAPXQG5u0qkBPy2UoHHVTYSVxCO8RSsDbn8h34WZA5ZCQcZBJZC5TmS0ZBPvpVdnzQcxLTGIK4ZCNaBUqO2ZAwJCESumPSusMkFZC9dkFcFWChBud7h0HrB3sctOxLm4L1kK7mdwOZAabUCdxG1cHTryhfBf4gHhZCdR2xMSZBq5FHKZBnqFNtR9fW2n0peeIJfNCeaj8rfxg0QW
INSTAGRAM_PAGE_ID=859614930562831

# Opcional: Para enviar respostas
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841477883364829
```

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

#### PASSO 4: Deploy no Swarm

```bash
docker stack deploy -c docker-compose.yml instagram-webhook
```

**Output esperado:**
```
Creating service instagram-webhook_app
```

#### PASSO 5: Verificar Deploy

```bash
# Ver serviços
docker service ls | grep instagram

# Ver logs
docker service logs instagram-webhook_app -f
```

**Logs esperados:**
```
🚀 Instagram Webhook Server iniciando na porta 8080...
🔑 Verify Token: meu_token...
```

#### PASSO 6: Testar URL

```bash
curl https://instagram-webhook.loop9.com.br
```

**Resposta esperada:**
```json
{
  "service": "Instagram Webhook Server",
  "status": "running",
  "url": "https://instagram-webhook.loop9.com.br"
}
```

---

## 🔧 CONFIGURAR META DASHBOARD

### PASSO 1: Acessar Dashboard

1. Abrir: https://developers.facebook.com/apps/
2. Selecionar seu app ou criar novo
3. Menu lateral → **Produtos** → **Webhooks**

### PASSO 2: Adicionar Webhook

1. Clicar em **Editar subscrição** (ou Adicionar subscrição)
2. Selecionar objeto: **Instagram**

### PASSO 3: Configurar URL

**Callback URL:**
```
https://instagram-webhook.loop9.com.br/webhook
```

**Verify Token:**
```
meu_token_secreto_123
```

### PASSO 4: Verificar

1. Clicar em **Verificar e salvar**
2. Aguardar validação
3. ✅ "URL verificada com sucesso"

**Se falhar:**
- Ver logs: `docker service logs instagram-webhook_app -f`
- Verificar se VERIFY_TOKEN no .env está correto

---

## 📡 SUBSCREVER EVENTOS (Local no Mac)

### PASSO 1: Rodar Script

```bash
cd /Users/felipemdepaula/Desktop/ClaudeCode-Workspace/SWARM/automations/instagram-webhook
python3 subscribe_events.py
```

**Output esperado:**
```
====================================
🚀 CONFIGURAÇÃO DE WEBHOOKS - INSTAGRAM
====================================

📋 Configurações:
   Page ID: 859614930562831
   Token: EAAPXQG5u0qkBPy2UoH...

====================================
ETAPA 1: Obter Instagram Account ID
====================================
📡 Buscando Instagram Business Account ID...
✅ Instagram Account ID: 17841477883364829

====================================
ETAPA 2: Subscrever Eventos
====================================
📡 Subscrevendo eventos: messages, comments, mentions...
✅ Subscrição criada com sucesso!

====================================
ETAPA 3: Verificar Subscrições
====================================
📡 Verificando subscrições ativas...
✅ Eventos subscritos: messages, comments, mentions, messaging_postbacks, messaging_handover, message_reactions, messaging_seen

====================================
✅ CONFIGURAÇÃO CONCLUÍDA!
====================================
```

---

## 🧪 TESTAR WEBHOOK

### Teste 1: Enviar Mensagem DM

1. Abrir Instagram
2. Enviar DM para **@lfimoveismg**
3. Mensagem: "Teste webhook"

### Teste 2: Ver Logs na VPS

```bash
ssh root@82.25.68.132
docker service logs instagram-webhook_app -f
```

**Logs esperados:**
```
📨 Webhook recebido: instagram
🔄 Processando entry 17841477883364829
💬 Mensagem de 123456: Teste webhook
```

### Teste 3: Comentar em Post

1. Comentar em qualquer post de @lfimoveismg
2. Ver logs (mesmo comando acima)

**Logs esperados:**
```
💬 Comentário de @seu_usuario: Teste
```

---

## ❌ Troubleshooting

### Webhook não valida

**Problema:** Meta Dashboard retorna erro ao validar URL

**Solução:**
```bash
# Ver logs em tempo real
ssh root@82.25.68.132
docker service logs instagram-webhook_app -f

# Enviar request de teste
curl "https://instagram-webhook.loop9.com.br/webhook?hub.mode=subscribe&hub.verify_token=meu_token_secreto_123&hub.challenge=teste123"

# Deve retornar: teste123
```

### Container não inicia

**Problema:** `docker service ls` mostra 0/1 réplicas

**Solução:**
```bash
# Ver erro
docker service ps instagram-webhook_app --no-trunc

# Rebuild
docker service update --force instagram-webhook_app
```

### SSL não funciona

**Problema:** HTTPS retorna erro de certificado

**Solução:**
```bash
# Aguardar 1-2 minutos para Traefik gerar certificado
# Ver logs do Traefik
docker service logs traefik_traefik -f | grep instagram
```

### Eventos não chegam

**Problema:** Webhook valida, mas eventos não aparecem nos logs

**Solução:**
1. Verificar subscrição: `python3 subscribe_events.py`
2. Verificar permissões do app no Meta Dashboard
3. Testar com mensagem real (não teste via Dashboard)

---

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
ssh root@82.25.68.132
docker service logs instagram-webhook_app -f
```

### Ver Status do Serviço

```bash
docker service ls | grep instagram
docker service ps instagram-webhook_app
```

### Reiniciar Serviço

```bash
docker service update --force instagram-webhook_app
```

### Remover Serviço

```bash
docker stack rm instagram-webhook
```

---

## 🔄 Atualizar Código

### Quando modificar app.py ou qualquer arquivo:

```bash
# LOCAL: Commit e push
cd /Users/felipemdepaula/Desktop/ClaudeCode-Workspace/SWARM/automations/instagram-webhook
git add .
git commit -m "feat: adicionar nova funcionalidade"
git push origin main

# VPS: Pull e re-deploy
ssh root@82.25.68.132
cd /opt/swarm/automations/instagram-webhook
git pull origin main
docker stack deploy -c docker-compose.yml instagram-webhook
```

---

## 📋 Checklist Final

- [ ] Código desenvolvido ✅
- [ ] Repositório no GitHub ✅
- [ ] Credenciais configuradas ✅
- [ ] Deploy na VPS
- [ ] Webhook validado no Meta Dashboard
- [ ] Eventos subscritos via API
- [ ] Teste com mensagem real
- [ ] Logs funcionando

---

## 🆘 Precisa de Ajuda?

1. Ver logs: `docker service logs instagram-webhook_app -f`
2. Verificar documentação: `README.md`
3. Consultar docs oficiais: [DOCS-API/instagram-webhooks/](../../../DOCS-API/instagram-webhooks/)

---

**Última atualização:** 2025-11-06
**URL:** https://instagram-webhook.loop9.com.br
**GitHub:** https://github.com/dipaulavs/instagram-webhook
