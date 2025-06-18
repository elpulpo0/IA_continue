# Étape 1: Build de l'application
FROM node:alpine AS builder

WORKDIR /app

# Copier uniquement les fichiers de dépendances pour optimiser le cache
COPY package.json package-lock.json ./
RUN npm install

# Copier le reste des fichiers et construire l'application
COPY . .
RUN npm run build

# Étape 2: Serveur léger avec 'serve'
FROM node:alpine
WORKDIR /usr/share/app

# Installer 'serve' globalement
RUN npm install -g serve

# Copier les fichiers générés de la build dans le conteneur
COPY --from=builder /app/dist .

# Installer 'shadow' pour avoir useradd, et bash
RUN apk add --no-cache shadow bash

# Créer un utilisateur sans spécifier /bin/bash (utilise /bin/sh par défaut)
RUN useradd -m appuser

# Donner la propriété des fichiers à appuser
RUN chown -R appuser:appuser /usr/share/app

USER appuser

# Exposer le port 8081
EXPOSE 8081

# Lancer 'serve' avec le mode SPA (-s) sur le port 8081
CMD ["serve", "-s", "-l", "8081"]
