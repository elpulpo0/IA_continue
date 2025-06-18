# IA_Continue

Ce projet est une architecture modulaire regroupant une API **FastAPI** pour la génération de datasets et la prédiction via **MLflow**, un pipeline de traitement asynchrone orchestré avec **Prefect** pour l’automatisation des workflows, ainsi que des outils de monitoring et de surveillance (**Uptime Kuma**, **Grafana**, **Prometheus**, **cAdvisor**). Le tout est intégré et déployé facilement grâce à **Docker Compose**.

## Structure

```sh
# Partie Application
app/
├── Dockerfile
├── config/
|   └── logger.py                 # Configuration du logger
├── database.py                   # Configuration et gestion de la base de données SQLite
├── main.py                       # Point d'entrée : lancement de l'application FastAPI
├── requirements.txt              # Dépendances Python spécifiques à l'application FastAPI
├── db/
|   ├── data.db                   # Base de données SQLite utilisée pour stocker les datasets générés
|   └── mlruns.db                 # Base de données SQLite utilisée par MLflow pour suivre les expériences
├── routes.py                     # Définition des routes et endpoints de l'API FastAPI
└── tests/
    └── test_routes.py            # Tests unitaires et d’intégration des routes FastAPI

# Partie Pipeline Prefect
prefect/
├── Dockerfile
├── config/
|   └── logger.py                 # Configuration du logger
├── flow.py                       # Définition des flows et tâches Prefect (pipeline asynchrone)
├── requirements.txt              # Dépendances Python spécifiques au pipeline Prefect
└── webhook_disord.py             # Module pour l’envoi de notifications Discord (webhooks)

# Partie Monitoring
monitoring/
│── grafana/
│   └── dashboards/               # Fichiers json des dashboards pré-installés
│   └── provisionning/
│   │   └── dashboards/
│   │   │   └── dashboards.yml    # Configuration des dashboards pour Grafana
│   │   └── datasources/
│   │   │   └── datasources.yml   # Configuration des sources pour Grafana
│── prometheus/
│   └── alerts.yml                # Configuration des alertes pour Prometheus
│   └── prometheus.yml            # Configuration générale de Prometheus
└── uptime-kuma
    └── kuma.db                  # Configuration générale de Uptime Kuma (sera généré à la première utilsation de Kuma)

# Fichiers de configuration et utilitaires
.gitignore                        # Liste des fichiers et dossiers ignorés par Git
README.md                         # Documentation et informations générales du projet
docker-compose.yml                # Configuration des services Docker (FastAPI, Prefect, monitoring, etc.)
requirements.txt                  # Dépendances Python globales pour le développement (inclut app & prefect)
.env                              # Variables d’environnement confidentielles (ne pas partager)
```

## Utisation en production

**Copier et éditer le fichier .env**

```sh
cp .env_example .env
```

**Lancement via Docker**

```sh
docker compose up -d --build
```

## Services disponibles via Docker Compose

- **FastAPI** → http://localhost:8069
- **Prefect UI** → http://localhost:4200
- **Uptime Kuma** → http://localhost:3001
- **Grafana** → http://localhost:3000 (admin / admin)
- **Prometheus** → http://localhost:9090

**Configurez Kuma**

Visitez http://localhost:3001 et ajoutez le health check de l'API: http://api:8069/health ainsi qu'une notiofication Discord avec votre webhook.

## Installation pour usage en local

**Clone this repository**

```bash
git clone https://github.com/elpulpo0/IA_continue.git
```

**Create a virtual environnement**

```bash
python -m venv .venv
```

**Connect to the virtual environnement**

```bash
source .venv/Scripts/activate
```

**Upgrade pip and install librairies**

```bash
python.exe -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

**Copier et éditer le fichier .env**

```sh
cp .env_example .env
```

**Pour l'API**

```sh
cd app
uvicorn main:app --reload
```
Elle sera accessible à l’adresse : http://localhost:8000/docs

**Pour le pipeline Prefect**

```sh
cd prefect
prefect server start
```
L’interface web sera disponible sur : http://localhost:4200

**Lancer le flow (Toujours dans prefect)**

```sh
python flow.py
```

L'interface Kuma pour la configuration se trouve sur http://localhost:3001
