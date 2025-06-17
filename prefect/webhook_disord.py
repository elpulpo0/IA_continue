import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from config.logger import configure_logger

logger = configure_logger()

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_embed(
    message: str,
    title: str = "Notification Prefect",
    status: str = "Info",
    color: int = 3447003
):
    """
    Envoie un message enrichi (embed) à un canal Discord via un Webhook.

    :param message: Le message principal (dans 'description').
    :param title: Titre de l'embed (par défaut : "Notification Prefect").
    :param status: Statut affiché dans les champs (ex: Succès, Erreur...).
    :param color: Couleur de l'embed (int format Discord).
    """
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ DISCORD_WEBHOOK_URL non défini.")
        return

    embed = {
        "title": title,
        "description": message,
        "color": color,
        "fields": [
            {
                "name": "Status",
                "value": status,
                "inline": True
            },
            {
                "name": "Horodatage",
                "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": False
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})

    if response.status_code not in (200, 204):
        logger.error(f"❌ Erreur lors de l'envoi à Discord ({response.status_code}) : {response.text}")
    else:
        logger.info(f"✅ Message Discord envoyé ({status})")