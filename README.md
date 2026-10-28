# XiMaths

Plateforme communautaire d'exercices de mathématiques du supérieur (L1 à M2, prépas MPSI, PCSI, PTSI, MP2I, MP, PC, PSI, PT) : on publie des exercices, on propose des solutions, et des pairs tirés au sort les relisent.

La conception complète (barème, détection de doublons, anti-triche, phasage) est dans le document [XiMaths — Proposition de développement](https://claude.ai/artifact/SFjJeg2DwwHuPvjJZ6MGcB). Les contenus publiés sont sous licence CC BY-SA 4.0.

## Structure

| Dossier ou fichier | Contenu |
| --- | --- |
| `backend/` | API Django 5.2 + Django Ninja. Apps : `accounts` (comptes, connexion Google, niveau de confiance), `catalog` (niveaux, chapitres), `content` (exercices, solutions, relectures, votes, tâches planifiées), `duplicates` (détection des doublons), `gamification` (ledger, barème, classements, badges, niveaux de confiance, séries et objectifs), `moderation` (signalements, anti-plagiat, sanctions, appels, questions de compréhension), `notifications`, `training` (chronométré et défi du jour) |
| `frontend/` | Next.js 16 (App Router), React 19, Tailwind 4, Markdown + KaTeX rendus côté serveur, éditeur CodeMirror 6. Design décrit dans `frontend/DESIGN-opencode.ai.md`, avec un mode sombre |
| `docker-compose.yml` | Développement : PostgreSQL 16 avec pgvector, Redis, et bge-m3 servi par Text Embeddings Inference |
| `docker-compose.prod.yml`, `Caddyfile` | Production : Caddy (HTTPS), PostgreSQL, Redis, l'API, le planificateur et le front |
| `.github/workflows/ci.yml` | Intégration continue : tests du backend, typage, lint, tests et construction du front |

## Prérequis

- [uv](https://docs.astral.sh/uv/) : il installe Python 3.12 tout seul.
- Node 24 (LTS). Node 20 n'est plus maintenu depuis avril 2026, et Next 16 demande au moins Node 20.9.
- Docker, facultatif en développement. Sans `DATABASE_URL`, le backend utilise SQLite (`backend/db.sqlite3`).

## Lancer en local

Backend, sur http://127.0.0.1:8000 :

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo          # comptes, exercices, solutions et un gabarit de défi
uv run python manage.py runserver 8000
```

Front, sur http://localhost:3000 :

```bash
cd frontend
npm install
npm run dev
```

- Comptes de démo : `camille` (experte), `relecteur1` à `relecteur3`, `lea`, `yanis`, et `moderateur`, qui a accès à l'admin. Leur mot de passe de développement est `DEMO_PASSWORD` dans `backend/content/management/commands/seed_demo.py`.
- Les emails s'affichent dans la console du backend.
- Le front relaie `/api` vers Django (`next.config.ts`) : session et CSRF fonctionnent sur la même origine.
- Évite `npm run build` pendant `npm run dev` : le serveur de dev voit passer les fichiers de la construction et peut servir une version périmée. En cas de souci, arrête-le, supprime `.next` et relance `npm run dev`.
- Documentation de l'API : http://127.0.0.1:8000/api/docs
- Back-office : http://127.0.0.1:8000/admin/, avec le compte `moderateur`.
- Avec PostgreSQL et les embeddings : `docker compose up -d`, puis copier `.env.example` dans `backend/.env` et lancer les commandes avec `uv run --env-file .env …`
- Les tâches planifiées se lancent à la main en développement : `uv run python manage.py run_jobs hourly` (ouvre aussi le défi du jour) et `run_jobs nightly`.

## Configuration

Tout passe par des variables d'environnement, décrites dans `.env.example` (développement) et `.env.prod.example` (production). Les services externes sont facultatifs : sans eux, le site fonctionne avec une solution de repli.

| Variable | Rôle | Sans elle |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL | SQLite |
| `REDIS_URL` | Cache partagé entre les workers, limitation de débit comprise | cache en mémoire, par processus |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Envoi réel, par le relais SMTP de Brevo | emails dans la console |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Connexion avec Google (OpenID Connect) | le bouton n'apparaît pas |
| `ACADEMIC_EXTRA_DOMAINS` | Domaines d'établissements reconnus en plus de la liste intégrée, séparés par des virgules | la liste intégrée seule |
| `EMBEDDINGS_URL` | Embeddings bge-m3 (E1, et E2 avec un LLM) | doublons détectés par MinHash seul |
| `ANTHROPIC_API_KEY`, `LLM_TIMEOUT` | Claude : résumés canoniques, avis sur les doublons, questions de compréhension | décisions et questions rédigées par les modérateurs |
| `SENTRY_DSN` | Suivi des erreurs (groupe de dépendances `prod`) | journaux seulement |
| `NEXT_PUBLIC_SITE_URL` | Adresse publique du site : plan du site, robots.txt, OpenGraph | `http://localhost:3000` |

## Comptes

- Inscription avec vérification de l'adresse par lien signé, connexion par pseudo ou email, limitation de débit.
- Connexion avec Google : un compte existant à la même adresse vérifiée est lié, sinon un compte est créé. L'adresse de retour à déclarer chez Google est `<site>/api/auth/google/callback`.
- Mot de passe oublié, changement de mot de passe, export des données (JSON) et suppression du compte depuis `/reglages`. Les contenus publiés restent, sans auteur.
- Réglages : niveau déclaré, tiers-temps, présence dans les classements, emails, résumé hebdomadaire, notification du défi du jour, thème clair, sombre ou système.
- Email académique, depuis `/reglages` : un lien signé, envoyé à une adresse d'université ou d'école, donne le badge « Étudiant vérifié ». Seuls le domaine et une empreinte (HMAC) sont gardés, pour qu'une adresse ne vérifie qu'un compte. Les domaines reconnus sont dans `backend/accounts/academic.py` ; `ACADEMIC_EXTRA_DOMAINS` en ajoute, et un modérateur peut aussi marquer un compte dans l'admin.

## Notifications

Dans l'application (`/notifications`) pour tout ce qui concerne le membre. Par email seulement pour ce qui le touche directement : retrait d'un contenu, sanction, appel tranché, solution en vérification, question de compréhension. Jamais d'email entre 22 h et 8 h : ils partent à 8 h. Résumé hebdomadaire le lundi, sur opt-in. Chaque email porte un lien de désinscription en un clic.

## Relecture par les pairs

- 3 relecteurs tirés au sort, anonymes et à l'aveugle. Relance à 48 h, réattribution à 72 h, sans pénalité.
- Relecture volontaire possible depuis `/relectures`, avec un poids de 0,5.
- Les solutions contestées (relecteurs en désaccord) sont tranchées par un expert ou un modérateur, sur `/arbitrages`.
- Une solution validée puis modifiée de plus de 20 % repart en relecture, pour un nouveau tour.
- L'auteur d'un exercice peut recommander une solution validée (+5 pour son auteur).

## Détection des doublons

À la publication, l'énoncé est comparé aux exercices publiés (document de conception, section « Détection IA des doublons ») :

- **Normalisation** : notations unifiées (`\R`, `ℝ` et `\mathbb{R}` ; `\le` et `\leqslant`…), variables renommées dans l'ordre d'apparition, constantes remplacées par `NUM` dans une version abstraite.
- **Signatures** : MinHash (128 permutations, shingles de 5 jetons) indexées en LSH ; l'embedding bge-m3 de l'énoncé (E1) si `EMBEDDINGS_URL` est défini ; avec un LLM en plus, l'embedding du résumé canonique (E2) écrit par Claude Haiku 5.5.
- **Bandes** : quasi-copie (J(F) ≥ 0,85), variante paramétrique (J(F′) ≥ 0,85, ou seules les constantes changent), très similaire (s ≥ 0,88), peut-être lié (s ≥ 0,80). Valeurs de départ, à calibrer.
- **Score** : s = 0,45 cos(E1) + 0,35 cos(E2) + 0,20 J(F). Sans E2 (pas de LLM, ou pendant la rédaction, car le résumé est calculé par la tâche nocturne), cos(E1) prend son poids.
- **Avis du LLM** : avec une clé, Claude Sonnet 5.5 qualifie chaque paire « quasi-copie » ou « très similaire » de la file (identique, variante, cas particulier, généralisation, même thème, différent), avec une justification d'une phrase. L'avis est mis en cache sur la paire et affiché dans l'admin ; un humain tranche toujours.

Pendant la rédaction, le panneau « Exercices proches » se met à jour. À la publication, une quasi-copie, une variante ou un exercice très similaire ouvre l'écran « Cet exercice existe peut-être déjà » : l'auteur dit si c'est le même, une variante, ou un exercice différent (publié, la paire part en file d'arbitrage). Aucune fusion n'est automatique, et une fusion s'annule.

```bash
uv run python manage.py scan_duplicates            # exercices publiés depuis 2 jours
uv run python manage.py scan_duplicates --reindex --all   # après un changement de normalisation ou de modèle
```

## Fil d'accueil et catalogue

Une seule page de 20 exercices, sans défilement infini : 60 % de Tendances, 25 % d'« À résoudre » (moins de 14 jours, moins de 2 solutions validées), 15 % d'exploration. Chaque exercice dit pourquoi il est là. Les scores sont logarithmiques : cent fois plus de solutions ne donnent qu'un score sept fois plus élevé. `/exercices` parcourt tout le catalogue : récents, populaires ou sans solution validée.

## Classements, badges et niveaux de confiance

- **Classements** (`/classements`) : hebdomadaires par niveau et global, du lundi 0 h au dimanche 23 h 59 (heure de Paris), plus un Panthéon au second plan. Les points comptent pour le niveau de l'exercice. Top 50, puis ta position avec 5 voisins de chaque côté ; filtre « mes pairs ». 24 h de consolidation pour annuler des points frauduleux.
- **Qui est classé** : les membres (niveau 1 ou plus), sans sanction d'exclusion en cours. Chacun peut masquer sa présence.
- **Badges** (`/badges`), critères publics : Premier pas, Validé !, Pionnier, Auteur, Relecteur fiable, Touche-à-tout, Élégance, Chasseur de doublons, Sous pression (5 défis validés), Régulier bronze, argent et or (4, 12 et 30 semaines d'objectif atteint), Étudiant vérifié (email académique confirmé).
- **Niveaux de confiance**, attribués automatiquement, jamais retirés automatiquement :
    - Membre : 7 jours et 30 points ;
    - Relecteur : 300 points, 5 solutions validées, aucune sanction depuis 90 jours ;
    - Expert : 1 500 points et 30 relectures concordantes à 80 % ou plus ;
    - Modérateur : nomination par le staff.

## Défi du jour

Un défi par niveau, chaque jour, sur `/defi`. Les modérateurs créent des gabarits dans l'admin (« Entraînement › Gabarits de défi ») : un exercice publié, un énoncé avec des paramètres (`{{a}}`), leurs valeurs possibles, et la réponse en fonction des paramètres (`sqrt(a)/b`). Le formulaire vérifie le gabarit et montre un exemple de tirage.

- **Fenêtre de 24 h**, de minuit à minuit ; 30 minutes (×1,33 avec un tiers-temps) ; **une seule tentative**, qu'abandonner consomme.
- **Énoncé tiré pour chacun** : partager sa réponse ne sert à rien. Les relecteurs voient l'énoncé tiré de l'auteur.
- **Barème** : 20 × m(d). 60 % dès que SymPy reconnaît la réponse, 40 % quand la justification est validée par les pairs. Bonus de rapidité jusqu'à ×1,25 ; chaque indication ouverte en retire 10 %. Les points comptent dans le classement de la semaine.
- **Règles de session classée** : le chrono ne s'arrête pas (onglet fermé compris, la session se reprend), pas de pause, collage externe désactivé et compté, IA interdite, sorties d'onglet comptées sans pénalité. Une tentative abandonnée onglet fermé est rendue par la tâche horaire.
- Les solutions des autres sont visibles à la fermeture du défi.

## Série et objectifs

Sur `/progression` :

- **Série hebdomadaire** : un objectif de 2 à 7 jours actifs par semaine. Un jour actif, c'est une tentative de solution, une relecture ou 15 minutes de chronomètre ; une connexion ne compte pas.
- **Deux jokers par mois**, appliqués d'eux-mêmes à une semaine manquée.
- **Mode examens ou vacances** : la série se met en pause, 4 semaines au plus.
- **Objectifs personnels** : « 10 exercices d'ici le 10 janvier » (éventuellement dans un chapitre) ou « 3 exercices chronométrés par semaine », avec une barre de progression.
- La régularité rapporte des badges, jamais de points. Le bilan de la semaine arrive le lundi, sur un ton neutre.

## Niveau de contributeur et carte de compétences

Sur `/progression` également :

- **Niveau de contributeur**, de 1 à 30, sur une courbe quadratique : le niveau n demande 20 (n − 1)² points (20 pour le niveau 2, 1 620 pour le 10, 16 820 pour le 30). Il suit le solde du ledger. Sur le profil public, il est masqué avec les points.
- **Carte de compétences**, visible de soi seul : dans chaque chapitre, la maîtrise (de 0 à 5) est la moyenne des difficultés de ses 5 exercices résolus les plus difficiles, une case vide comptant 0. Une solution avec l'aide de l'IA sur une idée compte pour moitié, une solution générée pas du tout ; un exercice et ses doublons fusionnés comptent une fois.
- **Prochain exercice** : dans chaque chapitre, un exercice publié ni écrit ni tenté, au plus près d'un cran au-dessus de la maîtrise, de son année d'études ou d'avant de préférence.

## Entraînement chronométré

Depuis la fiche d'un exercice : 15, 30, 45 ou 60 minutes, ou le temps conseillé. Non classé, documents autorisés, deux pauses. Le serveur fait foi : chaque sauvegarde (toutes les 10 s) fait avancer le chrono, et un onglet fermé l'arrête. Au rendu : réponse finale vérifiée par SymPy (grammaire restreinte, jamais de Python libre), justification envoyée en relecture, temps comparé à la médiane, auto-évaluation de la difficulté.

## Modération et intégrité

- **Signalements** : doublon, plagiat, erreur, contenu inapproprié, IA non déclarée. Un modérateur tranche dans l'admin, avec un motif transmis à l'auteur du contenu. Un signalement confirmé de doublon, plagiat ou erreur rapporte +3.
- **Comptes liés** (réciprocité des votes, ou à la main) : leurs interactions mutuelles sont neutralisées, sans sanction.
- **Anti-plagiat** : chaque solution est comparée aux solutions antérieures des autres auteurs (MinHash, Jaccard ≥ 0,7, 0,85 sous 400 caractères). Au-delà, elle est mise en vérification et l'auteur reçoit une question neutre ; un modérateur tranche.
- **Questions de compréhension** : sur une solution classée (défi) ou à fort enjeu (plus de 30 points), un score d'intégrité agrégé (ressemblance, collages et temps) déclenche une relecture de plus (≥ 0,4) ou une question sur sa propre solution (≥ 0,7). La question est rédigée par Claude Opus 5.5 si une clé est configurée, par un modérateur dans l'admin sinon. Le membre a 72 h pour l'ouvrir sur `/questions`, puis 5 minutes pour répondre. Un expert ou un modérateur évalue, sur `/arbitrages` ; le LLM peut préparer l'évaluation. Réussie : les points sont accordés, et 30 jours sans question. Sinon, la solution reste publiée sans ses points de classement, sans sanction. Une question tous les 14 jours au plus.
- **Sanctions**, toujours humaines et motivées, dans l'admin : avertissement, exclusion des classements (30 jours), suspension (7 jours), bannissement. Un compte suspendu peut se connecter pour faire appel, pas contribuer.
- **Appels** sous 14 jours, depuis `/decisions` : sanctions, retraits de contenu, plagiats confirmés. Un autre modérateur que l'auteur de la décision les examine, sous 7 jours, et motive sa réponse. Une décision annulée lève la sanction ou rétablit le contenu et ses points.

## Référencement

`/sitemap.xml` (pages publiques et exercices publiés, régénéré toutes les heures), `/robots.txt` (pages personnelles exclues), et sur chaque exercice une description tirée de l'énoncé, une adresse canonique (celle du canonique pour un doublon fusionné) et les balises OpenGraph.

## Tâches planifiées

`python manage.py run_jobs hourly`, `run_jobs nightly`, ou `run_jobs --loop` (le service `scheduler` de la production : toutes les heures, et la nuit à 3 h). Une tâche qui échoue est journalisée sans bloquer les suivantes.

- **Toutes les heures** : ouverture des défis du jour, rendu des tentatives abandonnées, relances et réattributions des relectures, fin des sanctions à durée, questions de compréhension (rédaction, délais, préévaluation), emails retenus pendant les heures calmes, résumé hebdomadaire du lundi.
- **La nuit** : bilan de la semaine écoulée (séries), doublons (résumés, scan, avis du LLM), promotions et badges, purges (notifications de plus de 6 mois, signaux d'intégrité tranchés depuis un an, sessions expirées).

## Production

```bash
cp .env.prod.example .env.prod      # puis remplir les secrets
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

- Caddy obtient le certificat HTTPS de `SITE_DOMAIN` et sert tout sur une seule origine : `/api`, `/admin` et `/static` vont à Django (gunicorn, fichiers statiques par whitenoise), le reste au front (Next.js en sortie autonome).
- Les migrations tournent une fois avant l'API et le planificateur.
- HSTS, cookies sécurisés, en-têtes de sécurité ; Redis pour le cache et la limitation de débit ; Sentry si `SENTRY_DSN` est défini.
- Embeddings : `--profile embeddings`, et `EMBEDDINGS_URL=http://embeddings` dans `.env.prod`.

## Tests

```bash
cd backend
uv run python manage.py test

cd frontend
npm test            # Vitest : utilitaires du front
npx tsc --noEmit
npm run lint
```

Le backend couvre le ledger et le barème, la relecture par les pairs (tours, délais, volontaires, arbitrages, révisions), les votes, l'authentification (Google compris), les notifications, la détection des doublons (avec E2 et l'avis du LLM simulés), les classements, les badges et les niveaux de confiance, le niveau de contributeur et la carte de compétences, le fil d'accueil, les signalements, l'anti-plagiat, les sanctions et appels, les questions de compréhension, l'entraînement chronométré, le défi du jour, les séries et objectifs, et les tâches planifiées. Aucun test n'appelle un service externe : Claude, Google et les embeddings sont simulés.

## Limites connues

- Les images Docker et la composition de production n'ont pas été construites ici (pas de Docker sur la machine de développement) : à vérifier au premier déploiement.
- Les appels à Claude sont testés avec un client simulé ; leur premier usage réel se fera avec la clé.
- Score d'intégrité : les empreintes IA de référence, la rupture de style et le classifieur du document ne sont pas encore mesurés ; leurs poids sont retirés et les autres renormalisés.
- Pas encore : épreuves classées (V2), photo de copie, PWA et Web Push.
