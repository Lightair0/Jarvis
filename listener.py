import speech_recognition as sr

class Listener:
    def __init__(self, config, queue, tts):
        self.config = config
        self.queue = queue
        self.tts = tts
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500  # Augmenter la sensibilité (Passage de 1000 à 500)
        
        # Essaye d'initialiser le micro, sinon utilise sounddevice
        try:
            self.mic = sr.Microphone()
            self.mode = "pyaudio"
            print("Mode PyAudio détecté")
        except (AttributeError, OSError):
            # PyAudio pas dispo, on va utiliser sounddevice
            self.mode = "sounddevice"
            self.sample_rate = 16000
            print("Mode Sounddevice activé") #J'ai enlevé le morceau "sans pyaudio"
        
        self.hotword = config.get("hotword", {}).get("keyword", "jarvis").lower()
        self.hotword_type = config.get("hotword", {}).get("type", "simple")

    def capture_audio(self, duration=8):
        """Capture audio selon le mode disponible"""
        if self.mode == "sounddevice":
            import sounddevice as sd
            import numpy as np
            
            audio_data = sd.rec(int(duration * self.sample_rate), 
                               samplerate=self.sample_rate, 
                               channels=1, 
                               dtype=np.int16)
            sd.wait()
            audio_bytes = audio_data.tobytes()
            return sr.AudioData(audio_bytes, self.sample_rate, 2)
        else:
            with self.mic as source:
                return self.recognizer.listen(source, phrase_time_limit=duration)

    def run(self):
        # Calibration initiale
        if self.mode == "pyaudio":
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complète. Prêt à écouter.")
        
        while True:
            print("En écoute (attente du mot-clé ou commande)...")
            try:
                audio = self.capture_audio(duration=8)
            except Exception as e:
                print("Erreur capture audio:", e)
                continue
            
            try:
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                text = text.lower()
                print("Reconnu:", text)
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print("Erreur STT:", e)
                continue

            if self.hotword_type == "simple":
                if self.hotword in text:
                    clean = text.replace(self.hotword, "").strip()
                    if clean == "":
                        
                        try:
                            audio2 = self.capture_audio(duration=6)
                            cmd = self.recognizer.recognize_google(audio2, language="fr-FR").lower()
                            print("Commande:", cmd)
                            self.queue.put(cmd)
                            self.tts.speak("Oui ?") #Déplacer de L.71
                        except sr.UnknownValueError:
                            print("Commande non reconnue")
                        except Exception as e:
                            print("Erreur lors de la capture de commande:", e)
                    else:
                        print("Commande détectée directement:", clean)
                        self.queue.put(clean)
                    
                    # Recalibration après traitement pour la prochaine écoute
                    if self.mode == "pyaudio":
                        try:
                            with self.mic as source:
                                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        except:
                            pass
            else:
                self.queue.put(text)