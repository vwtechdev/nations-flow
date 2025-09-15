#!/bin/bash

# Iniciar cron daemon
service cron start

# Executar o comando de processamento de notificações repetitivas a cada minuto
echo "* * * * * cd /app && /usr/local/bin/python3 manage.py process_repeat_notifications >> /var/log/cron.log 2>&1" | crontab -

# Manter o container rodando
tail -f /dev/null
