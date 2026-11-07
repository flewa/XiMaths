#!/usr/bin/env bash
# Met en route la mesure d'audience (Umami, voir docker-compose.prod.yml), une fois :
#
#   sudo ./deploy/statistiques.sh
#
# Umami démarre avec un compte « admin » dont le mot de passe, « umami », est connu de tous :
# le script le remplace par un mot de passe tiré au hasard, gardé dans .env.prod. Il déclare
# aussi le site dans Umami et donne son identifiant au front, qui se met alors à compter les
# visites. On peut le relancer : il ne refait que ce qui manque.
set -euo pipefail

cd "$(dirname "$0")/.."
COMPOSE=(docker compose -f docker-compose.prod.yml --env-file .env.prod)

fail() { printf '\n[x] %s\n' "$*" >&2; exit 1; }
[ "$(id -u)" -eq 0 ] || fail "Lance le script avec sudo : sudo ./deploy/statistiques.sh"
[ -f .env.prod ] || fail "Pas de .env.prod : installe d'abord avec ./deploy/install.sh"

# Une ligne de .env.prod : sa valeur (vide si elle manque), ou la remplacer.
value() { grep "^$1=" .env.prod | tail -n 1 | cut -d= -f2- || true; }
set_value() {
  sed -i "/^$1=/d" .env.prod
  printf '%s=%s\n' "$1" "$2" >> .env.prod
}

domain=$(value SITE_DOMAIN)
[ -n "$domain" ] || fail "SITE_DOMAIN manque dans .env.prod."

echo "Démarrage d'Umami…"
docker buildx version >/dev/null 2>&1 || export COMPOSE_BAKE=false
"${COMPOSE[@]}" up -d umami
for _ in $(seq 1 60); do
  "${COMPOSE[@]}" exec -T umami curl -fsS -o /dev/null http://localhost:3000/api/heartbeat 2>/dev/null && break
  sleep 2
done
"${COMPOSE[@]}" exec -T umami curl -fsS -o /dev/null http://localhost:3000/api/heartbeat \
  || fail "Umami ne répond pas. Regarde : ${COMPOSE[*]} logs umami"

# Écrit avant d'être appliqué : une coupure en route ne le perd pas.
password=$(value UMAMI_ADMIN_PASSWORD)
if [ -z "$password" ]; then
  password=$(openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 24)
  set_value UMAMI_ADMIN_PASSWORD "$password"
fi

# L'API d'Umami, depuis son conteneur. Le mot de passe passe par l'entrée standard, pas par
# la ligne de commande (visible de tous dans la liste des processus).
read -r -d '' SETUP <<'JS' || true
let input = "";
for await (const chunk of process.stdin) input += chunk;
const { password, domain } = JSON.parse(input);

async function call(path, { token, body } = {}) {
  const response = await fetch(`http://localhost:3000/api${path}`, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json", ...(token && { Authorization: `Bearer ${token}` }) },
    body: body && JSON.stringify(body),
  });
  return { ok: response.ok, data: await response.json().catch(() => null) };
}
const login = (secret) => call("/auth/login", { body: { username: "admin", password: secret } });

let session = await login(password);
if (!session.ok) {
  const initial = await login("umami");
  if (!initial.ok) {
    console.error("Connexion à Umami refusée : le compte admin n'a ni le mot de passe de .env.prod ni celui de départ.");
    process.exit(1);
  }
  const changed = await call("/me/password", {
    token: initial.data.token,
    body: { currentPassword: "umami", newPassword: password },
  });
  if (!changed.ok) {
    console.error("Le mot de passe d'Umami n'a pas pu être changé :", JSON.stringify(changed.data));
    process.exit(1);
  }
  session = await login(password);
}
const token = session.data.token;

const websites = await call("/websites?pageSize=100", { token });
let website = websites.data?.data?.find((site) => site.domain === domain);
if (!website) {
  const created = await call("/websites", { token, body: { name: "XiMaths", domain } });
  if (!created.ok) {
    console.error("Le site n'a pas pu être déclaré dans Umami :", JSON.stringify(created.data));
    process.exit(1);
  }
  website = created.data;
}
console.log(website.id);
JS
website=$(printf '{"password": "%s", "domain": "%s"}' "$password" "$domain" \
  | "${COMPOSE[@]}" exec -T umami node --input-type=module -e "$SETUP") \
  || fail "La mise en route d'Umami a échoué (message ci-dessus)."

[ "$(value UMAMI_WEBSITE_ID)" = "$website" ] || set_value UMAMI_WEBSITE_ID "$website"
# Le front lit l'identifiant à son démarrage : Compose le recrée s'il a changé.
"${COMPOSE[@]}" up -d frontend
echo "Mesure d'audience en route : le site compte ses visites."

ip=$(curl -fsS https://api.ipify.org || true)
resolved=$(getent ahostsv4 "stats.$domain" | awk 'NR==1 {print $1}' || true)
if [ -n "$ip" ] && [ "$resolved" != "$ip" ]; then
  echo
  echo "[!] Pour ouvrir le tableau de bord, ajoute chez ton registraire un enregistrement A :"
  echo "    stats.$domain → $ip (comme pour www). Le certificat HTTPS suit tout seul."
fi
echo
echo "Tableau de bord : https://stats.$domain"
echo "Identifiant : admin"
echo "Mot de passe : sudo grep UMAMI_ADMIN_PASSWORD .env.prod"
