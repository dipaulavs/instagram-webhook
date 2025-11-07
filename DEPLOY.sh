#!/bin/bash
# Script de deploy do Instagram Webhook na VPS

echo "===================================="
echo "🚀 DEPLOY INSTAGRAM WEBHOOK"
echo "===================================="

# Configurações
VPS_IP="82.25.68.132"
VPS_USER="root"
REPO_URL="https://github.com/dipaulavs/instagram-webhook.git"
DEPLOY_PATH="/opt/swarm/automations/instagram-webhook"

echo ""
echo "📡 Conectando na VPS..."
ssh $VPS_USER@$VPS_IP << 'ENDSSH'

echo "📁 Criando diretórios..."
mkdir -p /opt/swarm/automations
cd /opt/swarm/automations

echo "📥 Clonando repositório..."
if [ -d "instagram-webhook" ]; then
    echo "⚠️  Repositório já existe, atualizando..."
    cd instagram-webhook
    git pull origin main
else
    git clone https://github.com/dipaulavs/instagram-webhook.git
    cd instagram-webhook
fi

echo ""
echo "⚙️  CONFIGURAR .ENV"
echo "===================================="
echo "Abra outro terminal e execute:"
echo "ssh root@82.25.68.132"
echo "nano /opt/swarm/automations/instagram-webhook/.env"
echo ""
echo "Cole o conteúdo:"
cat << 'EOF'
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
EOF

echo ""
read -p "Pressione ENTER após configurar o .env..."

echo ""
echo "🐳 Fazendo deploy no Swarm..."
docker stack deploy -c docker-compose.yml instagram-webhook

echo ""
echo "⏳ Aguardando container iniciar..."
sleep 5

echo ""
echo "📊 Status do serviço:"
docker service ls | grep instagram

echo ""
echo "📝 Logs (últimas 20 linhas):"
docker service logs instagram-webhook_app --tail 20

echo ""
echo "===================================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "===================================="
echo ""
echo "🌐 URL: https://instagram-webhook.loop9.com.br"
echo ""
echo "📋 Próximos passos:"
echo "1. Configurar webhook no Meta Dashboard"
echo "2. Subscrever eventos via API (local)"
echo "3. Testar enviando mensagem DM"

ENDSSH

echo ""
echo "✅ Script concluído!"
