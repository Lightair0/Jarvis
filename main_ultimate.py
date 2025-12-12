#!/usr/bin/env python3
"""
JARVIS ULTIMATE - Assistant Vocal Surpuissant
Créé avec amour pour avoir le meilleur assistant vocal
"""
import json
import queue
import threading
import sys
import time

print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗            ║
║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝            ║
║        ██║███████║██████╔╝██║   ██║██║███████╗            ║
║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║       	    ║
║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║            ║
║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝            ║ 
║                                                           ║
║              U L T I M A T E   E D I T I O N              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")

from assistant_ultimate import JarvisUltimate
from listener import Listener
from speech import TTS

# Tente d'importer l'interface web
try:
    from jarvis_web_server_ultimate import run_server
    WEB_AVAILABLE = True
    print("✅ Module web ULTIMATE détecté")
except ImportError:
    try:
        from jarvis_web_server import run_server
        WEB_AVAILABLE = True
        print("✅ Module web standard détecté")
    except ImportError:
        WEB_AVAILABLE = False
        print("⚠️  Interface web non disponible")

def load_config(path="config.json"):
    """Charge la configuration"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier {path} introuvable. Utilisation config par défaut.")
        return {
            "groq_api_key": "",
            "hotword": {"type": "simple", "keyword": "jarvis"},
            "tts": {"engine": "gtts", "rate": 150},
            "debug": True
        }

def main():
    print("\n🚀 Initialisation de JARVIS ULTIMATE...\n")
    
    config = load_config()
    q = queue.Queue()

    # Initialise les composants
    print("🔊 Initialisation du système de synthèse vocale...")
    tts = TTS(config)
    
    print("🧠 Initialisation du cerveau de JARVIS...")
    assistant = JarvisUltimate(config, tts, q)
    
    print("🎤 Initialisation du système de reconnaissance vocale...")
    listener = Listener(config, q, tts)
    
    # Lie le TTS au listener
    tts.listener = listener

    # Lance l'assistant en thread
    assistant_thread = threading.Thread(target=assistant.run, daemon=True)
    assistant_thread.start()
    
    # Lance l'interface web si disponible
    if WEB_AVAILABLE:
        web_thread = threading.Thread(target=run_server, daemon=True)
        web_thread.start()
        time.sleep(2)  # Laisse le temps au serveur de démarrer
    
    try:
        print("\n" + "="*60)
        print("✨ JARVIS ULTIMATE est maintenant EN LIGNE ! ✨")
        print("="*60)
        print("\n💬 Dis 'Jarvis' suivi de ta commande")
        
        if WEB_AVAILABLE:
            print("🌐 Interface web : http://localhost:5000")
            print("   └─ Thèmes : Iron Man, Matrix, Cyberpunk, Fire")
        
        print("\n📋 Commandes disponibles :")
        print("   • Ouvre [app] - Lance une application")
        print("   • Cherche [query] - Recherche web")
        print("   • Quelle heure/date - Infos temporelles")
        print("   • Calcule [expression] - Calculs")
        print("   • Raconte une blague - Humour")
        print("   • Pierre papier ciseaux - Jeu")
        print("   • Convertis [temp] - Conversions")
        print("   • Motive-moi - Motivation")
        print("   • Citation - Citation inspirante")
        print("   • Statistiques - Voir les stats")
        print("   • Arrête-toi - Quitter\n")
        
        print("⛔ Appuie sur Ctrl+C pour quitter\n")
        print("="*60 + "\n")
        
        tts.speak("Jarvis Ultimate en ligne. Tous les systèmes opérationnels. Prêt à t'assister.")
        listener.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de JARVIS...")
        assistant.save_all_data()
        tts.speak("Arrêt de Jarvis. Toutes les données sauvegardées. Au revoir !")
        print("💾 Données sauvegardées")
        print("✅ JARVIS ULTIMATE arrêté proprement\n")
        sys.exit(0)

if __name__ == "__main__":
    main()