from flask import Flask, render_template_string
import os
import requests

app = Flask(__name__)

# L'URL publique de ton Raspberry Pi via l'ouverture de port sur ta box (Orange / Livebox)
# Exemple : http://83.114.37.238:50010
PI_PUBLIC_URL = os.environ.get("PI_PUBLIC_URL", "http://83.114.37.238:50010/trigger-wake")

# Le mot de passe secret de sécurité configuré sur ton Raspberry Pi
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "MonSuperSecretDeSecurite123")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>WOL Cloud Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #1e1e1e;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.6);
            text-align: center;
        }
        h1 { margin-top: 0; color: #ffffff; }
        button {
            background-color: #e50914;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 20px;
        }
        button:hover { background-color: #b20710; }
        .status { margin-top: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Cloud PC Controller</h1>
        <p>Allume ton PC depuis n'importe où.</p>
        <form action="/wake" method="POST">
            <button type="submit">ALLUMER LE PC</button>
        </form>
        {% if sent %}
            <p class="status" style="color: #4CAF50;">Signal transmis au Raspberry Pi avec succès !</p>
        {% elif error %}
            <p class="status" style="color: #e50914;">Erreur de communication avec le réseau local.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, sent=False, error=False)

@app.route('/wake', methods=['POST'])
def wake():
    success = False
    error = False
    try:
        headers = {"Authorization": f"Bearer {SECRET_TOKEN}"}
        response = requests.post(PI_PUBLIC_URL, headers=headers, timeout=5)
        if response.status_code == 200:
            success = True
        else:
            error = True
    except Exception as e:
        print(f"Erreur de liaison avec le Pi : {e}")
        error = True

    return render_template_string(HTML_PAGE, sent=success, error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)