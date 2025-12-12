from gtts import gTTS
import pygame
import tempfile
import os
import threading

class TTS:
    def __init__(self, config):
        self.config = config
        self.lock = threading.Lock()
        pygame.mixer.init()
        self.listener = None  # Sera défini par le listener
        print("✓ TTS initialisé avec Google Text-to-Speech")

    def speak(self, text):
        """Parle avec gTTS (Google)"""
        if not text or text.strip() == "":
            return
            
        print(f"🔊 Jarvis dit: {text}")
        
        with self.lock:
            try:
                # Crée un fichier temporaire
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_path = temp_file.name
                temp_file.close()
                
                # Génère l'audio avec gTTS
                tts = gTTS(text=text, lang='fr', slow=False)
                tts.save(temp_path)
                
                # Joue l'audio
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                # Attend que ce soit fini
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                # Supprime le fichier temporaire
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                print(f"❌ Erreur TTS: {e}")
                # Fallback vers pyttsx3 si gTTS échoue
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except:
                    print("❌ Impossible de faire parler Jarvis")