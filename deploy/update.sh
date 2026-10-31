#!/usr/bin/env bash
# Met le site à jour avec la dernière version du code, sans perdre de données :
#
#   sudo ./deploy/update.sh
#
# Les migrations passent avant le redémarrage de l'API (service « migrate »).
set -euo pipefail

cd "$(dirname "$0")/.."
[ "$(id -u)" -eq 0 ] || { echo "Lance le script avec sudo : sudo ./deploy/update.sh" >&2; exit 1; }
[ -f .env.prod ] || { echo "Pas de .env.prod : installe d'abord avec ./deploy/install.sh" >&2; exit 1; }

# Une sauvegarde juste avant, au cas où.
[ -x /etc/cron.daily/ximaths-sauvegarde ] && /etc/cron.daily/ximaths-sauvegarde

git pull --ff-only
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker image prune -f >/dev/null
echo "À jour."
