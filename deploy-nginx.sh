#!/bin/bash

# Script de deploy otimizado para Nginx - Nations Flow
# Aplica otimizações de performance e reinicia os serviços

set -e

echo "=== Deploy Nginx Otimizado - Nations Flow ==="
echo "Data: $(date)"
echo

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Parar serviços
echo "1. Parando serviços..."
docker compose down
echo

# Limpar containers antigos
echo "2. Limpando containers antigos..."
docker system prune -f
echo

# Rebuild da imagem Nginx
echo "3. Rebuild da imagem Nginx..."
docker compose build nginx
echo

# Coletar arquivos estáticos
echo "4. Coletando arquivos estáticos..."
docker compose run --rm web python manage.py collectstatic --noinput
echo

# Iniciar serviços
echo "5. Iniciando serviços..."
docker compose up -d
echo

# Aguardar serviços ficarem prontos
echo "6. Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status
echo "7. Verificando status dos serviços..."
docker compose ps
echo

# Verificar health checks
echo "8. Verificando health checks..."
echo "   - Nginx:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost/health || echo "   Falhou"
echo "   - Django:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/health/ || echo "   Falhou"
echo

# Verificar logs
echo "9. Verificando logs iniciais..."
echo "   - Nginx (últimas 5 linhas):"
docker logs nations-flow_nginx --tail 5
echo

# Executar monitoramento
echo "10. Executando monitoramento..."
if [ -f "nginx/monitor.sh" ]; then
    ./nginx/monitor.sh
else
    echo "   Script de monitoramento não encontrado"
fi

echo
echo "=== Deploy Concluído ==="
echo "Para monitorar continuamente, execute: ./nginx/monitor.sh"
echo "Para ver logs em tempo real: docker-compose logs -f nginx"
