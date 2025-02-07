from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import argparse

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = post_data.decode('utf-8')

        # Log à la console console
        print(f"\n=== WEBHOOK REÇU À {timestamp} === {self.server.custom_text}")
        print(f"Path: {self.path}")
        print(f"Headers: {dict(self.headers)}")
        print(f"Data: {json.dumps(data, indent=2)}")
        print("=" * 50 + "\n")

        # Log à un fichier
        with open("webhooks.log", "a") as f:
            f.write(f"\n=== WEBHOOK REÇU À {timestamp} === {self.server.custom_text}\n")
            f.write(f"Path: {self.path}\n")
            f.write(f"Headers: {dict(self.headers)}\n")
            f.write(f"Data: {json.dumps(data, indent=2)}\n")
            f.write("=" * 50 + "\n")

        # Réponse
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")

def run_server(port, custom_text):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    httpd.custom_text = custom_text  # Set the custom_text attribute
    print(f"Webhook logger démarré sur http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté")
        httpd.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Webhook Logger Server')
    parser.add_argument('-p', '--port', type=int, default=8020,
                        help='Port sur lequel le serveur écoute (défaut: 8020)')
    parser.add_argument('-t', '--text', type=str, default='',
                        help='Texte personnalisé à ajouter aux logs')

    args = parser.parse_args()
    run_server(args.port, args.text)
