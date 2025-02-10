# Webhook Flask

Un service webhook développé avec Flask, conteneurisé avec Docker.

## Prérequis

- Docker
- Docker Compose

## Configuration

### Structure des fichiers

Le projet nécessite les fichiers suivants :

### `.env`

WEBHOOK_PORT=8020


### `docker-compose.yml`

services:
flask_app:
container_name: emetteur_notifs
build: .
env_file:
- .env
ports:
- "${WEBHOOK_PORT}:${WEBHOOK_PORT}"
volumes:
- .:/app  # reload dynamique
environment:
- FLASK_ENV=development  # permet auto-reload pour Flask
- FLASK_APP=app.py
- WEBHOOK_PORT=${WEBHOOK_PORT}
command: flask --debug run --host=0.0.0.0 --port=${WEBHOOK_PORT}


### `Dockerfile`

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

COPY . /app
Exposer port pour Flask
EXPOSE ${WEBHOOK_PORT}
Usager non-root (pour raisons de securite)
RUN useradd -m flaskuser
USER flaskuser
# Demarrage Flask
CMD flask --debug run --host=0.0.0.0 --port=$WEBHOOK_PORT


## Installation et démarrage

1. Créez les fichiers ci-dessus dans un nouveau dossier `webhook`

2. Construisez l'image Docker :

docker compose build


3. Lancez le service :

docker compose up


Le webhook sera accessible à l'adresse : `http://localhost:8020`

## Développement

Le code est monté en volume dans le conteneur, ce qui permet le rechargement automatique des modifications en développement.

## Sécurité

- Le conteneur s'exécute avec un utilisateur non-root (flaskuser)
- Les dépendances sont maintenues à jour via requirements.txt

## Maintenance

Pour mettre à jour les dépendances :
1. Modifiez le fichier `requirements.txt`
2. Reconstruisez l'image : `docker compose build`