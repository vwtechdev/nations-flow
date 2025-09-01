#!/bin/bash
# wait-for-database.sh

set -e

# Configurações do banco a partir do .env
POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "Aguardando o banco de dados em $POSTGRES_HOST:$POSTGRES_PORT..."

# Espera até o banco responder na porta
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "Banco de dados pronto, iniciando o Django..."

# Executa o comando passado como argumento (por exemplo gunicorn)
exec "$@"