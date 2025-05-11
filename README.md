# uniquetracker
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

docker compose build
docker compose up -d


docker compose run --rm certbot renew
docker compose run --rm certbot renew --dry-run
0 3 * * * cd /home/tonuser/geekom/uniquetracker && docker compose run --rm certbot renew && docker compose restart web