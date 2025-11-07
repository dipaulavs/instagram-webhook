# 📊 Progresso: Instagram Webhook - 06/11/2025

## ✅ O QUE FOI FEITO

### 1. Servidor Flask Completo
- ✅ Código Python implementado ([app.py](app.py))
- ✅ Validação GET (verify token)
- ✅ Processamento POST (webhooks)
- ✅ Handlers para todos eventos: messages, comments, mentions, reactions, etc
- ✅ Validação de signature (segurança)
- ✅ Logs com timestamp

### 2. Deploy Automatizado
- ✅ Docker Swarm configurado
- ✅ Dockerfile com healthcheck
- ✅ docker-compose.yml com Traefik
- ✅ Repositório GitHub: https://github.com/dipaulavs/instagram-webhook
- ✅ Deploy via Git (GitHub-First)

### 3. Infraestrutura VPS
- ✅ Container rodando (1/1 réplicas)
- ✅ Servidor respondendo na porta 8080
- ✅ Integrado na rede loop9Net
- ✅ Sem conflito com N8N/Evolution/Chatwoot

### 4. Credenciais Configuradas
- ✅ Page Access Token
- ✅ Page ID: 859614930562831
- ✅ Business Account ID: 17841477883364829
- ✅ Verify Token: meu_token_secreto_123

### 5. Documentação
- ✅ [README.md](README.md) - Guia de uso
- ✅ [GUIA-DEPLOY.md](GUIA-DEPLOY.md) - Passo a passo deploy
- ✅ [DEPLOY.sh](DEPLOY.sh) - Script automático
- ✅ [subscribe_events.py](subscribe_events.py) - Script subscrição API
- ✅ [DOCS-API/instagram-webhooks/](../../../DOCS-API/instagram-webhooks/) - Docs completa da API

---

## ⚠️ PROBLEMA ATUAL

### SSL não está sendo gerado pelo Traefik

**Situação:**
- Container ativo e funcionando
- URL: https://instagram-webhook.loop9.com.br
- Responde corretamente (testado com `-k`)
- **MAS:** Certificado SSL é "TRAEFIK DEFAULT CERT" (self-signed)
- **Esperado:** Let's Encrypt certificate

**Verificação:**
```bash
# SSL atual (incorreto)
echo | openssl s_client -servername instagram-webhook.loop9.com.br -connect instagram-webhook.loop9.com.br:443 2>&1 | grep "subject="
# Output: subject=CN=TRAEFIK DEFAULT CERT

# Comparação com N8N (correto)
echo | openssl s_client -servername n8n.loop9.com.br -connect n8n.loop9.com.br:443 2>&1 | grep "issuer="
# Output: issuer=C=US, O=Let's Encrypt, CN=R13
```

**Possíveis causas:**
1. Let's Encrypt rate limit para loop9.com.br
2. Traefik não conseguiu validar domínio
3. Configuração das labels incorreta (improvável - estão corretas)
4. Tempo insuficiente (já passou 20+ minutos)

**Labels configuradas (corretas):**
```yaml
traefik.http.routers.instagram-webhook.tls.certresolver=letsencrypt
traefik.http.routers.instagram-webhook.rule=Host(`instagram-webhook.loop9.com.br`)
```

---

## 🎯 PRÓXIMO PASSO: USAR N8N (SOLUÇÃO RÁPIDA)

### Por que N8N?
- ✅ SSL Let's Encrypt já funcionando
- ✅ Mais rápido (não precisa esperar certificado)
- ✅ Interface visual para workflows
- ✅ Mesma infraestrutura (loop9Net)
- ✅ Pode processar e chamar outros serviços

### Configuração no Meta Dashboard

**Trocar:**
- ❌ URL antiga: `https://instagram-webhook.loop9.com.br/webhook`
- ✅ URL nova: `https://n8n.loop9.com.br/webhook/instagram-webhook`
- ✅ Verify Token: `meu_token_secreto_123` (mesmo)

---

## 📋 WORKFLOW N8N - Instagram Webhook

### Nodes necessários:

#### 1. Webhook Node
```
Name: Instagram Webhook
HTTP Method: GET, POST
Path: instagram-webhook
Authentication: None
Respond: Immediately
Response Mode: Using 'Respond to Webhook' Node
```

#### 2. IF Node (Verificar método)
```
Condition 1: {{ $node["Instagram Webhook"].json["method"] }} equals GET
Condition 2: {{ $node["Instagram Webhook"].json["method"] }} equals POST
```

#### 3. Function Node (Validação GET)
```javascript
// Validar webhook do Instagram
const mode = $node["Instagram Webhook"].json.query['hub.mode'];
const token = $node["Instagram Webhook"].json.query['hub.verify_token'];
const challenge = $node["Instagram Webhook"].json.query['hub.challenge'];

if (mode === 'subscribe' && token === 'meu_token_secreto_123') {
  // Retornar challenge para Instagram
  return [{
    json: {
      challenge: challenge
    }
  }];
} else {
  return [{
    json: {
      error: 'Token inválido'
    }
  }];
}
```

#### 4. Respond to Webhook Node (após Function)
```
Respond With: Text
Response Body: {{ $json.challenge }}
```

#### 5. Function Node (Processar POST - eventos)
```javascript
// Processar evento do Instagram
const data = $node["Instagram Webhook"].json.body;

if (data.object === 'instagram') {
  const events = [];

  for (const entry of data.entry || []) {
    // Processar mensagens
    if (entry.messaging) {
      for (const msg of entry.messaging) {
        if (msg.message) {
          events.push({
            type: 'message',
            sender_id: msg.sender.id,
            text: msg.message.text || '',
            timestamp: msg.timestamp
          });
        }
      }
    }

    // Processar comentários
    if (entry.changes) {
      for (const change of entry.changes) {
        if (change.field === 'comments') {
          events.push({
            type: 'comment',
            comment_id: change.value.id,
            text: change.value.text,
            username: change.value.from.username
          });
        }
      }
    }
  }

  return events.map(e => ({ json: e }));
}

return [];
```

#### 6. Respond to Webhook Node (após processar)
```
Respond With: Text
Response Body: OK
```

#### 7. Switch Node (Tipo de evento)
```
Route 0: {{ $json.type }} equals message
Route 1: {{ $json.type }} equals comment
Route 2: {{ $json.type }} equals mention
```

#### 8. Processar Mensagem
```
- Salvar no banco
- Chamar IA para responder
- Enviar resposta via Graph API
- Notificar equipe
```

---

## 🔄 ALTERNATIVA: CORRIGIR SSL DO FLASK (TEMPO INDETERMINADO)

### Opções para corrigir:

#### Opção A: Aguardar (não recomendado)
- Aguardar 24-48h para Let's Encrypt resetar rate limit
- Não garantido que vai funcionar

#### Opção B: Usar outro subdomínio
```bash
# Trocar para: webhook-ig.loop9.com.br
# Editar docker-compose.yml
# Re-deploy
```

#### Opção C: Investigar logs Traefik
```bash
ssh root@82.25.68.132
docker service logs traefik_traefik -f | grep -i "instagram\|acme\|certificate"
```

#### Opção D: Remover certificado default e forçar novo
```bash
# Requer acesso ao volume do Traefik
# Risco de quebrar outros certificados
# NÃO RECOMENDADO
```

---

## ✅ RECOMENDAÇÃO FINAL

### USAR N8N (Solução em 5 minutos)

**Vantagens:**
- ✅ SSL funcionando
- ✅ Validação imediata
- ✅ Workflows visuais
- ✅ Fácil debug
- ✅ Pode chamar Flask depois se quiser

**Fluxo recomendado:**
```
Instagram → N8N (webhook) → Processar → Flask (opcional) → Responder
```

**Tempo estimado:** 5-10 minutos para configurar tudo

---

## 📂 Estrutura de Arquivos

```
SWARM/automations/instagram-webhook/
├── app.py                    # Servidor Flask completo ✅
├── subscribe_events.py       # Script subscrição API ✅
├── requirements.txt          # Dependências ✅
├── .env                      # Credenciais configuradas ✅
├── .env.example             # Template ✅
├── Dockerfile               # Build (healthcheck corrigido) ✅
├── docker-compose.yml       # Swarm + Traefik ✅
├── README.md                # Documentação ✅
├── GUIA-DEPLOY.md           # Guia passo a passo ✅
├── DEPLOY.sh                # Script automático ✅
└── PROGRESSO.md             # Este arquivo ✅
```

**GitHub:** https://github.com/dipaulavs/instagram-webhook

---

## 🎬 PRÓXIMAS AÇÕES

### Imediatas (usar N8N):
1. [ ] Criar workflow no N8N com nodes acima
2. [ ] Testar validação: `https://n8n.loop9.com.br/webhook/instagram-webhook?hub.mode=subscribe&hub.verify_token=meu_token_secreto_123&hub.challenge=teste`
3. [ ] Configurar URL no Meta Dashboard
4. [ ] Validar e salvar
5. [ ] Subscrever eventos: `python3 subscribe_events.py`
6. [ ] Testar com mensagem DM real

### Futuras (opcional):
- [ ] Investigar por que Traefik não gerou SSL
- [ ] Manter Flask como backup/fallback
- [ ] Integrar N8N → Flask para processamento Python
- [ ] Adicionar IA para respostas automáticas
- [ ] Dashboard de métricas

---

**Última atualização:** 06/11/2025 23:45
**Status:** Container funcionando, SSL pendente, solução N8N pronta
**Próximo:** Configurar workflow N8N (5 min)
