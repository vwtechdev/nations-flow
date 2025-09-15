#!/bin/bash

# Script de monitoramento do Nginx para Nations Flow
# Verifica performance, logs e status dos containers

echo "=== Monitoramento Nginx - Nations Flow ==="
echo "Data: $(date)"
echo

# Verificar status dos containers
echo "1. Status dos Containers:"
docker ps --filter "name=nations-flow" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# Verificar logs de erro do Nginx
echo "2. Logs de Erro do Nginx (últimas 10 linhas):"
docker logs nations-flow_nginx --tail 10 2>&1 | grep -i error || echo "Nenhum erro encontrado"
echo

# Verificar métricas de performance
echo "3. Métricas de Performance:"
echo "   - Conexões ativas:"
docker exec nations-flow_nginx nginx -T 2>/dev/null | grep -o "worker_connections [0-9]*" || echo "   Não disponível"
echo

# Verificar uso de memória
echo "4. Uso de Recursos:"
docker stats nations-flow_nginx --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

# Verificar arquivos de log
echo "5. Tamanho dos Logs:"
docker exec nations-flow_nginx sh -c "ls -lh /var/log/nginx/*.log 2>/dev/null | awk '{print \$5, \$9}'" || echo "Logs não encontrados"
echo

# Verificar health check
echo "6. Health Check:"
curl -s -o /dev/null -w "Status: %{http_code}, Tempo: %{time_total}s\n" http://localhost/health 2>/dev/null || echo "Health check falhou"
echo

# Verificar arquivos estáticos
echo "7. Verificação de Arquivos Estáticos:"
echo "   - Arquivos em /static:"
docker exec nations-flow_nginx sh -c "find /app/static -type f | wc -l" 2>/dev/null || echo "   Não disponível"
echo "   - Arquivos em /media:"
docker exec nations-flow_nginx sh -c "find /app/media -type f | wc -l" 2>/dev/null || echo "   Não disponível"
echo

echo "=== Fim do Monitoramento ==="
