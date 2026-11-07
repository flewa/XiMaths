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

avant=$(git rev-parse HEAD)
git pull --ff-only
# Sans buildx, Compose construit avec son propre moteur (voir install.sh).
docker buildx version >/dev/null 2>&1 || export COMPOSE_BAKE=false
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
# Caddy ne relit pas son Caddyfile tout seul, et « up » ne le redémarre pas : le conteneur
# verrait encore l'ancien fichier (www, en-têtes…).
if ! git diff --quiet "$avant" HEAD -- Caddyfile; then
  docker compose -f docker-compose.prod.yml --env-file .env.prod restart caddy
fi
# Exercices ajoutés à la rédaction depuis la dernière fois ; les autres ne bougent pas.
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python manage.py import_exercises
docker image prune -f >/dev/null
# Mesure d'audience pas encore en route : on la lance, une fois (voir deploy/statistiques.sh).
if ! grep -q '^UMAMI_WEBSITE_ID=.' .env.prod; then
  ./deploy/statistiques.sh || echo "[!] Mesure d'audience pas en route : relance sudo ./deploy/statistiques.sh"
fi
# La sauvegarde nocturne passe par deploy/sauvegarde.sh, qui garde aussi les photos des copies.
cat > /etc/cron.daily/ximaths-sauvegarde <<EOF
#!/bin/sh
# Sauvegarde nocturne de XiMaths (installée par deploy/update.sh) : voir deploy/sauvegarde.sh.
exec "$(pwd)/deploy/sauvegarde.sh"
EOF
chmod 755 /etc/cron.daily/ximaths-sauvegarde
echo "À jour."
