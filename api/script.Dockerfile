FROM python:3.11-slim

# Installer cron
RUN apt-get update && apt-get install -y cron

# Définir le dossier de travail
WORKDIR /api

# Copier les scripts Python
COPY . .

# Copier la crontab
COPY crontab.txt /etc/cron.d/my-cron

# Donner les droits nécessaires
RUN chmod 0644 /etc/cron.d/my-cron

# Enregistrer la crontab
RUN crontab /etc/cron.d/my-cron

# Script de démarrage pour cron
COPY cron/start-cron.sh /start-cron.sh
RUN chmod +x /start-cron.sh

CMD ["/start-cron.sh"]