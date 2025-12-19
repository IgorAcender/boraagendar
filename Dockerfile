FROM node:18-alpine AS tailwind_builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY tailwind.config.js postcss.config.js ./
COPY src/static/css/tailwind-input.css ./src/static/css/

# Copiar templates para Tailwind escanear (content)
COPY src/templates ./src/templates

RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY ./src /app/src

# Copiar CSS compilado para o lugar certo (depois de copiar src/)
COPY --from=tailwind_builder /app/src/static/css/tailwind.css /app/src/static/css/tailwind.css

COPY ./entrypoint.sh /app/src/
RUN chmod +x /app/src/entrypoint.sh

# Expõe a porta utilizada pelo gunicorn
EXPOSE 8000

ENTRYPOINT ["/app/src/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
