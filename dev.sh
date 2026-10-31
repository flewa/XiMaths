#!/usr/bin/env bash
# Lance XiMaths en local, en une commande : installe ce qui manque, prépare la base
# de démonstration, puis démarre l'API (port 8000) et le front (port 3000).
# Ctrl-C arrête les deux.
set -euo pipefail

cd "$(dirname "$0")"

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[x] $1 est introuvable : $2" >&2
    exit 1
  fi
}
need uv "installe-le depuis https://docs.astral.sh/uv/ (il installe Python tout seul)."
need npm "installe Node 24 depuis https://nodejs.org/."
need curl "installe curl avec le gestionnaire de paquets du système."

echo "[1/3] API : dépendances, base et données de démonstration"
(
  cd backend
  uv sync --quiet
  uv run python manage.py migrate --verbosity 0
  uv run python manage.py seed_demo
)

echo "[2/3] Front : dépendances"
if [ ! -d frontend/node_modules ]; then
  npm --prefix frontend install --no-audit --no-fund
fi

# Attend qu'une adresse réponde, 60 s au plus.
wait_for() {
  for _ in $(seq 1 60); do
    curl -s -o /dev/null "$1" && return 0
    sleep 1
  done
  echo "[x] $1 ne répond pas : regarde les messages ci-dessus." >&2
  return 1
}

echo "[3/3] Démarrage"
# À l'arrêt, tout le groupe de processus s'en va : uv, Django, npm et Next.
trap 'trap - EXIT INT TERM; kill 0 2>/dev/null' EXIT INT TERM
(cd backend && uv run python manage.py runserver 8000) &
wait_for http://127.0.0.1:8000/api/health
npm --prefix frontend run dev &
wait_for http://localhost:3000/

cat <<'EOF'

  XiMaths tourne sur http://localhost:3000
  Comptes de démo : lea (L1), yanis (PSI), camille (experte), moderateur (admin)
  Mot de passe : demo-ximaths-2026 · admin : http://localhost:8000/admin/
  Ctrl-C pour tout arrêter.

EOF
wait
