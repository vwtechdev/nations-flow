#!/bin/bash

# Script wrapper para backup que carrega variáveis de ambiente de forma segura
# Este script é executado pelo cron e carrega as variáveis de ambiente do container

# Carregar variáveis de ambiente do processo pai (Docker Compose)
# O Docker Compose injeta essas variáveis no container via env_file
export POSTGRES_HOST=${POSTGRES_HOST:-db}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_DB=${POSTGRES_DB}
export POSTGRES_USER=${POSTGRES_USER}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Verificar se as variáveis essenciais estão definidas
if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ Erro: Variáveis de ambiente do banco de dados não definidas" >> /var/log/backup.log
    echo "   POSTGRES_DB, POSTGRES_USER e POSTGRES_PASSWORD são obrigatórias" >> /var/log/backup.log
    exit 1
fi

# Executar o script de backup
exec /app/backup_script.sh
