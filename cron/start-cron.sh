#!/bin/bash

# Iniciar cron daemon
service cron start

# Criar diretório de logs se não existir
mkdir -p /var/log

# Executar o comando de processamento de notificações repetitivas a cada hora
echo "0 * * * * cd /app && /usr/local/bin/python3 manage.py process_repeat_notifications >> /var/log/cron.log 2>&1" | crontab -

# Verificar se o cron foi configurado corretamente
echo "Cron configurado com sucesso:"
crontab -l

# Manter o container rodando
tail -f /dev/null
