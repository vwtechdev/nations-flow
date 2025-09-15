FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
    
# Criar diretório de trabalho
WORKDIR /app

# Copiar scripts
COPY backup_script.sh /app/
COPY backup_wrapper.sh /app/
COPY crontab /app/

# Dar permissões de execução
RUN chmod +x /app/backup_script.sh
RUN chmod +x /app/backup_wrapper.sh

# Criar diretório para backups
RUN mkdir -p /app/backups

# Instalar crontab
RUN crontab /app/crontab

# Script de inicialização
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Comando padrão
CMD ["/app/start.sh"]
