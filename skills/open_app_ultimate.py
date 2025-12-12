import subprocess
import os
import webbrowser

# Applications par défaut Windows
SYSTEM_APPS = {
    "notepad": "notepad.exe",
    "bloc-notes": "notepad.exe",
    "calculatrice": "calc.exe",
    "calculette": "calc.exe",
    "paint": "mspaint.exe",
    "explorateur": "explorer.exe",
    "cmd": "cmd.exe",
    "terminal": "cmd.exe",
    "powershell": "powershell.exe",
    "paramètres": "ms-settings:",
    "panneau": "control",
}

# Applications tierces communes
THIRD_PARTY_APPS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "vscode": [
        rf"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "spotify": [
        rf"C:\Users\{os.getenv('USERNAME')}\AppData\Roaming\Spotify\Spotify.exe",
    ],
    "discord": [
        rf"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    ],
    "steam": [
        r"C:\Program Files (x86)\Steam\steam.exe",
        r"C:\Program Files\Steam\steam.exe",
    ],
    "word": [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
    ],
    "excel": [
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
    ],
    "powerpoint": [
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
    ],
}

# Sites web rapides
WEB_SHORTCUTS = {
    "youtube": "https://youtube.com",
    "gmail": "https://gmail.com",
    "google": "https://google.com",
    "twitter": "https://twitter.com",
    "facebook": "https://facebook.com",
    "netflix": "https://netflix.com",
    "twitch": "https://twitch.tv",
    "reddit": "https://reddit.com",
    "github": "https://github.com",
}

def find_app_path(app_name):
    """Cherche le chemin d'une application"""
    if app_name in THIRD_PARTY_APPS:
        for path in THIRD_PARTY_APPS[app_name]:
            if os.path.exists(path.split()[0]):  # Gère les apps avec args
                return path
    return None

def open_application(text, tts, config):
    """Ouvre une application ou un site web"""
    text = text.lower()
    print(f"[OPEN_APP] Analyse: {text}")
    
    # Vérifie les raccourcis web d'abord
    for site, url in WEB_SHORTCUTS.items():
        if site in text:
            webbrowser.open(url)
            response = f"J'ouvre {site}."
            tts.speak(response)
            print(f"✅ Site ouvert: {site}")
            return response
    
    # Vérifie les applications système
    for key, exe in SYSTEM_APPS.items():
        if key in text:
            try:
                if exe.startswith("ms-"):
                    os.startfile(exe)
                else:
                    subprocess.Popen(exe, shell=True)
                response = f"J'ouvre {key}."
                tts.speak(response)
                print(f"✅ App système: {key}")
                return response
            except Exception as e:
                print(f"❌ Erreur {key}: {e}")
                response = f"Impossible d'ouvrir {key}."
                tts.speak(response)
                return response
    
    # Vérifie les applications tierces
    for app in THIRD_PARTY_APPS.keys():
        if app in text:
            path = find_app_path(app)
            if path:
                try:
                    subprocess.Popen(path, shell=True)
                    response = f"J'ouvre {app}."
                    tts.speak(response)
                    print(f"✅ App tierce: {app}")
                    return response
                except Exception as e:
                    print(f"❌ Erreur {app}: {e}")
                    response = f"Erreur lors de l'ouverture de {app}."
                    tts.speak(response)
                    return response
            else:
                response = f"Je ne trouve pas {app} sur cet ordinateur."
                tts.speak(response)
                print(f"❌ App non trouvée: {app}")
                return response
    
    response = "Quelle application veux-tu ouvrir ?"
    tts.speak(response)
    print("❓ Application non reconnue")
    return response