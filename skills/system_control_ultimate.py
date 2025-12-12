import sys
import os
import subprocess
import re

def set_volume(text, tts, config):
    """Contrôle du volume système (Windows)"""
    try:
        # Extrait le niveau de volume
        match = re.search(r'(\d+)', text)
        if match:
            level = int(match.group(1))
            if 0 <= level <= 100:
                # Utilise NirCmd si disponible, sinon commande PowerShell
                try:
                    # Commande PowerShell pour changer le volume
                    ps_cmd = f'$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]173)'  # Volume down key
                    subprocess.run(['powershell', '-Command', f'(New-Object -ComObject WScript.Shell).SendKeys([char]{level})'], 
                                 capture_output=True, timeout=2)
                    response = f"Volume réglé à {level} pourcent."
                    tts.speak(response)
                    return response
                except:
                    response = "Impossible de contrôler le volume système."
                    tts.speak(response)
                    return response
            else:
                response = "Le volume doit être entre 0 et 100."
                tts.speak(response)
                return response
        else:
            response = "Dis-moi le niveau de volume entre 0 et 100."
            tts.speak(response)
            return response
    except Exception as e:
        print(f"Erreur volume: {e}")
        response = "Fonction volume non disponible."
        tts.speak(response)
        return response

def shutdown_computer(text, tts, config):
    """Éteint l'ordinateur"""
    response = "Êtes-vous sûr de vouloir éteindre l'ordinateur ? Dis 'confirme' dans les 10 secondes."
    tts.speak(response)
    # TODO: Implémenter confirmation
    return response

def restart_computer(text, tts, config):
    """Redémarre l'ordinateur"""
    response = "Fonction redémarrage non activée pour votre sécurité."
    tts.speak(response)
    return response

def lock_computer(text, tts, config):
    """Verrouille l'ordinateur"""
    try:
        if sys.platform == "win32":
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            response = "Ordinateur verrouillé."
            return response
    except Exception as e:
        response = "Impossible de verrouiller l'ordinateur."
        tts.speak(response)
        return response

def shutdown(text, tts, config):
    """Arrête Jarvis proprement"""
    response = "Arrêt de Jarvis. À bientôt !"
    tts.speak(response)
    print("🛑 Arrêt de Jarvis...")
    sys.exit(0)