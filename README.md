# uniquetracker
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

docker compose build
docker compose up -d

log cron
/home/necsus/certbot-renew.log