import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1384074750946705500/vGftTVhKZfOQU_Jba8AppR0o4_n3O2esBlF8Q8bqDZJQt-QeEa3CZ7kFlaWvh6tCDA1g"

def send_discord_embed(message):
    """Envoyer un message à un canal Discord via un Webhook."""
    data = {"embeds": [{
                "title": "Prefect test",
                "description": message,
                "color": 5814783,
                "fields": [{
                        "name": "Status",
                        "value": "Succès",
                        "inline": True
                    }]}]}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Erreur lors de l'envoi de l'embed : {response.status_code}")
    else:
        print("Embed envoyé avec succès !")
