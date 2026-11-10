# XiMaths

Plateforme communautaire d'exercices de mathématiques du supérieur (L1 à M2, prépas MPSI, PCSI, PTSI, MP2I, MP, PC, PSI, PT) : on publie des exercices, on propose des solutions, et des pairs tirés au sort les relisent.

La conception complète (barème, détection de doublons, anti-triche, phasage) est dans le document [XiMaths — Proposition de développement](https://claude.ai/artifact/SFjJeg2DwwHuPvjJZ6MGcB). Les contenus publiés sont sous licence CC BY-SA 4.0.

## Voir l'application

Il faut [uv](https://docs.astral.sh/uv/) et Node 24. Depuis la racine du dépôt :

```bash
./dev.sh
```

Le script installe les dépendances, crée la base de démonstration (14 exercices de la L1 au M1 et en prépa, des solutions relues ou en relecture, les défis du jour ouverts), puis démarre l'API et le front. Ouvre ensuite http://localhost:3000 et connecte-toi avec `lea` (L1), `yanis` (PSI), `camille` (experte) ou `moderateur` (admin), mot de passe `demo-ximaths-2026`. Ctrl-C arrête tout.

Dans l'application de bureau Claude Code, `.claude/launch.json` décrit les deux serveurs pour l'aperçu intégré ; la base doit avoir été préparée une fois, par `./dev.sh` ou par les commandes ci-dessous.

## Structure

| Dossier ou fichier | Contenu |
| --- | --- |
| `backend/` | API Django 5.2 + Django Ninja. Apps : `accounts` (comptes, connexion Google, niveau de confiance), `catalog` (niveaux, chapitres), `content` (exercices, solutions, relectures, votes, tâches planifiées), `duplicates` (détection des doublons), `gamification` (ledger, barème, classements, badges, niveaux de confiance, séries et objectifs), `moderation` (signalements, sanctions, appels, questions de compréhension), `notifications`, `training` (chronométré et défi du jour) |
| `frontend/` | Next.js 16 (App Router), React 19, Tailwind 4, Markdown + KaTeX rendus côté serveur, éditeur CodeMirror 6. Design : barre latérale, titres dans la police des formules (Computer Modern, via KaTeX), un seul accent corail ; sombre par défaut, clair au choix (jetons dans `src/app/globals.css`) |
| `dev.sh` | Lancement local en une commande : dépendances, base de démonstration, API et front |
| `deploy/` | Mise en ligne sur un serveur (`install.sh`), mises à jour (`update.sh`), sauvegarde (`sauvegarde.sh`) et mesure d'audience (`statistiques.sh`) |
| `marketing/tiktok/` | Vidéos TikTok en Remotion : scripts, captures de l'application, voix off ElevenLabs ([mode d'emploi](marketing/tiktok/README.md)) |
| `docker-compose.yml` | Développement : PostgreSQL 16 avec pgvector, Redis, et bge-m3 servi par Text Embeddings Inference |
| `docker-compose.prod.yml`, `Caddyfile` | Production : Caddy (HTTPS), PostgreSQL, Redis, l'API, le planificateur, le front et la mesure d'audience (Umami) |
| `.github/workflows/ci.yml` | Intégration continue : tests du backend, typage, lint, tests et construction du front |

## Prérequis

- [uv](https://docs.astral.sh/uv/) : il installe Python 3.12 tout seul.
- Node 24 (LTS). Node 20 n'est plus maintenu depuis avril 2026, et Next 16 demande au moins Node 20.9.
- Docker, facultatif en développement. Sans `DATABASE_URL`, le backend utilise SQLite (`backend/db.sqlite3`).

## Lancer en local

`./dev.sh` fait tout ce qui suit. Pour lancer chaque partie à la main :

Backend, sur http://127.0.0.1:8000 :

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo          # comptes, exercices, solutions, défis du jour ouverts
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
- Documentation de l'API : http://127.0.0.1:8000/api/docs (en développement seulement ; elle n'est pas servie en production)
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
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` | Notifications Web Push (clés créées par `manage.py generate_vapid_keys`) | pas de push, le réglage n'apparaît pas |
| `ACADEMIC_EXTRA_DOMAINS` | Domaines d'établissements reconnus en plus de la liste intégrée, séparés par des virgules | la liste intégrée seule |
| `EMBEDDINGS_URL` | Embeddings bge-m3 (E1, et E2 avec un LLM) | doublons détectés par MinHash seul |
| `ANTHROPIC_API_KEY`, `LLM_TIMEOUT` | Claude : résumés canoniques, avis sur les doublons, questions de compréhension (qui lisent les photos de la copie) | décisions et questions rédigées par les modérateurs |
| `SENTRY_DSN` | Suivi des erreurs (groupe de dépendances `prod`) | journaux seulement |
| `NEXT_PUBLIC_SITE_URL` | Adresse publique du site : plan du site, robots.txt, OpenGraph | `http://localhost:3000` |

## Comptes

- Inscription avec vérification de l'adresse par lien signé, connexion par pseudo ou email, limitation de débit.
- Connexion avec Google : un compte existant à la même adresse vérifiée est lié, sinon un compte est créé. L'adresse de retour à déclarer chez Google est `<site>/api/auth/google/callback`.
- Mot de passe oublié, changement de mot de passe, export des données (JSON) et suppression du compte depuis `/reglages`. Les contenus publiés restent, sans auteur.
- Réglages : niveau déclaré, présence dans les classements, emails, résumé hebdomadaire, notification du défi du jour, thème clair, sombre ou système.
- Email académique, depuis `/reglages` : un lien signé, envoyé à une adresse d'université ou d'école, donne le badge « Étudiant vérifié ». Seuls le domaine et une empreinte (HMAC) sont gardés, pour qu'une adresse ne vérifie qu'un compte. Les domaines reconnus sont dans `backend/accounts/academic.py` ; `ACADEMIC_EXTRA_DOMAINS` en ajoute, et un modérateur peut aussi marquer un compte dans l'admin.

## Notifications

Dans l'application (`/notifications`) pour tout ce qui concerne le membre. Par email seulement pour ce qui le touche directement : retrait d'un contenu, sanction, appel tranché, question de compréhension ; et, pour l'équipe, les copies qui attendent une correction depuis plus de 3 jours. Jamais d'email entre 22 h et 8 h : ils partent à 8 h. Résumé hebdomadaire le lundi, sur opt-in. Chaque email porte un lien de désinscription en un clic.

**PWA et Web Push.** XiMaths s'installe sur l'écran d'accueil (manifeste, icônes ; sur iPhone et iPad, l'installation ouvre aussi le push). Les notifications push s'activent appareil par appareil dans `/reglages`, sur opt-in :

- une par jour au plus, jamais entre 22 h et 8 h ; plusieurs en attente partent en un seul message qui les résume ;
- seulement relecture attribuée ou en attente, solution validée ou à compléter, exercice résolu, question de compréhension, défi du jour (s'il est demandé) et bilan de la semaine ;
- le serveur n'envoie qu'aux services de push des navigateurs (Google, Mozilla, Apple, Microsoft) ; un abonnement révoqué est supprimé, et un navigateur partagé passe au compte qui l'active ;
- le service worker (`frontend/public/sw.js`) n'affiche que les notifications, sans cache hors ligne.

Clés VAPID : `uv run python manage.py generate_vapid_keys`, à copier dans `.env` ou `.env.prod`. Sans elles, le réglage n'apparaît pas.

## Relecture par les pairs

- **Les solutions sont privées.** Une copie n'est vue que de son auteur, de ses relecteurs et de la modération, même validée ; le site n'affiche que le nombre de solutions envoyées. Pas de vote de solution.
- **Copie modèle** (la seule exception) : l'auteur coche une case d'accord, à l'envoi ou plus tard ; l'équipe choisit une copie validée par exercice, depuis la page de l'exercice ; elle est montrée sans nom aux membres qui ont envoyé leur propre copie, quand ils décident de l'ouvrir. Une copie envoyée après l'avoir ouverte peut être validée mais ne rapporte pas de points. L'accord se retire à tout moment, et prend fin avec le compte.
- 3 relecteurs tirés au sort, anonymes et à l'aveugle. Relance à 48 h, réattribution à 72 h, sans pénalité ; un tirage incomplet (pas assez de relecteurs possibles) est complété dès que possible.
- Chaque relecteur laisse un verdict et un **commentaire obligatoire** : c'est la seule correction que reçoit l'auteur. Il la lit dès qu'elle arrive, et en est prévenu par une notification (« Ta copie a été relue », 1 sur 3, 2 sur 3).
- **Consensus** : une fois toutes les relectures tirées au sort rendues, la copie est validée si tous les relecteurs la jugent juste (« correcte » ou « correcte avec lacunes »). Elle rapporte alors ses points ; sinon elle est à reprendre, et ne rapporte rien. Une copie envoyée ne rapporte rien en soi. Les relecteurs de la majorité gagnent leurs points de relecture.
- Relecture volontaire possible depuis `/relectures` ; son verdict compte dans le consensus.
- **Le filet : l'équipe du site.** Une relecture d'un membre de l'équipe (staff ou modérateur) vaut décision, sans attendre les autres : la copie est validée ou à reprendre aussitôt. Sur `/relectures`, l'équipe voit toutes les copies en attente, les plus anciennes d'abord. Chaque jour, elle est prévenue (notification et email) des copies en relecture depuis plus de 72 heures. Tant que les relecteurs manquent, aucune copie ne reste ainsi sans réponse.
- Une solution validée puis modifiée de plus de 20 % repart en relecture, pour un nouveau tour.

## Photo de copie

Une solution est toujours la copie manuscrite, en photos : rien ne se tape, ni rédaction ni réponse finale, en libre comme en temps limité. Sur l'ordinateur, « Depuis mon téléphone » affiche un QR code ; le téléphone qui le scanne ouvre `/photos/<jeton>` et y photographie les pages, sans se connecter (le jeton suffit, 30 minutes, prolongeables). Les photos apparaissent sur l'ordinateur au fur et à mesure, et partent en relecture avec la solution ; une révision envoie de nouvelles photos, qui remplacent les précédentes. Sur un téléphone, on ajoute les photos directement. Les relecteurs voient la réponse attendue de l'exercice (en défi, celle des valeurs tirées) pour vérifier vite le résultat. Trois pages au plus, 10 Mo chacune ; le serveur les redresse, les réduit à 2 000 px et les réencode en JPEG, ce qui efface leurs métadonnées. Elles sont servies par l'API, qui vérifie qui les demande (`content/photos.py`) : l'auteur, ses relecteurs, les évaluateurs de sa question de compréhension et les modérateurs ; personne d'autre, même une fois la solution validée. Une photo jamais jointe est effacée au bout d'un jour. Les photos sont dans le volume Docker `media`, sauvegardé chaque nuit avec la base.

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

## Interface

- **Accueil d'un membre** : sa semaine en sept cases, le défi du jour de son groupe de niveaux présenté comme un énoncé de manuel, puis ce qui l'attend (relectures à rendre, prochain exercice tiré de la carte de compétences, notifications non lues). Un visiteur voit la promesse, un bouton d'inscription et les trois étapes du site.
- **Mobile et tablette** (sous 1 024 px) : barre d'onglets en bas d'écran, à portée du pouce (Fil, Parcourir, Publier, Défi, Moi), masquée pendant une session chronométrée ; en-tête réduit au logo, aux notifications et au menu.
- **Accessibilité** : contrastes d'au moins 4,5:1 (marqueurs d'état, textes sur la surface sombre, indications des champs), anneau de focus de 2 px sur toutes les surfaces, lien « Aller au contenu », cibles tactiles d'au moins 24 px, onglets qui ramènent l'onglet actif dans la vue.

## Titres d'exercices

Un titre peut contenir des formules entre `$…$` (« Reste de `$3^{100}$` modulo 7 »), rendues par KaTeX partout où il s'affiche (`MathText`). Pour l'onglet du navigateur, Google, les partages, les notifications et les emails, `plain_math` (backend) en écrit une version texte : « Reste de 3¹⁰⁰ modulo 7 » (champ `title_text` de l'API). Un titre dont une formule n'est pas fermée, ou qui utilise une commande interdite, est refusé.

## Fil d'accueil et catalogue

Une seule page de 20 exercices, sans défilement infini : 60 % de Tendances, 25 % d'« À résoudre » (moins de 14 jours, moins de 2 solutions validées), 15 % d'exploration. Les scores sont logarithmiques : cent fois plus de solutions ne donnent qu'un score sept fois plus élevé. Chaque exercice affiche son état, pas la raison de sa présence : « Tendance », « Nouveau » (publié depuis moins de 7 jours), et le nombre de solutions validées, en gris.

Sur l'accueil, des onglets (`?vue=`) passent du fil aux vues triées : sans solution, tendance (score T), nouveaux. Connecté, l'accueil a deux colonnes sur grand écran : le défi du jour et les exercices, puis « Ta semaine », « À faire » et « Revoir le cours » (rappels publiés proches du fil) ; sur téléphone, une seule colonne. `/exercices` parcourt tout le catalogue : récents, populaires ou sans solution validée, et la recherche (`?q=`) y cherche chaque mot dans le titre, l'énoncé et les chapitres, sans tenir compte de la casse (les accents comptent).

## Niveaux et filières

Vingt niveaux, rangés en trois familles dans les menus : université (L1 à M2), prépas scientifiques (MPSI, MP2I, PCSI, PTSI, BCPST 1, MP, MPI, PC, PSI, PT, BCPST 2) et prépas ECG et B/L (deux années chacune). Les exercices de la rédaction rattachés aux filières BCPST, ECG et B/L sont listés à la main dans `backend/content/editorial/filieres.py`, d'après leurs programmes ; ceux de MP vont aussi en MPI. `import_exercises` ajoute ces niveaux aux exercices déjà publiés, sans jamais en retirer.

## Page d'un exercice

- **Statistiques** : combien de personnes l'ont lu, ont envoyé une copie, l'ont réussi, avec la part des lecteurs. Un membre compte une fois (`ExerciseRead`), un visiteur une fois par navigateur (liste gardée dans son navigateur, sans cookie ni identifiant).
- **Partage** : WhatsApp, Facebook, X, Pinterest, email, menu de partage du téléphone, copie du lien. De simples liens : aucun script tiers.
- **Questions et remarques** : un fil public par exercice, écrit une fois connecté, avec des réponses sur un niveau. On n'y donne pas la solution. Chacun retire ses messages, l'équipe retire ceux qui n'ont pas leur place, tout membre peut signaler un message (l'équipe est prévenue au premier signalement).

## Classements, badges et niveaux de confiance

- **Classements** (`/classements`) : hebdomadaires par niveau et global, du lundi 0 h au dimanche 23 h 59 (heure de Paris), plus un Panthéon au second plan. Les points comptent pour le niveau de l'exercice. Top 50, puis ta position avec 5 voisins de chaque côté ; filtre « mes pairs ». 24 h de consolidation pour annuler des points frauduleux.
- **Qui est classé** : les membres (niveau 1 ou plus), sans sanction d'exclusion en cours. Chacun peut masquer sa présence.
- **Badges** (`/badges`), critères publics : Premier pas, Validé !, Pionnier, Auteur, Relecteur fiable, Touche-à-tout, Élégance, Chasseur de doublons, Sous pression (5 défis validés), Régulier bronze, argent et or (4, 12 et 30 semaines d'objectif atteint), Étudiant vérifié (email académique confirmé).
- **Niveaux de confiance**, attribués automatiquement, jamais retirés automatiquement :
    - Membre : 7 jours et 30 points ;
    - Relecteur : 50 points, 2 solutions validées, aucune sanction depuis 90 jours (seuil bas exprès : il faut des relecteurs pour corriger les copies, et des copies corrigées pour devenir relecteur) ;
    - Expert : 1 500 points et 30 relectures concordantes à 80 % ou plus ;
    - Modérateur : nomination par le staff.

## Défi du jour

Chaque jour, sur `/defi`, un défi par groupe de niveaux : 1re année (L1 et sup), 2e année (L2 et spé), L3, master. Le défi porte le niveau de l'exercice tiré, pour lequel comptent ses points ; un gabarit ne revient pas dans son groupe avant une semaine, s'il y a le choix. Les modérateurs créent des gabarits dans l'admin (« Entraînement › Gabarits de défi ») : un exercice publié, un énoncé avec des paramètres (`{{a}}`), leurs valeurs possibles, et la réponse en fonction des paramètres (`sqrt(a)/b`). Le formulaire vérifie le gabarit et montre un exemple de tirage.

- **Fenêtre de 24 h**, de minuit à minuit ; 30 minutes ; **une seule tentative**, qu'abandonner consomme.
- **Énoncé tiré pour chacun** : partager sa réponse ne sert à rien. Les relecteurs voient l'énoncé tiré de l'auteur et la réponse attendue pour ses valeurs.
- **Copie manuscrite** : le QR code s'affiche au départ ; les photos (3 au plus) doivent arriver avant la fin du temps, avec 60 s de grâce, après quoi le dépôt ferme et la session est rendue avec ce qui est arrivé.
- **Barème** : 20 × m(d), gagnés quand la copie est validée par les pairs : plus de correction automatique. Bonus de rapidité jusqu'à ×1,25 ; chaque indication ouverte en retire 10 %. Les points comptent dans le classement de la semaine.
- **Règles de session classée** : le chrono ne s'arrête pas (onglet fermé compris, la session se reprend), pas de pause, IA interdite, sorties d'onglet comptées sans pénalité. Une tentative abandonnée onglet fermé est rendue par la tâche horaire.
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

Depuis la fiche d'un exercice : 15, 30, 45 ou 60 minutes, ou le temps conseillé. Non classé, documents autorisés, deux pauses. Le serveur fait foi : un signe de vie toutes les 10 s fait avancer le chrono, et un onglet fermé l'arrête. La copie est manuscrite : le QR code s'affiche au départ, et les photos doivent arriver avant la fin du temps, avec 60 s de grâce. Au rendu : copie envoyée en relecture, temps comparé à la médiane, auto-évaluation de la difficulté. Le vérificateur SymPy (`training/answers.py`, grammaire restreinte) ne sert plus qu'à valider les réponses et les gabarits de la rédaction, qu'on montre aux relecteurs.

## Modération et intégrité

- **Signalements** : doublon, plagiat, erreur, contenu inapproprié, IA non déclarée. Un modérateur tranche dans l'admin, avec un motif transmis à l'auteur du contenu. Un signalement confirmé de doublon, plagiat ou erreur rapporte +3.
- **Comptes liés** (réciprocité des votes, ou à la main) : leurs interactions mutuelles sont neutralisées, sans sanction.
- **Plagiat d'une copie** : les copies sont des photos, il n'y a pas de texte à comparer. C'est le relecteur qui le signale (« Signaler cette copie », sur `/relectures`) ; un modérateur tranche. Les plagiats confirmés par l'ancienne détection automatique restent visibles de leur auteur, qui peut faire appel.
- **Questions de compréhension** : sur une solution classée (défi) ou à fort enjeu (plus de 30 points), un score d'intégrité (un défi rendu bien plus vite que les autres) déclenche une relecture de plus (≥ 0,4) ou une question sur sa propre solution (≥ 0,7). La question est rédigée par Claude Opus 5.5 si une clé est configurée, par un modérateur dans l'admin sinon. Le membre a 72 h pour l'ouvrir sur `/questions`, puis 5 minutes pour répondre. Un expert ou un modérateur évalue, sur `/evaluations` ; le LLM peut préparer l'évaluation. Réussie : les points sont accordés, et 30 jours sans question. Sinon, la solution reste publiée sans ses points de classement, sans sanction. Une question tous les 14 jours au plus.
- **Sanctions**, toujours humaines et motivées, dans l'admin : avertissement, exclusion des classements (30 jours), suspension (7 jours), bannissement. Un compte suspendu peut se connecter pour faire appel, pas contribuer.
- **Appels** sous 14 jours, depuis `/decisions` : sanctions, retraits de contenu, plagiats confirmés. Un autre modérateur que l'auteur de la décision les examine, sous 7 jours, et motive sa réponse. Une décision annulée lève la sanction ou rétablit le contenu et ses points.

## Rappels de cours

Fiches de cours de prépa, sup et spé (`backend/courses/notes/sup/` et `spe/`, un fichier Markdown + LaTeX par fiche, avec un en-tête titre, programmes, ordre et notion du site). `import_exercises` les importe aussi (`import_course_notes` seul sinon) : elles arrivent **en brouillon**, visibles de l'équipe seulement (comptes `is_staff`), sur `/rappels`. Un admin relit chaque fiche sur le site et la publie d'un bouton ; publiée, elle est visible de tous, proposée sur la page de sa notion et listée dans le plan du site. Une fiche dont le texte change dans le dépôt repasse en brouillon, pour être relue de nouveau.

Garde-fous : chaque formule passe dans KaTeX (`src/lib/course-notes.test.ts`), les en-têtes et notions sont vérifiés côté serveur (`courses/tests.py`). Conventions d'écriture : notations définies en tête de fiche (« Cadre et notations »), énoncés complets dans des encadrés (`> **Théorème (nom).** …`), `]{-}r, r[` pour un intervalle ouvert à borne négative, pas de tableau Markdown (non rendu).

## Référencement

- **Pages d'entrée** par niveau (`/niveaux/mpsi`), par chapitre (`/chapitres/algebre-lineaire`) et par notion (`/chapitres/series-entieres`) : ce que tapent les élèves (« exercices MPSI », « exercices de séries entières »), avec un texte d'introduction propre à chacune (`src/lib/seo-pages.ts`). Les 38 notions sont des sous-chapitres (`Topic` avec un parent, migration `catalog/0004_notions`) ; choisir une notion range aussi l'exercice dans son chapitre, et la carte de compétences reste par chapitre. Une notion sans exercice est en `noindex` et hors du plan du site.
- **Maillage interne** : chaque exercice lie ses chapitres et notions et propose six « exercices proches » (`/api/exercises/<id>/related` : même notion d'abord, puis même chapitre, au même niveau de préférence) ; chaque chapitre liste ses notions, chaque notion ses voisines, chaque niveau les notions qu'on y travaille.
- **Balises** : sur chaque page publique, un titre parlant (« Intégrales de Wallis : exercice de calcul intégral (MPSI) », la notion avant le chapitre), une description qui dit la notion, les niveaux, le début de l'énoncé et le nombre d'indications (formules et matrices en texte lisible), une adresse canonique (le catalogue filtré renvoie à la page du niveau, un doublon fusionné à son canonique), l'image de partage `app/opengraph-image.png`. Pages personnelles, publication, chronomètre et profils en `noindex`.
- **Données structurées** : nom du site et logo (WebSite, Organization) sur l'accueil, fil d'Ariane (BreadcrumbList) sur les pages d'entrée et les exercices (chapitre › notion › exercice), ressource pédagogique (LearningResource) sur chaque exercice. Google a arrêté en 2026 les résultats enrichis « exercices » : il n'y a pas de balisage qui les rende.
- **Titres des exercices de la rédaction** : ils nomment l'objet (« Reste de 3¹⁰⁰ modulo 7 » plutôt que « Une puissance modulo 7 »), avec de vrais exposants Unicode. Un titre changé garde l'ancien dans `former_titles` : `import_exercises` retrouve l'exercice publié, le renomme et met à jour ses chapitres et notions, sans le recréer.
- **`/sitemap.xml`** (pages fixes, pages d'entrée et exercices publiés, construit à chaque lecture) et **`/robots.txt`**. `www.` renvoie vers l'adresse sans `www` (Caddy).
- **À faire une fois en ligne** : déclarer le domaine dans Google Search Console (propriété de type domaine, vérifiée par un enregistrement TXT chez le registraire), y soumettre `https://<domaine>/sitemap.xml`, puis importer le site dans Bing Webmaster Tools depuis Search Console.

## Tâches planifiées

`python manage.py run_jobs hourly`, `run_jobs nightly`, ou `run_jobs --loop` (le service `scheduler` de la production : toutes les heures, et la nuit à 3 h). Une tâche qui échoue est journalisée sans bloquer les suivantes.

- **Toutes les heures** : ouverture des défis du jour, rendu des tentatives abandonnées, relances et réattributions des relectures, fin des sanctions à durée, questions de compréhension (rédaction, délais, préévaluation), emails et notifications push retenus pendant les heures calmes, résumé hebdomadaire du lundi.
- **La nuit** : bilan de la semaine écoulée (séries), doublons (résumés, scan, avis du LLM), promotions et badges, purges (notifications de plus de 6 mois, signaux d'intégrité tranchés depuis un an, sessions expirées).

## Production

### Mettre en ligne

Il faut :

- un serveur Linux (Ubuntu 24.04 ou Debian 12) avec 4 Go de mémoire, de préférence hébergé dans l'Union européenne (Hetzner, OVHcloud, Scaleway) ;
- un nom de domaine, dont l'enregistrement A pointe vers l'adresse IP du serveur ;
- un compte [Brevo](https://www.brevo.com/) pour les emails (inscriptions, mots de passe oubliés), avec le domaine authentifié (SPF et DKIM) pour ne pas finir en indésirables.

Sur le serveur, en root (`sudo -i`) :

```bash
git clone https://github.com/flewa/XiMaths.git /opt/ximaths
cd /opt/ximaths
./deploy/install.sh
```

Le script installe Docker s'il manque, écrit `.env.prod` (secrets tirés au hasard, questions pour le domaine et Brevo), vérifie que le domaine pointe vers le serveur, construit et démarre le site, publie le stock d'exercices de la rédaction (`backend/content/editorial/`, un fichier par lot, sous le compte « XiMaths »), crée le compte d'administration et programme une sauvegarde chaque nuit de la base et des photos de copies (`deploy/sauvegarde.sh`, dans `/var/backups/ximaths`, 14 jours gardés). Le site est alors en ligne en HTTPS ; la modération se fait sur `/admin/`.

Mise à jour après un changement du code (sauvegarde, `git pull`, reconstruction, migrations, exercices ajoutés à la rédaction) :

```bash
cd /opt/ximaths && ./deploy/update.sh
```

Restaurer une sauvegarde :

```bash
gunzip -c /var/backups/ximaths/ximaths-AAAA-MM-JJ.sql.gz | docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db psql -U ximaths ximaths
```

Et les photos des copies, du même jour :

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend tar -C /app/media -xzf - < /var/backups/ximaths/photos-AAAA-MM-JJ.tar.gz
```

Copier les sauvegardes hors du serveur (sans cela, une panne du disque emporte le site et ses sauvegardes) : ajouter dans `.env.prod` une destination au format de rsync, par exemple `SAUVEGARDE_DISTANTE=utilisateur@autre-machine:/chemin/ximaths`. Il faut `rsync` sur le serveur et une connexion SSH par clé pour root. Chaque nuit, le dossier distant devient le miroir de `/var/backups/ximaths`.

Être prévenu d'une panne : faire surveiller `https://<SITE_DOMAIN>/api/health` par un service de surveillance (UptimeRobot, Better Stack…), et renseigner `SENTRY_DSN` pour recevoir les erreurs du serveur.

Mentions légales : l'éditeur, l'adresse de contact et l'hébergeur sont dans `frontend/src/lib/legal.ts`.

### Mesure d'audience

[Umami](https://umami.is/) compte les visites : sur ce serveur, sans cookie, sans lien avec les comptes, les robots écartés. Le tableau de bord (visiteurs du jour, de la semaine, en ce moment, pages vues, provenances, appareils, pays) est sur `https://stats.<SITE_DOMAIN>`. Il faut pour lui un enregistrement DNS `stats` (A vers le serveur), comme pour `www`.

`install.sh` le met en route ; sur un serveur déjà installé, `update.sh` le fait à sa première passe, ou à la main :

```bash
sudo ./deploy/statistiques.sh
```

Le script remplace le mot de passe de départ du compte `admin` d'Umami (« umami », connu de tous) par un mot de passe tiré au hasard, gardé dans `.env.prod` (`sudo grep UMAMI_ADMIN_PASSWORD .env.prod`), déclare le site dans Umami et passe son identifiant au front (`UMAMI_WEBSITE_ID`) ; il ne refait que ce qui manque. Langue du tableau de bord : Profil › Langue.

- Les pages chargent le script et envoient les visites par `/mesure/` sur le site même (Caddyfile) ; seuls ces deux chemins mènent à Umami. Avant chaque envoi, `src/lib/audience.ts` retire de l'adresse les jetons (paramètres sauf `utm_…`, page `/photos/<jeton>`).
- « Do Not Track » est respecté, et la page Confidentialité permet de ne plus compter un appareil.
- La sauvegarde de nuit garde aussi la base `umami` (`audience-AAAA-MM-JJ.sql.gz`) et efface les visites de plus de 25 mois.

### Fonctionnement

À la main, sans le script :

```bash
cp .env.prod.example .env.prod      # puis remplir les secrets
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

- Caddy obtient le certificat HTTPS de `SITE_DOMAIN` et sert tout sur une seule origine : `/api`, `/admin` et `/static` vont à Django (gunicorn, fichiers statiques par whitenoise), le reste au front (Next.js en sortie autonome). Il redirige le HTTP vers le HTTPS et ajoute les en-têtes de sécurité à tout le site.
- Les migrations tournent une fois avant l'API et le planificateur. Les niveaux et chapitres sont créés par les migrations : une base neuve est utilisable sans données de démonstration.
- HSTS (`DJANGO_HSTS_SECONDS`), cookies sécurisés ; Redis pour le cache et la limitation de débit ; Sentry si `SENTRY_DSN` est défini.
- Embeddings : `--profile embeddings`, et `EMBEDDINGS_URL=http://embeddings` dans `.env.prod`.
- Umami a sa propre base, `umami`, dans le même PostgreSQL (créée par le service `umami-db`).

## Tests

```bash
cd backend
uv run python manage.py test

cd frontend
npm test            # Vitest : utilitaires du front
npx tsc --noEmit
npm run lint
```

Le backend couvre le ledger et le barème, la relecture par les pairs (tours, délais, volontaires, relecture de l'équipe, révisions), les votes, l'authentification (Google compris), les notifications (push compris), la détection des doublons (avec E2 et l'avis du LLM simulés), les classements, les badges et les niveaux de confiance, le niveau de contributeur et la carte de compétences, le fil d'accueil, les signalements, les sanctions et appels, les questions de compréhension, les photos de copie (QR code, sessions chronométrées), l'entraînement chronométré, le défi du jour, les séries et objectifs, et les tâches planifiées. Aucun test n'appelle un service externe : Claude, Google et les embeddings sont simulés.

## Limites connues

- La composition de production a été construite et répétée de bout en bout avec Docker, mais derrière le certificat interne de Caddy : le certificat Let's Encrypt et l'envoi réel des emails par Brevo se vérifient au premier déploiement.
- Les appels à Claude sont testés avec un client simulé ; leur premier usage réel se fera avec la clé.
- Score d'intégrité : les empreintes IA de référence, la rupture de style et le classifieur du document ne sont pas encore mesurés ; leurs poids sont retirés et les autres renormalisés.
- Le Web Push est testé avec un chiffrement et une signature VAPID réels, mais un service de push simulé : à vérifier sur un appareil au premier déploiement, en HTTPS.
- Pas encore : épreuves classées (V2).
