FROM python:3.11-slim

# Installer cron
RUN apt-get update && apt-get install -y cron

# Définir le répertoire de travail
WORKDIR /api

# Copier les fichiers nécessaires
COPY . .

# Installer les dépendances (si besoin)
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Installer la crontab
RUN crontab crontab.txt

# Lancer cron en avant-plan pour Docker
CMD ["cron", "-f"]