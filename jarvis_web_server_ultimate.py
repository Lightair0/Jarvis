from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import psutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis_ultimate_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

jarvis_state = {
    "status": "ACTIF",
    "vocal": "EN LIGNE",
    "ia": "HYBRIDE",
    "last_command": "En attente...",
    "last_response": "",
    "cpu": 0,
    "ram": 0,
    "network": 0,
    "console_messages": [],
    "commands_count": 0,
    "questions_count": 0
}

def load_html():
    """Charge l'interface HTML"""
    try:
        with open('jarvis_interface_ultra.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        try:
            with open('jarvis_interface.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return """
            <html>
            <head><title>JARVIS ULTIMATE</title></head>
            <body style="background: #000; color: #0f0; font-family: monospace; padding: 50px; text-align: center;">
                <h1>⚠️ Fichier interface HTML introuvable</h1>
                <p>Crée jarvis_interface_ultra.html ou jarvis_interface.html</p>
                <p>Le serveur fonctionne quand même !</p>
            </body>
            </html>
            """

@app.route('/')
def index():
    return render_template_string(load_html())

@app.route('/api/status')
def get_status():
    return jsonify(jarvis_state)

@socketio.on('connect')
def handle_connect():
    print('🌐 Client connecté à l\'interface')
    emit('status_update', jarvis_state)

def update_system_stats():
    """Met à jour les stats système en temps réel"""
    while True:
        try:
            jarvis_state['cpu'] = psutil.cpu_percent(interval=1)
            jarvis_state['ram'] = psutil.virtual_memory().percent
            
            # Envoie aux clients connectés
            socketio.emit('stats_update', {
                'cpu': jarvis_state['cpu'],
                'ram': jarvis_state['ram']
            })
        except Exception as e:
            print(f"Erreur stats: {e}")
        
        time.sleep(2)

def add_console_message(message):
    """Ajoute un message à la console"""
    timestamp = time.strftime('%H:%M:%S')
    jarvis_state['console_messages'].append({
        'time': timestamp,
        'message': message
    })
    
    if len(jarvis_state['console_messages']) > 50:
        jarvis_state['console_messages'].pop(0)
    
    socketio.emit('console_message', {
        'time': timestamp,
        'message': message
    })

def update_jarvis_command(command, response):
    """Met à jour la dernière commande et réponse"""
    jarvis_state['last_command'] = command
    jarvis_state['last_response'] = response
    jarvis_state['commands_count'] += 1
    jarvis_state['questions_count'] += 1
    
    add_console_message(f"USER: {command}")
    add_console_message(f"JARVIS: {response}")
    
    socketio.emit('command_update', {
        'command': command,
        'response': response
    })

def run_server():
    """Lance le serveur web"""
    stats_thread = threading.Thread(target=update_system_stats, daemon=True)
    stats_thread.start()
    
    print("\n" + "="*60)
    print("🌐 Interface Web JARVIS ULTIMATE lancée !")
    print("📍 URL : http://localhost:5000")
    print("🎨 Thèmes disponibles : Iron Man, Matrix, Cyberpunk, Fire")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_server()