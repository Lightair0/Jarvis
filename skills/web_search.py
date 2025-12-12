import webbrowser
import re

def search_web(text, tts, config):
    q = text
    q = re.sub(r'^(cherche|cherchez|recherche|cherche-moi)\s*', '', q)
    if not q:
        tts.speak("Que veux-tu que je recherche ?")
        return
    url = "https://www.google.com/search?q=" + q.replace(" ", "+")
    webbrowser.open(url)
    tts.speak(f"Voici les résultats pour {q}.")
