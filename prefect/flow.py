from prefect import flow, task
from prefect.logging import get_run_logger
import os
import time
import requests
from dotenv import load_dotenv
from webhook_disord import send_discord_embed

load_dotenv()

# Configuration
PYTHONIOENCODING = os.getenv("PYTHONIOENCODING", "utf-8")
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "http://127.0.0.1:4200/api")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

def send_discord(message: str, status: str = "Succès", title: str = None):
    """Fonction utilitaire pour envoyer un message Discord avec titre et couleur adaptés."""
    colors = {
        "Succès": 0x2ecc71,    # vert
        "Erreur": 0xe74c3c,    # rouge
        "Warning": 0xf1c40f,   # jaune
        "Info": 3447003        # bleu par défaut
    }
    if title is None:
        if status == "Succès":
            title = "✅ Succès"
        elif status == "Erreur":
            title = "❌ Erreur"
        elif status == "Warning":
            title = "⚠️ Avertissement"
        else:
            title = "ℹ️ Information"

    color = colors.get(status, colors["Info"])

    send_discord_embed(message=message, title=title, status=status, color=color)


@task(retries=3, retry_delay_seconds=5, name="Prévoir avec le modèle")
def predict():
    logger = get_run_logger()
    try:
        response = requests.get(f"{FASTAPI_URL}/predict", timeout=5)
    except Exception as e:
        logger.error(f"❌ Erreur réseau pendant la prédiction : {e}")
        send_discord(f"Erreur réseau pendant la prédiction : {e}", status="Erreur", title="❌ Erreur de prédiction")
        raise

    # Si la réponse est 400, on considère qu'il n'y a pas assez de données / modèle
    if response.status_code == 400:
        data = response.json()
        logger.warning(f"⚠️ 400 Bad Request: {data.get('error')}")
        send_discord(f"Prédiction impossible : {data.get('error')}", status="Warning", title="⚠️ Prédiction impossible")
        return None

    # Pour tout autre code d’erreur HTTP >= 401, on lève pour déclencher le retry
    if response.status_code >= 401:
        logger.error(f"❌ Erreur HTTP {response.status_code} pendant la prédiction.")
        send_discord(f"Erreur HTTP {response.status_code} pendant la prédiction.", status="Erreur", title="❌ Erreur HTTP Prédiction")
        response.raise_for_status()

    # Enfin, cas 200 OK
    result = response.json()
    prediction = result.get("prediction")
    logger.info(f"✅ Prédiction : {prediction}")
    send_discord(f"Prédiction réussie : {prediction}", status="Succès", title="🎯 Prédiction effectuée")
    return prediction


@task(name="Générer le dataset")
def generate():
    logger = get_run_logger()
    try:
        response = requests.post(f"{FASTAPI_URL}/generate", timeout=5)
        response.raise_for_status()
        logger.info("📦 Dataset généré avec succès.")
        send_discord("Nouveau jeu de données généré avec succès.", status="Succès", title="🧬 Nouveau jeu de données")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du dataset : {e}")
        send_discord(f"Erreur lors de la génération du dataset : {e}", status="Erreur", title="🚨 Erreur génération dataset")
        raise e


@task(name="Réentraîner le modèle")
def retrain():
    logger = get_run_logger()
    try:
        response = requests.post(f"{FASTAPI_URL}/retrain", timeout=10)
        response.raise_for_status()
        logger.info("🔁 Modèle réentraîné avec succès.")
        send_discord("Le modèle a été réentraîné avec succès.", status="Succès", title="🔁 Réentraînement du modèle")
    except Exception as e:
        logger.error(f"Erreur lors du réentraînement : {e}")
        send_discord(f"Erreur lors du réentraînement : {e}", status="Erreur", title="🚨 Échec d'entraînement")
        raise e


@flow(name="Surveillance modèle ML")
def periodic_check():
    logger = get_run_logger()
    logger.info("⏳ Vérification du modèle en cours...")

    try:
        prediction = predict()
    except Exception:
        logger.warning("💥 Échec total de la prédiction après retries. Tentative de réentraînement...")
        send_discord("Échec total de la prédiction après retries. Tentative de réentraînement...", status="Erreur", title="💥 Échec de prédiction")
        generate()
        time.sleep(1)
        retrain()
        return

    if prediction == 0:
        logger.warning("⚠️ Mauvaise prédiction. Réentraînement nécessaire.")
        send_discord("⚠️ Mauvaise prédiction détectée. Réentraînement nécessaire.", status="Warning", title="⚠️ Réentraînement nécessaire")
        generate()
        time.sleep(1)
        retrain()
    else:
        logger.info("✅ Le modèle fonctionne correctement.")
        send_discord("Le modèle fonctionne correctement.", status="Succès", title="✅ Modèle stable")


if __name__ == "__main__":
    while True:
        periodic_check.with_options(flow_run_name="Surveillance")()
        time.sleep(10)