# Image python minimale
FROM python:3.12-slim-bullseye

# Dossier de travail a l'interieur du conteneur
WORKDIR /app

# Installation de curl a l'interieur du conteneur
RUN apt-get update && apt-get install -y curl

# Requirements
COPY requirements.txt /app/

# Dependences Python
RUN pip install --no-cache-dir -r requirements.txt

# 
COPY . /app

# Exposer port pour webhook
EXPOSE ${WEBHOOK_PORT}

# Usager non-root (pour raisons de securite)
RUN useradd -m webhookuser
USER webhookuser

# Demarrage du serveur webhook
CMD python app.py
