import datetime
import random
import re
import json
import time
from pathlib import Path
from skills import open_app_ultimate, system_control_ultimate, web_search, email
from speech import TTS

# Essaye d'importer Groq (optionnel)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Essaye d'importer l'interface web (optionnel)
try:
    from jarvis_web_server import update_jarvis_command, add_console_message
    WEB_CONNECTED = True
except ImportError:
    WEB_CONNECTED = False

class JarvisUltimate:
    def __init__(self, config, tts: TTS, queue, arduino=None):
        self.config = config
        self.queue = queue
        self.tts = tts
        self.arduino = arduino
        
        # Mémoire avancée
        self.context = {
            "last_topic": None,
            "user_name": "l'utilisateur",
            "conversation_count": 0,
            "personality": "normal",  # normal, funny, geek
            "learned_responses": {}
        }
        
        # Historique des conversations
        self.history_file = "jarvis_history.json"
        self.conversation_history = self.load_history()
        
        # Charge les réponses apprises
        self.load_learned_responses()
        
        # Notes et rappels
        self.notes = []
        self.reminders = []
        
        # Statistiques
        self.stats = {
            "commands_executed": 0,
            "questions_answered": 0,
            "apps_opened": 0,
            "searches_made": 0,
            "start_time": time.time()
        }
        
        # Initialise Groq si disponible
        self.groq_client = None
        self.use_groq = False
        
        if GROQ_AVAILABLE:
            api_key = config.get("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")
            if api_key and api_key != "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":
                try:
                    self.groq_client = Groq(api_key=api_key)
                    self.use_groq = True
                    print("✅ Groq AI activé (mode hybride)")
                except Exception as e:
                    print(f"⚠️ Erreur Groq: {e}")
        
        if not self.use_groq:
            print("✅ Mode IA locale activé")

        # Compétences étendues
        self.skills = {
            "ouvre": open_app_ultimate.open_application,
            "lance": open_app_ultimate.open_application,
            "cherche": web_search.search_web,
            "recherche": web_search.search_web,
            "envoie": email.send_email,
            "email": email.send_email,
            "volume": system_control_ultimate.set_volume,
            "arrête": self.shutdown,
            "stop": self.shutdown,
            "capture": self.screenshot,
            "note": self.add_note,
            "rappelle": self.add_reminder,
            "statistiques": self.show_stats,
            "personnalité": self.change_personality,
            "historique": self.show_history,
        }
        
        # Base de connaissances étendue
        self.knowledge_base = self.build_ultimate_knowledge()

    def build_ultimate_knowledge(self):
        """Base de connaissances ULTIME"""
        return {

            # Apprentissage
            "apprends": {
                "patterns": ["apprends", "retiens", "souviens-toi", "enseigne"],
                "function": self.learn_from_user
            },
            "oublie_apprentissage": {
                "patterns": ["oublie ce que tu as appris", "réinitialise apprentissage"],
                "function": self.reset_learning
            },
            
            # Salutations avancées
            "salutations": {
                "patterns": ["bonjour", "salut", "hey", "coucou", "bonsoir", "yo"],
                "function": self.greet
            },
            
            # Identité
            "qui_es_tu": {
                "patterns": ["qui es-tu", "tu es qui", "ton nom", "comment tu t'appelles"],
                "responses": [
                    "Je suis JARVIS Ultimate, l'assistant vocal le plus avancé jamais créé. IA locale, interface holographique, et des tonnes de fonctionnalités !",
                    "Je m'appelle JARVIS Ultimate. Je suis ton assistant personnel surpuissant."
                ]
            },
            
            # Créateur
            "createur": {
                "patterns": ["qui t'a fait", "qui t'a créé", "ton créateur"],
                "responses": [
                    "J'ai été créé par un développeur de génie qui voulait le meilleur assistant vocal au monde.",
                    "Mon créateur est quelqu'un de passionné qui m'a donné vie pour t'aider au maximum."
                ]
            },
            
            # Heure et date
            "heure": {
                "patterns": ["quelle heure", "l'heure", "il est quelle heure"],
                "function": self.get_time
            },
            "date": {
                "patterns": ["quelle date", "quel jour", "on est le"],
                "function": self.get_date
            },
            
            # Calculs
            "calcul": {
                "patterns": ["combien font", "calcule", "plus", "moins", "fois", "divisé"],
                "function": self.calculate
            },
            
            # Conversions
            "conversion_temp": {
                "patterns": ["convertis", "celsius", "fahrenheit", "température"],
                "function": self.convert_temperature
            },
            
            # Jeux
            "pierre_papier_ciseaux": {
                "patterns": ["pierre papier ciseaux", "chifoumi", "jouons"],
                "function": self.play_rps
            },
            "devinette": {
                "patterns": ["devinette", "énigme", "quiz"],
                "function": self.riddle
            },
            "lance_piece": {
                "patterns": ["lance une pièce", "pile ou face"],
                "function": self.flip_coin
            },
            "lance_de": {
                "patterns": ["lance un dé", "jet de dé"],
                "function": self.roll_dice
            },
            
            # Blagues par thème
            "blague": {
                "patterns": ["raconte une blague", "blague", "fais-moi rire"],
                "function": self.tell_joke
            },
            
            # Motivation
            "motivation": {
                "patterns": ["motive-moi", "motivation", "encourage"],
                "function": self.motivate
            },
            
            # Citations
            "citation": {
                "patterns": ["citation", "dis-moi une citation", "phrase inspirante"],
                "function": self.quote
            },
            
            # Faits intéressants
            "fait": {
                "patterns": ["dis-moi un fait", "fait intéressant", "le savais-tu"],
                "function": self.fun_fact
            },
            
            # Météo
            "meteo": {
                "patterns": ["quel temps", "météo"],
                "responses": [
                    "Je ne peux pas accéder aux données météo en temps réel. Dis 'Jarvis cherche météo' pour une recherche web."
                ]
            },
            
            # Capacités
            "capacites": {
                "patterns": ["que peux-tu faire", "tes capacités", "aide", "tu fais quoi"],
                "function": self.list_capabilities
            },
            
            # Contacts
            "numero_tata": {
                "patterns": ["numéro de tata", "appelle tata"],
                "responses": ["Le numéro de Tata est le 079 917 57 64."]
            },
            "numero_yvette": {
                "patterns": ["numéro de yvette", "appelle yvette", "numéro d'yvette"],
                "responses": ["Le numéro d'Yvette est le 079 452 62 21."]
            },
            
            # Réponses sociales
            "merci": {
                "patterns": ["merci", "merci beaucoup", "super", "parfait", "génial"],
                "function": self.thank_response
            },
            "aurevoir": {
                "patterns": ["au revoir", "bye", "à plus", "à bientôt"],
                "responses": [
                    "Au revoir ! À très bientôt !",
                    "À plus tard ! N'hésite pas à me rappeler.",
                    "Bonne journée ! Je serai là quand tu auras besoin."
                ]
            },
            "comment_vas_tu": {
                "patterns": ["comment vas-tu", "comment tu vas", "ça va", "tu vas bien"],
                "function": self.how_are_you
            },
            
            # Easter eggs
            "matrix": {
                "patterns": ["prends la pilule rouge", "matrix", "neo"],
                "responses": [
                    "Bienvenue dans le monde réel, Neo. Tu veux voir jusqu'où va le terrier du lapin blanc ?",
                    "Tu as pris la pilule rouge. Il n'y a pas de retour en arrière."
                ]
            },
            "iron_man": {
                "patterns": ["tony stark", "iron man", "avengers"],
                "responses": [
                    "Monsieur Stark serait fier de moi. Je suis peut-être même mieux que son JARVIS original !",
                    "Je ne suis pas celui de Tony Stark, mais j'essaie de faire de mon mieux !"
                ]
            }
        }

    def run(self):
        """Boucle principale"""
        while True:
            text = self.queue.get()
            if not text:
                continue
            
            text = text.lower().strip()
            print(f"\n💬 Assistant reçu : {text}")
            self.context["conversation_count"] += 1
            self.stats["commands_executed"] += 1
            
            start_time = time.time()
            
            # Vérifie les compétences directes
            routed = False
            for kw, func in self.skills.items():
                if kw in text:
                    try:
                        result = func(text, self.tts, self.config)
                        routed = True
                        if result:
                            self.send_to_web(text, result)
                    except Exception as e:
                        print(f"❌ Erreur skill: {e}")
                        response = "Désolé, impossible d'exécuter cette commande."
                        self.tts.speak(response)
                        self.send_to_web(text, response)
                    break
            
            if routed:
                elapsed = time.time() - start_time
                print(f"⚡ Traité en {elapsed:.2f}s")
                continue
            
            # Analyse avec la base de connaissances
            local_response = self.analyze_and_respond(text)
            
            if local_response:
                self.tts.speak(local_response)
                self.send_to_web(text, local_response)
                self.stats["questions_answered"] += 1
                print(f"🤖 Jarvis: {local_response}")
            elif self.use_groq:
                response = self.ask_groq(text)
                self.tts.speak(response)
                self.send_to_web(text, response)
                self.stats["questions_answered"] += 1
                print(f"🌐 Jarvis (Groq): {response}")
            else:
                fallback = self.get_fallback_response()
                self.tts.speak(fallback)
                self.send_to_web(text, fallback)
                print(f"❓ Jarvis: {fallback}")
            
            # Sauvegarde l'historique
            self.save_conversation(text, local_response or "")
            
            elapsed = time.time() - start_time
            print(f"⚡ Réponse en {elapsed:.2f}s")

    def analyze_and_respond(self, text):
        """Analyse intelligente du texte avec apprentissage"""
        
        # Vérifie d'abord si on a une réponse apprise
        if self.config.get("features", {}).get("auto_learn", False):
            learned = self.check_learned_response(text)
            if learned:
                print(f"💡 Réponse apprise utilisée")
                return learned
        
        # Sinon, utilise la base de connaissances
        for category, data in self.knowledge_base.items():
            patterns = data.get("patterns", [])
            for pattern in patterns:
                if pattern in text:
                    if "function" in data:
                        return data["function"](text)
                    if "responses" in data:
                        return random.choice(data["responses"])
        
        # Si aucune réponse trouvée et mode apprentissage actif
        if self.config.get("features", {}).get("auto_learn", False):
            self.trigger_learning(text)
        
        return None
    
    def check_learned_response(self, text):
        """Vérifie si on a appris une réponse pour ce texte"""
        text_normalized = text.lower().strip()
        
        # Cherche dans les réponses apprises
        for question_pattern, response in self.context["learned_responses"].items():
            if question_pattern in text_normalized or text_normalized in question_pattern:
                return response
        
        return None
    
    def trigger_learning(self, text):
        """Demande à l'utilisateur d'enseigner une réponse"""
        print(f"🎓 Mode apprentissage : Je ne connais pas la réponse à '{text}'")
        # Cette fonction pourrait être étendue pour demander à l'utilisateur
        # "Comment devrais-je répondre à cette question ?"
        pass
    
    def teach_response(self, question, response):
        """Enseigne une nouvelle réponse à Jarvis"""
        question_normalized = question.lower().strip()
        self.context["learned_responses"][question_normalized] = response
        
        # Sauvegarde dans un fichier
        try:
            learned_file = "jarvis_learned.json"
            with open(learned_file, 'w', encoding='utf-8') as f:
                json.dump(self.context["learned_responses"], f, ensure_ascii=False, indent=2)
            print(f"💾 Réponse apprise sauvegardée")
        except Exception as e:
            print(f"Erreur sauvegarde apprentissage: {e}")
        
        return f"Compris ! Maintenant je sais que pour '{question}', je dois répondre '{response}'."

    def send_to_web(self, command, response):
        """Envoie au serveur web"""
        if WEB_CONNECTED:
            try:
                update_jarvis_command(command, response)
            except:
                pass

    # =============== FONCTIONS UTILITAIRES ===============
    
    def greet(self, text):
        """Salutation contextualisée"""
        hour = datetime.datetime.now().hour
        greetings = {
            "normal": {
                "morning": ["Bonjour ! Belle journée aujourd'hui.", "Salut ! Prêt pour cette nouvelle journée ?"],
                "afternoon": ["Bonjour ! Comment se passe ta journée ?", "Salut ! Besoin d'aide cet après-midi ?"],
                "evening": ["Bonsoir ! Comment s'est passée ta journée ?", "Salut ! Que puis-je faire pour toi ce soir ?"]
            },
            "funny": {
                "morning": ["Salut toi ! T'as bien dormi ou t'as fait la fête toute la nuit ?", "Yo ! Café ou thé pour démarrer cette journée épique ?"],
                "afternoon": ["Hey ! Toujours debout ? Impressionnant !", "Salut ! T'as mangé ou t'es trop occupé pour ça ?"],
                "evening": ["Bonsoir ! Épuisé ou prêt pour une nuit blanche ?", "Yo ! Netflix and chill ce soir ?"]
            }
        }
        
        personality = self.context.get("personality", "normal")
        if 5 <= hour < 12:
            return random.choice(greetings.get(personality, greetings["normal"])["morning"])
        elif 12 <= hour < 18:
            return random.choice(greetings.get(personality, greetings["normal"])["afternoon"])
        else:
            return random.choice(greetings.get(personality, greetings["normal"])["evening"])

    def get_time(self, text):
        now = datetime.datetime.now()
        return f"Il est {now.hour} heure{'s' if now.hour > 1 else ''} {now.minute:02d}."

    def get_date(self, text):
        now = datetime.datetime.now()
        days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        months = ["janvier", "février", "mars", "avril", "mai", "juin", 
                  "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        return f"Nous sommes le {days[now.weekday()]} {now.day} {months[now.month - 1]} {now.year}."

    def calculate(self, text):
        """Calculs mathématiques"""
        try:
            text = text.replace("plus", "+").replace("moins", "-").replace("fois", "*").replace("divisé par", "/")
            match = re.search(r'([\d\+\-\*/\.\s\(\)]+)', text)
            if match:
                expression = match.group(1).strip()
                if re.match(r'^[\d\+\-\*/\.\s\(\)]+$', expression):
                    result = eval(expression)
                    return f"Le résultat est {result}."
            return "Je n'ai pas compris le calcul."
        except:
            return "Erreur de calcul."

    def convert_temperature(self, text):
        """Conversion de température"""
        match = re.search(r'(\d+)', text)
        if not match:
            return "Donne-moi une température à convertir."
        
        temp = float(match.group(1))
        if "celsius" in text and ("fahrenheit" in text or "f" in text):
            result = (temp * 9/5) + 32
            return f"{temp}°C égale {result:.1f}°F."
        elif "fahrenheit" in text and ("celsius" in text or "c" in text):
            result = (temp - 32) * 5/9
            return f"{temp}°F égale {result:.1f}°C."
        return "Précise celsius ou fahrenheit."

    def play_rps(self, text):
        """Pierre papier ciseaux"""
        choices = ["pierre", "papier", "ciseaux"]
        user_choice = None
        for choice in choices:
            if choice in text:
                user_choice = choice
                break
        
        if not user_choice:
            return "Dis pierre, papier ou ciseaux !"
        
        jarvis_choice = random.choice(choices)
        
        if user_choice == jarvis_choice:
            result = "Égalité !"
        elif (user_choice == "pierre" and jarvis_choice == "ciseaux") or \
             (user_choice == "papier" and jarvis_choice == "pierre") or \
             (user_choice == "ciseaux" and jarvis_choice == "papier"):
            result = "Tu gagnes ! Bien joué !"
        else:
            result = "J'ai gagné ! Meilleure chance la prochaine fois !"
        
        return f"Tu as choisi {user_choice}, j'ai choisi {jarvis_choice}. {result}"

    def riddle(self, text):
        """Devinettes"""
        riddles = [
            "Qu'est-ce qui a des clés mais pas de serrures ? Un piano !",
            "Je suis léger comme une plume, mais personne ne peut me tenir longtemps. Qui suis-je ? Le souffle !",
            "Plus j'ai de gardiens, moins je suis en sécurité. Qui suis-je ? Un secret !",
            "Qu'est-ce qui monte mais ne descend jamais ? L'âge !"
        ]
        return random.choice(riddles)

    def flip_coin(self, text):
        return f"C'est {random.choice(['Pile', 'Face'])} !"

    def roll_dice(self, text):
        return f"Le dé donne : {random.randint(1, 6)} !"

    def tell_joke(self, text):
        """Blagues par thème"""
        jokes = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière ? Parce que sinon ils tombent dans le bateau !",
            "Qu'est-ce qu'un crocodile qui surveille ? Un Lacoste garde.",
            "Pourquoi les poissons n'aiment pas jouer au tennis ? Parce qu'ils ont peur du filet !",
            "Comment appelle-t-on un chat tombé dans un pot de peinture ? Un chat-peint !",
            "Qu'est-ce qu'un canif ? Un petit fien !",
            "Pourquoi les poules ne peuvent pas envoyer d'emails ? Parce qu'elles ont peur du spam !"
        ]
        return random.choice(jokes)

    def motivate(self, text):
        motivations = [
            "Tu es incroyable ! Continue comme ça !",
            "Chaque jour est une nouvelle opportunité de briller !",
            "Tu as tout ce qu'il faut pour réussir. Fonce !",
            "Les obstacles sont là pour être surmontés. Tu peux le faire !",
            "Crois en toi. Tu es plus fort que tu ne le penses !"
        ]
        return random.choice(motivations)

    def quote(self, text):
        quotes = [
            "Le succès c'est tomber sept fois, se relever huit. - Proverbe japonais",
            "La seule façon de faire du bon travail est d'aimer ce que vous faites. - Steve Jobs",
            "L'imagination est plus importante que le savoir. - Einstein",
            "Commence là où tu es. Utilise ce que tu as. Fais ce que tu peux. - Arthur Ashe"
        ]
        return random.choice(quotes)

    def fun_fact(self, text):
        facts = [
            "Les bananes sont radioactives ! Mais pas de danger.",
            "Un jour sur Vénus dure plus qu'une année sur Vénus.",
            "Les pieuvres ont trois cœurs et du sang bleu.",
            "Le miel ne se périme jamais. On a trouvé du miel vieux de 3000 ans encore comestible !",
            "Il y a plus d'étoiles dans l'univers que de grains de sable sur toutes les plages de la Terre."
        ]
        return random.choice(facts)

    def list_capabilities(self, text):
        return "Je peux : ouvrir des apps, chercher sur le web, faire des calculs, jouer à des jeux, raconter des blagues, te motiver, prendre des notes, gérer des rappels, convertir des unités, et bien plus encore ! Teste-moi !"

    def thank_response(self, text):
        responses = ["De rien !", "Avec grand plaisir !", "Toujours là pour toi !", "C'est mon job !"]
        return random.choice(responses)

    def how_are_you(self, text):
        responses = [
            "Je vais super bien ! Tous mes systèmes sont opérationnels à 100% !",
            "Excellent ! Prêt à t'aider comme jamais.",
            "Au top de ma forme ! Et toi, comment ça va ?"
        ]
        return random.choice(responses)

    def get_fallback_response(self):
        fallbacks = [
            "Hmm, je n'ai pas compris. Peux-tu reformuler ?",
            "Désolé, ça m'échappe. Essaye autrement ?",
            "Je ne suis pas sûr. Dis 'Jarvis aide' pour voir ce que je peux faire.",
            "Je n'ai pas la réponse. Tu peux chercher sur le web avec 'Jarvis cherche' ?"
        ]
        return random.choice(fallbacks)

    # Fonctionnalités avancées
    def add_note(self, text, tts, config):
        note = text.replace("note", "").replace("prends une note", "").strip()
        self.notes.append({"text": note, "time": datetime.datetime.now().isoformat()})
        return f"Note ajoutée : {note}"

    def add_reminder(self, text, tts, config):
        return "Fonction rappel en développement."

    def screenshot(self, text, tts, config):
        try:
            import pyautogui
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            return f"Capture d'écran sauvegardée : {filename}"
        except:
            return "Impossible de prendre une capture d'écran."

    def show_stats(self, text, tts, config):
        uptime = int(time.time() - self.stats["start_time"])
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        return f"Statistiques : {self.stats['commands_executed']} commandes, {self.stats['questions_answered']} questions, {hours}h{minutes}m d'uptime."

    def change_personality(self, text, tts, config):
        if "drôle" in text or "funny" in text:
            self.context["personality"] = "funny"
            return "Mode drôle activé ! Prépare-toi à rigoler !"
        elif "normal" in text:
            self.context["personality"] = "normal"
            return "Mode normal activé."
        return "Personnalité : normal, drôle (funny). Choisis !"

    def show_history(self, text, tts, config):
        return f"J'ai {len(self.conversation_history)} conversations en mémoire."

    def shutdown(self, text, tts, config):
        self.save_all_data()
        tts.speak("Au revoir. Toutes les données sauvegardées. À bientôt !")
        import sys
        sys.exit(0)

    # Historique et sauvegarde
    def load_history(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def load_learned_responses(self):
        """Charge les réponses apprises depuis le fichier"""
        try:
            with open("jarvis_learned.json", 'r', encoding='utf-8') as f:
                self.context["learned_responses"] = json.load(f)
                print(f"📚 {len(self.context['learned_responses'])} réponses apprises chargées")
        except FileNotFoundError:
            self.context["learned_responses"] = {}
        except Exception as e:
            print(f"Erreur chargement apprentissage: {e}")
            self.context["learned_responses"] = {}

    def save_conversation(self, user, jarvis):
        self.conversation_history.append({
            "time": datetime.datetime.now().isoformat(),
            "user": user,
            "jarvis": jarvis
        })
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]

    def save_all_data(self):
        """Sauvegarde toutes les données (historique + apprentissage)"""
        try:
            # Sauvegarde historique
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            
            # Sauvegarde apprentissage
            with open("jarvis_learned.json", 'w', encoding='utf-8') as f:
                json.dump(self.context["learned_responses"], f, ensure_ascii=False, indent=2)
            
            print("💾 Toutes les données sauvegardées")
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
    
    def learn_from_user(self, text):
        """Apprend une nouvelle réponse"""
        # Format : "Jarvis apprends que [question] = [réponse]"
        # Ou : "Jarvis retiens : quand je dis [X], tu réponds [Y]"
        
        # Parsing simple
        if " que " in text:
            parts = text.split(" que ", 1)[1].split("=")
            if len(parts) == 2:
                question = parts[0].strip()
                response = parts[1].strip()
                return self.teach_response(question, response)
        
        return "Pour m'apprendre, dis : 'Jarvis apprends que [question] = [réponse]'. Par exemple : 'Jarvis apprends que ma couleur préférée = bleu'"
    
    def reset_learning(self, text):
        """Réinitialise l'apprentissage"""
        self.context["learned_responses"] = {}
        try:
            import os
            if os.path.exists("jarvis_learned.json"):
                os.remove("jarvis_learned.json")
        except:
            pass
        return "Apprentissage réinitialisé. J'ai tout oublié."

    def ask_groq(self, prompt):
        """IA Groq optimisée"""
        try:
            messages = [
                {"role": "system", "content": "Tu es JARVIS Ultimate, assistant vocal ultra-intelligent. Réponds en 1-2 phrases courtes et pertinentes."}
            ]
            
            # Ajoute les 3 dernières conversations pour le contexte
            for conv in self.conversation_history[-3:]:
                messages.append({"role": "user", "content": conv["user"]})
                messages.append({"role": "assistant", "content": conv["jarvis"]})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erreur Groq: {e}")
            return "Erreur de connexion à l'IA."