#!/bin/bash

# Configurações do banco de dados (usando variáveis de ambiente do container)
POSTGRES_HOST=${POSTGRES_HOST:-db}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Diretório de backup
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%d_%m_%Y_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Verificar se as variáveis de ambiente estão definidas
if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ Erro: Variáveis de ambiente do banco de dados não definidas"
    echo "   POSTGRES_DB, POSTGRES_USER e POSTGRES_PASSWORD são obrigatórias"
    exit 1
fi

# Backup será apenas local (sem Google Drive)
echo "ℹ️  Modo: Backup local apenas"
echo "🔄 Iniciando backup do banco de dados..."
echo "   Host: $POSTGRES_HOST:$POSTGRES_PORT"
echo "   Database: $POSTGRES_DB"
echo "   User: $POSTGRES_USER"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Executar pg_dump
echo "📦 Executando pg_dump..."
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --verbose \
    --no-password \
    --format=plain \
    --file="$BACKUP_FILE"

# Verificar se o backup foi criado com sucesso
if [ $? -eq 0 ] && [ -f "$BACKUP_FILE" ]; then
    echo "✅ Backup criado com sucesso: $BACKUP_FILE"
    echo "📊 Tamanho do arquivo: $(du -h "$BACKUP_FILE" | cut -f1)"
    echo "📁 Localização: $BACKUP_FILE"
    echo "💾 Backup salvo localmente (sem upload para nuvem)"
    
    # Limpar backups antigos - manter apenas os 10 mais recentes
    echo "🧹 Limpando backups antigos (mantendo apenas 10 mais recentes)..."
    cd "$BACKUP_DIR"
    
    # Contar arquivos de backup
    BACKUP_COUNT=$(ls -1 db_backup_*.sql 2>/dev/null | wc -l)
    
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        # Ordenar por data de modificação (mais antigos primeiro) e remover os excedentes
        ls -1t db_backup_*.sql | tail -n +11 | while read -r old_backup; do
            echo "🗑️  Removendo backup antigo: $old_backup"
            rm -f "$old_backup"
        done
        
        REMAINING_COUNT=$(ls -1 db_backup_*.sql 2>/dev/null | wc -l)
        echo "📊 Backups restantes: $REMAINING_COUNT"
    else
        echo "📊 Total de backups: $BACKUP_COUNT (dentro do limite de 10)"
    fi
    
else
    echo "❌ Erro ao criar backup do banco de dados"
    exit 1
fi

echo "🎉 Processo de backup concluído com sucesso!"
