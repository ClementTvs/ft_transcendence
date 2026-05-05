FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/static

# Generate a self-signed TLS certificate for HTTPS
RUN apk add --no-cache openssl && \
    mkdir -p /app/certs && \
    openssl req -x509 -nodes \
        -out /app/certs/server.crt \
        -keyout /app/certs/server.key \
        -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=localhost"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--ssl-keyfile", "/app/certs/server.key", "--ssl-certfile", "/app/certs/server.crt"]