import smtplib
from email.message import EmailMessage
import re

def send_email(text, tts, config):
    email_cfg = config.get("email", {})
    if not email_cfg:
        tts.speak("Les paramètres email ne sont pas configurés.")
        return

    m = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if not m:
        tts.speak("À quelle adresse veux-tu envoyer l'email ?")
        return
    to_addr = m.group(0)

    subj_match = re.search(r'sujet (.+?) corps', text)
    body_match = re.search(r'corps (.+)', text)
    subject = subj_match.group(1).strip() if subj_match else "Message de Jarvis"
    body = body_match.group(1).strip() if body_match else "Bonjour."

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_cfg.get("username")
    msg['To'] = to_addr
    msg.set_content(body)

    try:
        s = smtplib.SMTP(email_cfg['smtp_server'], email_cfg['smtp_port'])
        s.starttls()
        s.login(email_cfg['username'], email_cfg['password'])
        s.send_message(msg)
        s.quit()
        tts.speak(f"Email envoyé à {to_addr}.")
    except Exception as e:
        print("Erreur SMTP:", e)
        tts.speak("Impossible d'envoyer l'email.")
