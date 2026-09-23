from flask import Flask, request, jsonify
import socket
import os

app = Flask(__name__)
MAC_ADDRESS = "4C-CC-6A-BB-E5-44"

# Un mot de passe secret partagé entre Render et ton Pi
SECRET_TOKEN = "MonSuperSecretDeSecurite123"

def send_wol(mac):
    clean_mac = mac.replace('-', '').replace(':', '')
    data = bytes.fromhex('FF' * 6 + clean_mac * 16)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ('255.255.255.255', 9))

@app.route('/trigger-wake', methods=['POST'])
def trigger_wake():
    # Vérifie le token de sécurité envoyé dans les en-têtes
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {SECRET_TOKEN}":
        return jsonify({"status": "unauthorized"}), 403

    try:
        send_wol(MAC_ADDRESS)
        print("Paquet WOL envoyé par le Raspberry Pi suite à une requête valide !")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)