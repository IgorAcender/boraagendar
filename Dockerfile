FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Instalar dependências do sistema + Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# ⭐ Build Frontend React
COPY ./frontend /app/frontend
WORKDIR /app/frontend
RUN npm install && npm run build
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY ./src /app

# Copia o build do React para Django static (se não tiver sido copiado)
RUN mkdir -p /app/static/dist && \
    if [ -d /app/frontend/dist ]; then cp -r /app/frontend/dist/* /app/static/dist/; fi

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expõe a porta utilizada pelo gunicorn
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
