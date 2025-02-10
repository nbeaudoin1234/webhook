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

# Exposer port pour Flask
EXPOSE ${WEBHOOK_PORT}

# Usager non-root (pour raisons de securite)
RUN useradd -m flaskuser
USER flaskuser

# Demarrage Flask
CMD flask --debug run --host=0.0.0.0 --port=$WEBHOOK_PORT
