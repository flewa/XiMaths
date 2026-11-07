#!/bin/sh
# Sauvegarde de XiMaths : la base et les photos des copies, gardées 14 jours dans
# /var/backups/ximaths. Lancée chaque nuit par /etc/cron.daily/ximaths-sauvegarde
# (installé par deploy/install.sh et deploy/update.sh). À la main :
#
#   sudo ./deploy/sauvegarde.sh
set -eu

cd "$(dirname "$0")/.."
# Les copies contiennent des données personnelles : root seulement.
umask 077
mkdir -p /var/backups/ximaths
chmod 700 /var/backups/ximaths
day=$(date +%F)
compose="docker compose -f docker-compose.prod.yml --env-file .env.prod"

# Les variables sont celles du conteneur de la base.
# shellcheck disable=SC2016
$compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "/var/backups/ximaths/ximaths-$day.sql.gz"
$compose exec -T backend tar -C /app/media -czf - . > "/var/backups/ximaths/photos-$day.tar.gz"
find /var/backups/ximaths \( -name 'ximaths-*.sql.gz' -o -name 'photos-*.tar.gz' \) -mtime +14 -delete
