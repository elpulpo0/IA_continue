FROM python:3.13-alpine

# Installer les dépendances système nécessaires
RUN apk update && apk add --no-cache \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    python3-dev \
    build-base \
    linux-headers \
    libpq-dev

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances Python
COPY requirements.txt .

# Installer pip + requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8069"]
