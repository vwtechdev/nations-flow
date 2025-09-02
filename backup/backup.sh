#!/bin/bash
set -e

# Configurações do banco (vindas do .env do projeto)
DB_NAME="${POSTGRES_DB}"
DB_USER="${POSTGRES_USER}"
DB_PASS="${POSTGRES_PASSWORD}"
DB_HOST="db"

# Pasta onde o dump ficará antes de ir pro Google Drive
LOCAL_PATH="/backups"
FILENAME="backup_$(date +%Y%m%d_%H%M%S).sql.gz"

export PGPASSWORD=$DB_PASS

echo "Iniciando backup do banco ${DB_NAME}..."
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > ${LOCAL_PATH}/${FILENAME}

echo "Enviando backup para Google Drive..."
rclone copy ${LOCAL_PATH}/${FILENAME} gdrive:/Backups/nationsflow/ --progress

echo "Backup concluído com sucesso: ${FILENAME}"