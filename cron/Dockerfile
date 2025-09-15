FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    cron \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar e configurar script de inicialização
RUN echo '#!/bin/bash' > /app/start-cron.sh && \
    echo '' >> /app/start-cron.sh && \
    echo '# Iniciar cron daemon' >> /app/start-cron.sh && \
    echo 'service cron start' >> /app/start-cron.sh && \
    echo '' >> /app/start-cron.sh && \
    echo '# Executar o comando de processamento de notificações repetitivas a cada minuto' >> /app/start-cron.sh && \
    echo 'echo "* * * * * cd /app && /usr/local/bin/python3 manage.py process_repeat_notifications >> /var/log/cron.log 2>&1" | crontab -' >> /app/start-cron.sh && \
    echo '' >> /app/start-cron.sh && \
    echo '# Manter o container rodando' >> /app/start-cron.sh && \
    echo 'tail -f /dev/null' >> /app/start-cron.sh && \
    chmod +x /app/start-cron.sh

# Criar diretórios para logs
RUN mkdir -p /var/log /app/logs

# Comando de inicialização
CMD ["/bin/bash", "-c", "service cron start && echo '* * * * * cd /app && /usr/local/bin/python3 manage.py process_repeat_notifications >> /var/log/cron.log 2>&1' | crontab - && tail -f /dev/null"]
