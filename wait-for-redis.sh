#!/bin/bash

# Script para aguardar o Redis estar disponível
# Uso: ./wait-for-redis.sh [host] [port] [timeout]

REDIS_HOST=${1:-redis}
REDIS_PORT=${2:-6379}
TIMEOUT=${3:-30}

echo "Aguardando Redis em $REDIS_HOST:$REDIS_PORT..."

# Função para testar conexão Redis usando netcat
test_redis() {
    nc -z $REDIS_HOST $REDIS_PORT > /dev/null 2>&1
    return $?
}

# Contador de tentativas
count=0
max_attempts=$((TIMEOUT * 2))  # 2 tentativas por segundo

while [ $count -lt $max_attempts ]; do
    if test_redis; then
        echo "Redis está disponível!"
        exit 0
    fi
    
    count=$((count + 1))
    sleep 0.5
done

echo "Timeout: Redis não ficou disponível em $TIMEOUT segundos"
exit 1
