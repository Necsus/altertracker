#!/bin/bash
# entrypoint.sh

set -e

echo "⏳ Attente de PostgreSQL..."

# Attendre que le service PostgreSQL soit prêt
while ! nc -z db 5432; do
  sleep 1
done

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

echo "✅ PostgreSQL prêt."