#!/bin/sh
# Sauvegarde de XiMaths : la base, les photos des copies et la mesure d'audience, gardées
# 14 jours dans /var/backups/ximaths, et copiées sur une autre machine si SAUVEGARDE_DISTANTE
# est renseigné dans .env.prod. Lancée chaque nuit par /etc/cron.daily/ximaths-sauvegarde
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
# La mesure d'audience (Umami), si elle est en route : sa base, puis l'effacement des visites
# de plus de 25 mois, la durée que recommande la CNIL.
# shellcheck disable=SC2016
if $compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT datname FROM pg_database"' \
  | grep -qx umami; then
  # shellcheck disable=SC2016
  $compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" umami' | gzip > "/var/backups/ximaths/audience-$day.sql.gz"
  # shellcheck disable=SC2016
  $compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d umami -q -v ON_ERROR_STOP=1' <<'SQL'
DELETE FROM website_event WHERE created_at < now() - interval '25 months';
DELETE FROM event_data WHERE created_at < now() - interval '25 months';
DELETE FROM session_data WHERE created_at < now() - interval '25 months';
DELETE FROM session WHERE created_at < now() - interval '25 months';
SQL
fi
find /var/backups/ximaths \( -name 'ximaths-*.sql.gz' -o -name 'photos-*.tar.gz' -o -name 'audience-*.sql.gz' \) \
  -mtime +14 -delete

# Copie hors du serveur : sans elle, une panne du disque ou la perte du serveur emporte le site
# et ses sauvegardes. La destination se donne dans .env.prod, au format de rsync :
#   SAUVEGARDE_DISTANTE=utilisateur@autre-machine:/chemin/ximaths
# (connexion SSH par clé pour root, sans mot de passe). Le dossier distant devient le miroir
# de /var/backups/ximaths, donc garde lui aussi 14 jours.
remote=$(sed -n 's/^SAUVEGARDE_DISTANTE=//p' .env.prod | tail -n 1)
if [ -n "$remote" ]; then
  if ! command -v rsync >/dev/null 2>&1; then
    echo "[!] Sauvegarde distante impossible : rsync manque (apt install rsync)." >&2
  elif ! rsync -a --delete /var/backups/ximaths/ "$remote/"; then
    echo "[!] La copie des sauvegardes vers $remote a échoué : elles ne sont que sur ce serveur." >&2
  fi
fi
