#!/usr/bin/env bash
# Met XiMaths en ligne sur un serveur Ubuntu ou Debian neuf, en une commande, depuis le
# dossier du dépôt cloné :
#
#   sudo ./deploy/install.sh
#
# Le script installe Docker s'il manque, écrit .env.prod (secrets tirés au hasard, questions
# pour le domaine et l'envoi des emails), construit et démarre le site, crée le compte
# d'administration et programme une sauvegarde quotidienne de la base. On peut le relancer :
# il garde le .env.prod existant.
set -euo pipefail

cd "$(dirname "$0")/.."
COMPOSE=(docker compose -f docker-compose.prod.yml --env-file .env.prod)

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
fail() { printf '\n[x] %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "Lance le script avec sudo : sudo ./deploy/install.sh"

say "[1/6] Docker"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
docker compose version >/dev/null 2>&1 || fail "Docker Compose manque : installe le paquet docker-compose-plugin."

say "[2/6] Configuration (.env.prod)"
secret() { openssl rand -base64 64 | tr -dc 'A-Za-z0-9' | head -c "$1"; }
# Une valeur saisie, prête pour le remplacement de sed (|, & et \ gardent leur sens littéral).
literal() { printf '%s' "$1" | sed -e 's/[|&\\]/\\&/g'; }
if [ -f .env.prod ]; then
  echo "Déjà là : on le garde. Pour tout reprendre, supprime .env.prod et relance."
else
  read -rp "Domaine du site, sans https:// (par exemple ximaths.fr) : " domain
  [ -n "$domain" ] || fail "Il faut un domaine."
  echo
  echo "Emails (confirmation d'inscription, mots de passe oubliés) : relais SMTP de Brevo."
  echo "Identifiants dans Brevo : Paramètres › SMTP et API. Laisse vide pour le faire plus tard."
  read -rp "Adresse d'envoi (par exemple no-reply@$domain) : " from
  read -rp "Identifiant SMTP Brevo : " smtp_user
  read -rsp "Clé SMTP Brevo (rien ne s'affiche) : " smtp_key
  echo
  umask 077
  sed \
    -e "s|^SITE_DOMAIN=.*|SITE_DOMAIN=$(literal "$domain")|" \
    -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(secret 32)|" \
    -e "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$(secret 50)|" \
    -e "s|^EMAIL_HOST_USER=.*|EMAIL_HOST_USER=$(literal "$smtp_user")|" \
    -e "s|^EMAIL_HOST_PASSWORD=.*|EMAIL_HOST_PASSWORD=$(literal "$smtp_key")|" \
    -e "s|^DEFAULT_FROM_EMAIL=.*|DEFAULT_FROM_EMAIL=XiMaths <$(literal "${from:-no-reply@$domain}")>|" \
    .env.prod.example > .env.prod
  if [ -z "$smtp_key" ]; then
    # Sans relais, les emails partent dans le journal de l'API au lieu d'échouer.
    sed -i "s|^EMAIL_BACKEND=.*|EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend|" .env.prod
    echo "[!] Pas de relais SMTP : les inscriptions ne pourront pas être confirmées avant d'en ajouter un dans .env.prod."
  fi
  echo "Écrit : .env.prod (lisible par root seulement). Garde-en une copie à l'abri : il contient les secrets."
fi
domain=$(grep '^SITE_DOMAIN=' .env.prod | cut -d= -f2)

say "[3/6] Domaine"
ip=$(curl -fsS https://api.ipify.org || true)
resolved=$(getent ahostsv4 "$domain" | awk 'NR==1 {print $1}' || true)
if [ -n "$ip" ] && [ "$resolved" != "$ip" ]; then
  echo "[!] $domain pointe vers ${resolved:-rien}, et ce serveur a l'adresse $ip."
  echo "    Ajoute chez ton registraire un enregistrement A : $domain → $ip, puis relance ce script."
  echo "    Sans lui, le certificat HTTPS ne peut pas être obtenu."
  read -rp "Continuer quand même ? [o/N] " go
  [ "$go" = "o" ] || exit 1
else
  echo "$domain → $ip : bon."
fi
if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  ufw allow OpenSSH >/dev/null && ufw allow 80/tcp >/dev/null && ufw allow 443 >/dev/null
  echo "Pare-feu : SSH, 80 et 443 ouverts."
fi

say "[4/6] Construction et démarrage (quelques minutes la première fois)"
"${COMPOSE[@]}" build
if ! grep -q '^VAPID_PUBLIC_KEY=.\+' .env.prod; then
  # Clés des notifications push, créées par l'application elle-même.
  keys=$("${COMPOSE[@]}" run --rm --no-deps -T backend python manage.py generate_vapid_keys)
  sed -i '/^VAPID_PUBLIC_KEY=/d; /^VAPID_PRIVATE_KEY=/d' .env.prod
  printf '%s\n' "$keys" >> .env.prod
fi
"${COMPOSE[@]}" up -d
for _ in $(seq 1 60); do
  curl -fsS -o /dev/null "https://$domain/api/health" && break
  sleep 5
done
curl -fsS -o /dev/null "https://$domain/api/health" \
  || fail "Le site ne répond pas en HTTPS. Regarde : ${COMPOSE[*]} logs caddy backend"
echo "En ligne : https://$domain"

say "[5/6] Compte d'administration (modération : https://$domain/admin/)"
if "${COMPOSE[@]}" exec -T backend python manage.py shell -c \
  "from django.contrib.auth import get_user_model as m; import sys; sys.exit(0 if m().objects.filter(is_superuser=True).exists() else 1)"; then
  echo "Il y en a déjà un."
else
  "${COMPOSE[@]}" exec backend python manage.py createsuperuser
fi

say "[6/6] Sauvegarde quotidienne de la base"
root=$(pwd)
cat > /etc/cron.daily/ximaths-sauvegarde <<EOF
#!/bin/sh
# Copie de la base chaque nuit, gardée 14 jours (installée par deploy/install.sh).
set -e
# Les copies contiennent des données personnelles : root seulement.
umask 077
mkdir -p -m 700 /var/backups/ximaths
cd "$root"
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db \\
  sh -c 'pg_dump -U "\$POSTGRES_USER" "\$POSTGRES_DB"' | gzip > "/var/backups/ximaths/ximaths-\$(date +%F).sql.gz"
find /var/backups/ximaths -name 'ximaths-*.sql.gz' -mtime +14 -delete
EOF
chmod 755 /etc/cron.daily/ximaths-sauvegarde
echo "Chaque nuit dans /var/backups/ximaths (14 jours gardés). Pense à en copier une hors du serveur de temps en temps."

say "XiMaths est en ligne : https://$domain"
echo "Mise à jour après un changement du code : sudo ./deploy/update.sh"
