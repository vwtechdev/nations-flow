#!/bin/bash
set -e

echo "🚀 Iniciando cron..."

# Criar diretórios de log se não existirem
mkdir -p /var/log
touch /var/log/cron.log /var/log/backup.log
chmod 666 /var/log/cron.log /var/log/backup.log

# Salvar variáveis de ambiente essenciais em arquivo para uso pelos scripts do cron
# O cron não herda variáveis de ambiente automaticamente
# Salvar apenas variáveis essenciais de forma segura
> /etc/cron.env
echo "PATH=/usr/local/bin:/usr/bin:/bin" >> /etc/cron.env

# Lista de variáveis essenciais para o Django e PostgreSQL
ESSENTIAL_VARS="DJANGO_SETTINGS_MODULE POSTGRES_HOST POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD SECRET_KEY DEBUG ALLOWED_HOSTS REDIS_HOST REDIS_PORT REDIS_DB BACKUP_RETENTION_DAYS TZ"

for var in $ESSENTIAL_VARS; do
    if [ -n "${!var}" ]; then
        # Usar printf com %q para escapar caracteres especiais de forma segura
        printf 'export %s=%q\n' "$var" "${!var}" >> /etc/cron.env
    fi
done

# Copiar scripts wrapper para local acessível
cp /app/cron/run-notifications.sh /usr/local/bin/run-notifications.sh
cp /app/cron/run-backup.sh /usr/local/bin/run-backup.sh
chmod +x /usr/local/bin/run-notifications.sh
chmod +x /usr/local/bin/run-backup.sh

# Encontrar caminho do Python
PYTHON_PATH=$(which python3 || which python)
echo "📦 Python encontrado em: $PYTHON_PATH"

# Iniciar serviço cron
service cron start

# Criar arquivo temporário de cron
CRON_FILE=/tmp/crontab
> $CRON_FILE

# =========================
# Notificações – a cada hora
# =========================
echo "0 * * * * /usr/local/bin/run-notifications.sh >> /var/log/cron.log 2>&1" >> $CRON_FILE

# =========================
# Backup PostgreSQL – diário às 02:00
# =========================
echo "0 2 * * * /usr/local/bin/run-backup.sh >> /var/log/backup.log 2>&1" >> $CRON_FILE

# Instalar crontab
crontab $CRON_FILE

echo "✅ Crontab configurado:"
crontab -l

# Testar comandos manualmente para debug
echo ""
echo "🧪 Testando comandos..."
echo "Testando notificações..."
/usr/local/bin/run-notifications.sh >> /var/log/cron.log 2>&1 || echo "⚠️ Erro ao testar notificações (verifique logs)"

echo "Testando backup..."
/usr/local/bin/run-backup.sh >> /var/log/backup.log 2>&1 || echo "⚠️ Erro ao testar backup (verifique logs)"

echo ""
echo "📋 Logs disponíveis em:"
echo "  - /var/log/cron.log"
echo "  - /var/log/backup.log"
echo ""

# Manter container vivo + logs visíveis
tail -f /var/log/cron.log /var/log/backup.log
