# Utiliser une image Python de base plus récente
FROM python:alpine

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Créer un utilisateur non-root
RUN adduser -D -s /bin/sh appuser

# Copier les fichiers requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application dans le conteneur
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/database
RUN mkdir -p /app/logs

# Changer les propriétaires des répertoires à l'utilisateur appuser
RUN chown -R appuser:appuser /app/database
RUN chown -R appuser:appuser /app/logs

# Assurer que les répertoires ont les bonnes permissions
RUN chmod -R 755 /app/database
RUN chmod -R 755 /app/logs

# Changer le propriétaire des fichiers de l'application
RUN chown -R appuser:appuser /app

# Utiliser l'utilisateur non-root pour exécuter l'application
USER appuser