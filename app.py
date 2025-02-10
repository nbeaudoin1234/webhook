from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
import json
from datetime import datetime
from collections import deque
import logging
import sys
import os
from gevent import monkey
monkey.patch_all()

# Configuration du port webhook (défaut: 8020)
PORT_WEBHOOK = int(os.getenv('PORT_WEBHOOK', 8020))

# Création de l'application Flask avec SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins='*')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Conserver les 50 derniers messages en mémoire
messages = deque(maxlen=50)

# HTML template avec WebSocket
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Notifications ACA-Py</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        pre { white-space: pre-wrap; word-wrap: break-word; }
        body { background-color: #f8f9fa; }
        .card { 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .card-header {
            background-color: #0d6efd;
            color: white;
            font-weight: bold;
        }
        .card.mb-4 .card-header {
            background-color: #198754;
        }
        .small-section {
            font-size: 0.7em;
            max-width: 550px;
        }
        .small-section .card-header {
            padding: 0.25rem 0.5rem;
        }
        .small-section .card-body {
            padding: 0.5rem;
        }
        pre {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.25rem;
            border: 1px solid #dee2e6;
        }
        h1, h2 { 
            color: #0d6efd;
            margin-bottom: 1.5rem;
        }
        .title-small {
            font-size: 2.2rem !important;
            margin-bottom: 0.5rem;
        }
        .subtitle-small {
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        .container { 
            max-width: 1000px;
            margin-top: 2rem;
        }
        .alert-info {
            background-color: #cfe2ff;
            border-color: #b6d4fe;
            color: #084298;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="display-4 title-small">Messages d'événements ACA-Py ("webhooks")</h1>
        <p class="lead text-muted subtitle-small">Port d'écoute: {{ port }} <span style="font-size: 0.8em;">(peut être modifié avec la variable d'environnement PORT_WEBHOOK et redémarrage du conteneur)</span></p>
        <div class="card mb-4 small-section">
            <div class="card-header py-1" style="font-size: 0.85em;">
                Comment tester
            </div>
            <div class="card-body py-2">
                <pre style="font-size: 0.8em; margin-bottom: 0;">curl -X POST http://localhost:{{ port }}/webhook \
    -H "Content-Type: application/json" \
    -d '{"test": "message"}'</pre>
            </div>
        </div>
        
        <h2 class="display-4 title-small mt-5">Derniers messages reçus</h2>
        <div id="messages">
            {% if messages %}
                {% for msg in messages %}
                    <div class="card mb-3">
                        <div class="card-header">
                            {{ msg.timestamp }}
                        </div>
                        <div class="card-body">
                            <pre>{{ msg.data }}</pre>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">
                    Aucun message reçu pour le moment
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        var socket = io();
        var messagesDiv = document.getElementById('messages');
        
        socket.on('new_message', function(msg) {
            // Créer la nouvelle carte
            var newCard = document.createElement('div');
            newCard.className = 'card mb-3';
            newCard.innerHTML = `
                <div class="card-header">
                    ${msg.timestamp}
                </div>
                <div class="card-body">
                    <pre>${msg.data}</pre>
                </div>
            `;
            
            // Insérer au début
            if (messagesDiv.firstChild) {
                messagesDiv.insertBefore(newCard, messagesDiv.firstChild);
            } else {
                messagesDiv.appendChild(newCard);
            }
            
            // Supprimer le message "Aucun message reçu" s'il existe
            var noMessages = messagesDiv.querySelector('.alert-info');
            if (noMessages) {
                noMessages.remove();
            }
        });
    </script>
</body>
</html>
"""

# Catch absolutely everything
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    logger.info(f"Path: {path}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Data: {request.get_data(as_text=True)}")
    
    # Return HTML for GET requests to root
    if request.method == 'GET' and not path:
        return render_template_string(HTML_TEMPLATE, port=PORT_WEBHOOK, messages=messages)
    
    return "", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Webhook endpoint prêt"
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        if request.is_json:
            data = request.get_json()
        else:
            try:
                data = json.loads(request.data.decode('utf-8'))
            except json.JSONDecodeError:
                data = request.data.decode('utf-8')
        
        message = {
            'timestamp': timestamp,
            'data': json.dumps(data, indent=2, ensure_ascii=False)
        }
        messages.appendleft(message)
        socketio.emit('new_message', message)
        
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Erreur lors du traitement du webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Démarrage du serveur webhook sur le port {PORT_WEBHOOK}")
    logger.info("                                          (peut être modifié avec la variable d'environnement PORT_WEBHOOK et redémarrage du conteneur)")
    app.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True
    socketio.run(app, host='0.0.0.0', port=PORT_WEBHOOK)
