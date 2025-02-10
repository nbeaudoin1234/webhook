# Capteur de notifications ("Webhooks")

Cette application permet de capter les notifications ("webhooks") venant d'une application tierce sur un port spécifique.  Elle est développée avec Flask et conteneurisée avec Docker.

## Prérequis

- Docker
- Docker Compose

## Configuration

Par défaut, le capteur écoute le port 8020.  Cette valeur peut être modifiée dans le fichier '.env'

### `.env`

WEBHOOK_PORT=8020




## Installation et démarrage

1. git clone https://github.com/xxxxxx/webhook.git

2. A partir du dossier "webhook", construire l'image (lors de la première exécution)
    docker compose build

3. Lancez le service 
    docker compose up

Le webhook sera accessible à l'adresse : `http://localhost:8020`

## Sécurité

- Le conteneur s'exécute avec un utilisateur non-root (flaskuser)
- Les dépendances sont maintenues à jour via requirements.txt

## Maintenance

Pour mettre à jour les dépendances :
1. Modifiez le fichier `requirements.txt`
2. Reconstruisez l'image : `docker compose build`