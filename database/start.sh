#!/bin/bash

echo "🚀 Iniciando serviço de backup automatizado..."

# Criar diretório de logs se não existir
mkdir -p /var/log

# Verificar se o crontab foi instalado
if crontab -l > /dev/null 2>&1; then
    echo "✅ Crontab instalado com sucesso"
    echo "📅 Agendamentos ativos:"
    crontab -l
else
    echo "❌ Erro ao instalar crontab"
    exit 1
fi

# Verificar conectividade com o banco de dados
echo "🔍 Verificando conectividade com o banco de dados..."
if [ -n "$POSTGRES_HOST" ] && [ -n "$POSTGRES_DB" ]; then
    echo "   Host: $POSTGRES_HOST"
    echo "   Database: $POSTGRES_DB"
    echo "   User: $POSTGRES_USER"
else
    echo "⚠️  Variáveis de ambiente do banco não definidas"
fi

# Iniciar o cron em foreground
echo "⏰ Iniciando cron daemon..."
echo "📝 Logs serão salvos em /var/log/backup.log"
echo "🔄 Próximo backup agendado para 3:00 da manhã"

# Executar cron em foreground para manter o container ativo
exec cron -f
