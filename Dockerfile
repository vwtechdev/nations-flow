FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Diretório do app
WORKDIR /app

# Dependências
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia o código
COPY . /app/

# Coleta estáticos (pode rodar durante build ou no entrypoint)
RUN python manage.py collectstatic --noinput

# Expõe a porta
EXPOSE 8000

# Comando padrão
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]