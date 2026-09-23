from flask import Flask, render_template_string, send_from_directory
import os
import requests

app = Flask(__name__)

PI_PUBLIC_URL = os.environ.get("PI_PUBLIC_URL", "http://83.114.37.238:50010/trigger-wake")
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "1234")

# Template global inspiré des designs gaming/dark modernes
BASE_STYLE = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Outfit', sans-serif;
            background-color: #0b0f19;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.1) 0px, transparent 50%);
            color: #f3f4f6;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            width: 100%;
            max-width: 420px;
            text-align: center;
        }
        h1 {
            margin-top: 0;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #ffffff;
            background: linear-gradient(to right, #ffffff, #9ca3af);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            padding: 14px 20px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.25s ease;
            width: 100%;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
            text-decoration: none;
            display: inline-block;
            margin-bottom: 12px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
            filter: brightness(1.1);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #d1d5db;
            box-shadow: none;
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            box-shadow: none;
            border-color: rgba(255, 255, 255, 0.2);
        }
        .badge-status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
        }
        .success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .error { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .download-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-align: left;
        }
        .download-info .title { font-weight: 600; font-size: 14px; color: #fff; }
        .download-info .desc { font-size: 12px; color: #9ca3af; }
        .btn-small {
            background: #0ea5e9;
            color: white;
            padding: 8px 14px;
            font-size: 13px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }
        .btn-small:hover { background: #0284c7; }
        .btn-small.disabled { background: rgba(255,255,255,0.08); color: #6b7280; cursor: not-allowed; }
        .back-link {
            display: inline-block;
            margin-top: 15px;
            color: #9ca3af;
            text-decoration: none;
            font-size: 13px;
            transition: color 0.2s;
        }
        .back-link:hover { color: #fff; }
    </style>
"""

HOME_PAGE = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Cloud PC - Control Center</title>
    {BASE_STYLE}
</head>
<body>
    <div class="container">
        <h1>Cloud PC Controller</h1>
        <p>Interface de réveil à distance sécurisée</p>
        
        <form action="/wake" method="POST">
            <button type="submit" class="btn">⚡ ALLUMER LE PC</button>
        </form>
        
        <a href="/downloads" class="btn btn-secondary">📥 Espace Téléchargements</a>

        {{% if sent %}}
            <div class="badge-status success">Signal Wake-on-LAN transmis au réseau !</div>
        {{% elif error %}}
            <div class="badge-status error">Erreur de communication avec le relais.</div>
        {{% endif %}}
    </div>
</body>
</html>
"""

DOWNLOADS_PAGE = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Téléchargements - Cloud PC</title>
    {BASE_STYLE}
</head>
<body>
    <div class="container" style="max-width: 460px;">
        <h1>Téléchargements</h1>
        <p>Récupère l'application cliente pour tes différents appareils.</p>
        
        <!-- Windows -->
        <div class="download-card">
            <div class="download-info">
                <div class="title">💻 Windows Desktop</div>
                <div class="desc">Application native x64</div>
            </div>
            <a href="/download/windows" class="btn-small">Télécharger</a>
        </div>

        <!-- Android -->
        <div class="download-card">
            <div class="download-info">
                <div class="title">📱 Android APK</div>
                <div class="desc">Bientôt disponible</div>
            </div>
            <a href="#" class="btn-small disabled">Bientôt</a>
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
            success = True
        else:
            error = True
    except Exception:
        error = True

    return render_template_string(HOME_PAGE, sent=success, error=error)

@app.route('/download/windows')
def download_windows():
    return send_from_directory('static', 'wol-controller-windows.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
