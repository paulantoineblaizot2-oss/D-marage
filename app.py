from flask import Flask, render_template_string, send_from_directory
import os
import requests

app = Flask(__name__)

PI_PUBLIC_URL = os.environ.get("PI_PUBLIC_URL", "http://83.114.37.238:50010/trigger-wake")
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "123")

# Code HTML / CSS du site complet (Design moderne sombre + Page de téléchargement)
HOME_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Cloud PC Controller - WOL</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f13, #1a1a24);
            color: #f0f0f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #16161e;
            padding: 45px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            text-align: center;
            width: 380px;
            border: 1px solid #2a2a3c;
        }
        h1 { margin-top: 0; color: #ffffff; font-size: 24px; letter-spacing: 0.5px; }
        p { color: #9494b8; font-size: 14px; margin-bottom: 25px; }
        button, .btn-link {
            background: linear-gradient(135deg, #ff3344, #cc0011);
            color: white;
            border: none;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100%;
            box-shadow: 0 4px 15px rgba(255, 51, 68, 0.4);
            text-decoration: none;
            display: inline-block;
            box-sizing: border-box;
            margin-top: 10px;
        }
        button:hover, .btn-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 51, 68, 0.6);
        }
        .btn-secondary {
            background: transparent;
            border: 1px solid #3f3f59;
            color: #b8b8d0;
            box-shadow: none;
            margin-top: 15px;
        }
        .btn-secondary:hover {
            background: #222230;
            color: white;
            border-color: #5c5c80;
            box-shadow: none;
        }
        .status { margin-top: 20px; font-size: 13px; font-weight: 500; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Cloud PC Controller</h1>
        <p>Allume ton PC fixe à distance en un clic.</p>
        <form action="/wake" method="POST">
            <button type="submit">ALLUMER LE PC</button>
        </form>
        
        <a href="/downloads" class="btn-link btn-secondary">📥 Télécharger l'application</a>

        {% if sent %}
            <p class="status" style="color: #2ecc71;">Signal transmis au Raspberry Pi !</p>
        {% elif error %}
            <p class="status" style="color: #e74c3c;">Échec de communication avec le réseau.</p>
        {% endif %}
    </div>
</body>
</html>
"""

DOWNLOADS_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Téléchargements - WOL Controller</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f13, #1a1a24);
            color: #f0f0f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #16161e;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            text-align: center;
            width: 420px;
            border: 1px solid #2a2a3c;
        }
        h1 { margin-top: 0; color: #ffffff; font-size: 22px; }
        .app-box {
            background: #1f1f2e;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #2d2d44;
        }
        .app-info { text-align: left; }
        .app-title { font-weight: bold; font-size: 15px; color: #fff; }
        .app-desc { font-size: 12px; color: #9494b8; }
        .btn-dl {
            background-color: #3498db;
            color: white;
            padding: 8px 14px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 13px;
            font-weight: bold;
            transition: background 0.2s;
        }
        .btn-dl:hover { background-color: #2980b9; }
        .btn-dl.disabled { background-color: #444455; color: #888899; cursor: not-allowed; }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #9494b8;
            text-decoration: none;
            font-size: 13px;
        }
        .back-link:hover { color: #fff; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Centre de Téléchargement</h1>
        <p style="color: #9494b8; font-size: 13px; margin-bottom: 20px;">Choisis ta version pour contrôler ton PC partout.</p>
        
        <!-- Version Windows -->
        <div class="app-box">
            <div class="app-info">
                <div class="app-title">💻 Windows (Desktop)</div>
                <div class="app-desc">Application native PC</div>
            </div>
            <a href="/download/windows" class="btn-dl">Télécharger</a>
        </div>

        <!-- Version Android -->
        <div class="app-box">
            <div class="app-info">
                <div class="app-title">📱 Android (APK)</div>
                <div class="app-desc">Bientôt disponible</div>
            </div>
            <a href="#" class="btn-dl disabled">Bientôt</a>
        </div>

        <a href="/" class="back-link">← Retour au panneau de contrôle</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_PAGE, sent=False, error=False)

@app.route('/downloads')
def downloads():
    return render_template_string(DOWNLOADS_PAGE)

@app.route('/wake', methods=['POST'])
def wake():
    success = False
    error = False
    try:
        headers = {"Authorization": f"Bearer {SECRET_TOKEN}"}
        response = requests.post(PI_PUBLIC_URL, headers=headers, timeout=5)
        if response.status_code == 200:
            success = true
        else:
            error = True
    except Exception:
        error = True

    return render_template_string(HOME_PAGE, sent=success, error=error)

# Route pour télécharger l'application Windows (on va créer le fichier juste après)
@app.route('/download/windows')
def download_windows():
    return send_from_directory('static', 'wol-controller-windows.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
