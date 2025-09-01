FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Diretório do app
WORKDIR /app

# Copia requirements e instala
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . /app

# Cria pasta para arquivos estáticos
RUN mkdir -p /app/static /app/media
