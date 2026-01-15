FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    cron \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /var/log /backups

# Copiar scripts de inicialização e wrappers
COPY cron/start-cron.sh /start-cron.sh
COPY cron/run-notifications.sh /app/cron/run-notifications.sh
COPY cron/run-backup.sh /app/cron/run-backup.sh
RUN chmod +x /start-cron.sh /app/cron/run-notifications.sh /app/cron/run-backup.sh

# Comando de inicialização
CMD ["/start-cron.sh"]