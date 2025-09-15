# Configuração Nginx Otimizada - Nations Flow

Este diretório contém a configuração otimizada do Nginx para servir arquivos estáticos e de mídia com alta performance e escalabilidade.

## 🚀 Otimizações Implementadas

### Performance
- **Worker processes**: Configurado para usar todos os cores disponíveis
- **Worker connections**: Aumentado para 4096 conexões simultâneas
- **Keep-alive**: Otimizado para 1000 requisições por conexão
- **Gzip compression**: Habilitado com nível 6 para melhor compressão
- **Sendfile**: Habilitado para transferência eficiente de arquivos
- **TCP optimizations**: tcp_nopush e tcp_nodelay habilitados

### Cache e Headers
- **Static files**: Cache de 1 ano com headers `immutable`
- **Media files**: Cache de 30 dias
- **Vary headers**: Configurados para compressão
- **Security headers**: X-Frame-Options, X-Content-Type-Options, etc.

### Rate Limiting
- **API requests**: 10 requisições por segundo
- **Static files**: 50 requisições por segundo
- **Connection limiting**: 10 conexões por IP

### Logs Estruturados
- **Access logs**: Separados por tipo (api, static, media)
- **Error logs**: Configurados com nível notice
- **Log rotation**: Configurado para produção

## 📁 Estrutura de Arquivos

```
nginx/
├── Dockerfile              # Imagem Nginx otimizada
├── nginx.conf              # Configuração principal
├── nginx-production.conf   # Configurações adicionais para produção
├── monitor.sh              # Script de monitoramento
└── README.md               # Esta documentação
```

## 🔧 Como Usar

### Deploy
```bash
# Aplicar otimizações e reiniciar
./deploy-nginx.sh

# Monitorar performance
./nginx/monitor.sh
```

### Verificar Status
```bash
# Status dos containers
docker-compose ps

# Logs do Nginx
docker-compose logs -f nginx

# Health check
curl http://localhost/health
```

## 📊 Monitoramento

O script `monitor.sh` verifica:
- Status dos containers
- Logs de erro
- Métricas de performance
- Uso de recursos
- Health checks
- Arquivos estáticos e de mídia

## 🛡️ Segurança

- Rate limiting configurado
- Headers de segurança
- Logs de acesso separados
- Configurações de proxy otimizadas
- Timeouts configurados

## 📈 Escalabilidade

- Configurações de recursos no docker-compose
- Health checks configurados
- Logs persistentes com volumes
- Configurações otimizadas para alta carga

## 🔍 Troubleshooting

### Problemas Comuns

1. **Arquivos estáticos não carregam**
   ```bash
   # Verificar permissões
   docker exec nations-flow_nginx ls -la /app/static/
   
   # Recoletar arquivos estáticos
   docker-compose run --rm web python manage.py collectstatic --noinput
   ```

2. **Rate limiting muito restritivo**
   ```bash
   # Ajustar no nginx.conf
   limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
   ```

3. **Logs não aparecem**
   ```bash
   # Verificar volumes
   docker volume ls | grep nginx_logs
   
   # Verificar permissões
   docker exec nations-flow_nginx ls -la /var/log/nginx/
   ```

## 📝 Configurações Avançadas

### Para Produção
- Incluir `nginx-production.conf` no `nginx.conf`
- Ajustar rate limits conforme necessário
- Configurar log rotation
- Monitorar métricas de performance

### Para Desenvolvimento
- Reduzir rate limits
- Habilitar logs mais verbosos
- Desabilitar cache agressivo

## 🔄 Atualizações

Para aplicar novas otimizações:
1. Editar `nginx.conf`
2. Executar `./deploy-nginx.sh`
3. Verificar com `./nginx/monitor.sh`
4. Monitorar logs por alguns minutos
