#!/bin/bash
set -e

# Carregar variáveis de ambiente do arquivo criado pelo start-cron.sh
if [ -f /etc/cron.env ]; then
    # Usar source de forma segura
    set -a
    . /etc/cron.env
    set +a
fi

# Garantir variáveis essenciais
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-core.settings}
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Executar comando
cd /app
exec python3 manage.py backup_postgres
