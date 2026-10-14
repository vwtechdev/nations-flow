#!/bin/bash
set -euo pipefail

# Carregar variáveis de ambiente do arquivo criado pelo start-cron.sh
if [ -f /etc/cron.env ]; then
    # Usar source de forma segura
    set -a
    . /etc/cron.env
    set +a
fi

export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Backup PostgreSQL via pg_dump direto (sem boot do Django).
# O manage.py backup_postgres importava o Django inteiro (~100M RSS) só para
# chamar o pg_dump, e o OOM-killer matava o processo no host sem RAM livre
# (backup.log terminava em "Killed" sem nenhuma linha). Versão shell usa ~5M.
# Destinos mantidos: /backups -> $HOME/data/<projeto>/backups,
# stdout -> /var/log/backup.log -> $HOME/logs/<projeto>/cron/.

BACKUP_DIR="/backups"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-10}"
DB_HOST="${POSTGRES_HOST:-db}"
DB_NAME="${POSTGRES_DB:?POSTGRES_DB ausente}"
DB_USER="${POSTGRES_USER:?POSTGRES_USER ausente}"
export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD ausente}"

mkdir -p "$BACKUP_DIR"

# 1. Limpar backups antigos (mesmo glob do backup_postgres.py)
find "$BACKUP_DIR" -maxdepth 1 -name 'backup_*.sql.gz' -mtime +"$RETENTION_DAYS" -print -delete

# 2. Novo backup (timestamp igual ao .py: %d_%m_%Y_%H_%M; TZ=America/Sao_Paulo vem do compose)
TIMESTAMP="$(date '+%d_%m_%Y_%H_%M')"
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz"

pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "✅ Backup criado com sucesso: $BACKUP_FILE"
