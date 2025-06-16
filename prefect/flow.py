from prefect import flow, task
from prefect.logging import get_run_logger
import os
import time
from random import random
from webhook_disord import send_discord_embed

# Configuration
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")

@task(retries=2, retry_delay_seconds=1, name="Ma Tâche")
def check_random():
    logger_prefect = get_run_logger()
    num = random()
    logger_prefect.info(f"Numéro généré: {num}")

    if num < 0.8:
        raise ValueError(f"Le check a échoué, {num} est trop faible, nouvelle tentative..")
    elif num < 0.9:
        logger_prefect.warning(f"Le modèle doit être réentraîné ! {num} est trop faible")
        # send_discord_embed(f"WARNING! Le modèle doit être réentraîné ! {num} est trop faible")
        logger_prefect.info("Simulation d'entrainement")
    else:
        logger_prefect.info("Le modèle est stable.")

@flow(name="Mon Flow")
def periodic_check():
    logger_prefect = get_run_logger()
    logger_prefect.info("Vérification du modèle en cours...")
    state = check_random(return_state=True)
    if state.is_failed():
        logger_prefect.error("Le nombre de retry sans succès a été dépassé.")
        # send_discord_embed("ERROR! Le nombre de retry sans succès a été dépassé.")

if __name__ == "__main__":
    while True:
        periodic_check.with_options(flow_run_name="Mon Run")()
        time.sleep(10)
