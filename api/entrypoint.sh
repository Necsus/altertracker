#!/bin/bash
# entrypoint.sh

set -e

echo "⏳ Attente de PostgreSQL..."

# Attente que PostgreSQL soit prêt
while ! nc -z localhost 5432; do
  sleep 1
done

echo "✅ PostgreSQL prêt."

echo "📦 Création des tables SQLAlchemy..."

python << END
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
END

echo "🚀 Démarrage de Flask..."
exec flask run --host=0.0.0.0