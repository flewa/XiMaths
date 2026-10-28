# XiMaths

Plateforme communautaire d'exercices de mathématiques du supérieur (L1 à M2, prépa MP, PC, PSI, PT) : on publie des exercices, on propose des solutions, et des pairs tirés au sort les relisent.

La conception complète (barème, détection de doublons, anti-triche, phasage) est dans le document [XiMaths — Proposition de développement](https://claude.ai/artifact/SFjJeg2DwwHuPvjJZ6MGcB).

## Structure

| Dossier | Contenu |
| --- | --- |
| `backend/` | API Django 5.2 + Django Ninja. Apps : `accounts` (utilisateur, niveau de confiance), `catalog` (niveaux, chapitres), `content` (exercices, solutions, relectures, votes), `duplicates` (détection des doublons), `gamification` (ledger des points, barème, classements, badges), `moderation` (signalements), `training` (entraînement chronométré) |
| `frontend/` | Next.js 15 (App Router), Tailwind, Markdown + KaTeX rendus côté serveur. Design décrit dans `frontend/DESIGN-opencode.ai.md` |
| `docker-compose.yml` | PostgreSQL 16 avec pgvector, Redis, et bge-m3 servi par Text Embeddings Inference |

## Prérequis

- [uv](https://docs.astral.sh/uv/) : il installe Python 3.12 tout seul.
- Node 18.18 ou plus. Node 20+ est recommandé : Tailwind est figé en 4.1.18, dernière version compatible Node 18.
- Docker, facultatif. Sans `DATABASE_URL`, le backend utilise SQLite (`backend/db.sqlite3`).

## Lancer en local

Backend, sur http://127.0.0.1:8000 :

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo          # comptes, exercices et solutions de démonstration
uv run python manage.py runserver 8000
```

Front, sur http://localhost:3000 :

```bash
cd frontend
npm install
npm run dev
```

- Comptes de démo : `camille` (experte), `relecteur1` à `relecteur3`, `lea`, `yanis`, et `moderateur`, qui a accès à l'admin. Leur mot de passe de développement est `DEMO_PASSWORD` dans `backend/content/management/commands/seed_demo.py`.
- Les emails (lien de vérification d'adresse) s'affichent dans la console du backend.
- Le front relaie `/api` vers Django (`next.config.ts`) : session et CSRF fonctionnent sur la même origine.
- Ne lance pas `npm run build` pendant `npm run dev` : les deux écrivent dans `.next` et le serveur de dev renvoie alors des 500. En cas de souci, supprime `.next` et relance `npm run dev`.
- Documentation de l'API : http://127.0.0.1:8000/api/docs
- Back-office : http://127.0.0.1:8000/admin/, avec le compte `moderateur`. La file des doublons à arbitrer y est sous « Doublons ».
- Avec PostgreSQL et les embeddings : `docker compose up -d`, puis copier `.env.example` dans `backend/.env` et lancer les commandes avec `uv run --env-file .env …`

## Détection des doublons

À la publication, l'énoncé est comparé aux exercices publiés (document de conception, section « Détection IA des doublons », version MVP sans LLM) :

- **Normalisation** : notations unifiées (`\R`, `ℝ` et `\mathbb{R}` ; `\le` et `\leqslant`…), variables renommées dans l'ordre d'apparition, constantes remplacées par `NUM` dans une version abstraite.
- **Signatures** : MinHash (128 permutations, shingles de 5 jetons) indexées en LSH, plus l'embedding bge-m3 si `EMBEDDINGS_URL` est défini.
- **Bandes** :
    - quasi-copie : J(F) ≥ 0,85 ;
    - variante paramétrique : J(F′) ≥ 0,85, ou seules les constantes changent ;
    - très similaire : s ≥ 0,88 ;
    - peut-être lié : s ≥ 0,80.
- **Score** : s = 0,8 cos(E1) + 0,2 J(F). Sans le résumé par LLM (E2), cos(E1) prend son poids. Ces seuils sont des valeurs de départ à calibrer.
- **Sans service d'embeddings** (SQLite, pas de Docker) : seules les quasi-copies et les variantes sont détectées.

Pendant la rédaction, le panneau « Exercices proches » se met à jour. À la publication, une quasi-copie, une variante ou un exercice très similaire ouvre l'écran « Cet exercice existe peut-être déjà ». L'auteur y choisit :

- **le même** : il va voir l'existant, rien n'est publié ;
- **une variante** : publiée en lien avec l'existant ;
- **différent** : publié, avec une phrase d'explication ; la paire part en file d'arbitrage.

Aucune fusion n'est automatique. Dans l'admin, un modérateur fusionne (le plus récent rejoint le plus ancien, ses solutions suivent, son adresse redirige), lie comme variantes ou déclare distincts ; une fusion s'annule. Une paire tranchée n'est jamais reproposée.

Le job nocturne indexe les exercices et ouvre les paires manquées :

```bash
uv run python manage.py scan_duplicates            # exercices publiés depuis 2 jours
uv run python manage.py scan_duplicates --reindex --all   # après un changement de normalisation ou de modèle
```

## Fil d'accueil

La page d'accueil montre le fil d'un niveau : par défaut, celui que tu as déclaré.

- **Composition :** une seule page de 20 exercices, sans défilement infini.
    - 60 % de **Tendances**, par score T ;
    - 25 % d'**À résoudre** : moins de 14 jours et moins de 2 solutions validées, les moins affichés d'abord ;
    - 15 % d'**exploration** : exercices de moins de 30 jours tirés au hasard, en priorité ceux qui n'ont pas encore eu 200 affichages.
- **Ordre :** les trois sources sont entrelacées sur la page. Chaque exercice affiche pourquoi il est là.
- **Scores**, logarithmiques : cent fois plus de solutions ne donnent qu'un score sept fois plus élevé.
    - T (Tendances) : une solution perd la moitié de son poids tous les 30 jours ;
    - P (Populaires) : sans décroissance ; c'est le tri « Populaires » de la page `/exercices`.
- **Ce qui compte :**
    - une solution par auteur, hors auteur de l'exercice ;
    - 1 pour une solution validée, 0,4 en relecture, 0 pour une solution générée ;
    - les votes pondérés ;
    - ×1,1 pour l'exercice canonique d'un cluster de doublons.
- **Pénalités :** les solutions des comptes liés à l'auteur ne comptent pas, et un exercice signalé compte pour moitié tant que le signalement est ouvert.
- **Calcul :** à la demande. Les affichages sont comptés à chaque fil servi, ce qui en fait une approximation.

`/exercices` permet aussi de parcourir tout le catalogue : récents, populaires ou sans solution validée.

## Classements et badges

Classements (page `/classements`) :

- **Calcul :** à la demande, depuis le ledger.
- **Semaine :** du lundi 0 h au dimanche 23 h 59, heure de Paris.
- **Tableaux :** un par niveau et un global, plus un Panthéon des points cumulés, laissé au second plan.
- **Niveau qui compte :** celui de l'exercice. Un exercice de M2 fait marquer en M2, quel que soit le niveau déclaré.
- **Affichage :** le top 50, puis ta position avec tes 5 voisins de chaque côté. Le filtre « mes pairs » ne garde que ceux qui ont déclaré ton niveau.
- **Qui est classé :** les membres (niveau de confiance 1 ou plus), sans sanction en cours. Chacun peut masquer sa présence ; ses points disparaissent alors aussi de son profil public.
- **Consolidation :** une annulation compte dans la semaine des points annulés si elle arrive dans les 24 h qui suivent la fin de la semaine. Passé ce délai, la semaine est définitive.
- **Écart avec le document :** pas de sorted sets Redis. Une agrégation SQL suffit à l'échelle du MVP et permet le filtre « mes pairs ». Le stockage peut changer sans toucher à l'interface.

Badges (page `/badges`, et sur chaque profil `/membres/<pseudo>`) :

- **Les 8 badges du MVP :** Premier pas, Validé !, Pionnier, Auteur, Relecteur fiable, Touche-à-tout, Élégance et Chasseur de doublons.
- **Critères :** publics. Un badge est attribué dès l'événement qui le débloque, et reste acquis.

Un compte Nouveau devient Membre dès 7 jours d'ancienneté et 30 points. Les niveaux suivants restent attribués à la main.

Le job nocturne fait les promotions que l'ancienneté seule débloque, et rattrape les badges manquants :

```bash
uv run python manage.py refresh_progress
```

## Signalements et comptes liés

**Signaler.** Tout membre vérifié peut signaler un exercice publié ou une solution validée, sauf les siens. Le bouton est sous chaque contenu. Il suit ses signalements sur `/signalements` et l'auteur du contenu ne sait pas qui l'a signalé.

**Doublons signalés.** Ils demandent le niveau Relecteur et l'exercice d'origine. Ils ouvrent, ou rejoignent, une paire dans la file des doublons, et suivent la décision prise sur la paire. Une paire déjà jugée distincte ne peut pas être resignalée.

**Décision.** Un modérateur tranche les autres motifs dans l'admin (« Modération › Signalements »). Pour confirmer, il doit écrire un motif, destiné à l'auteur du contenu. Les autres signalements du même contenu pour le même motif sont tranchés en même temps.

| Motif | Si le signalement est confirmé |
| --- | --- |
| Doublon | fusion ou lien de variantes, décidés dans la file des doublons |
| Plagiat d'une solution | points annulés, −50, solution masquée |
| Plagiat ou contenu inapproprié | contenu retiré, ses points annulés |
| IA non déclarée | points de la solution annulés, sans étiquette publique ni pénalité |
| Erreur | pas d'effet automatique : le modérateur corrige le contenu |

**Récompenses.** Un doublon, un plagiat ou une erreur confirmés rapportent +3 au signaleur. Le premier doublon confirmé donne le badge Chasseur de doublons.

**Effet sur le fil.** Un exercice signalé, tant que le signalement est ouvert, compte pour moitié dans le fil d'accueil.

**Comptes liés.** Deux comptes sont liés automatiquement quand chacun réserve plus de la moitié de ses votes à l'autre, avec au moins 10 votes chacun. Un modérateur peut aussi les lier à la main, dans l'admin (« Comptes › Comptes liés »).

Un lien n'est pas une sanction :

- leurs votes mutuels ne pèsent plus rien, et les points déjà gagnés par ces votes sont annulés ;
- ils ne sont plus tirés au sort pour se relire ;
- leurs solutions ne font plus monter les exercices de l'autre dans le fil.

## Entraînement chronométré

Depuis la fiche d'un exercice, « S'entraîner en temps limité » ouvre l'écran des règles. On y choisit 15, 30, 45 ou 60 minutes ; le temps conseillé dépend de la difficulté. On peut aussi déclarer un tiers-temps (×1,33). La session vit sur `/entrainement/<id>`.

- **Le serveur fait foi.** Le navigateur sauvegarde le brouillon toutes les 10 s, et chaque sauvegarde fait avancer le chrono. Au-delà de 30 s sans nouvelles, l'onglet est considéré fermé : ce temps ne compte pas, et la session se reprend.
- **Pauses.** Deux au plus. Pendant une pause, l'énoncé et le brouillon sont masqués.
- **Échéance.** La dernière version est rendue automatiquement. Une sauvegarde arrivée dans les 60 s de grâce compte encore.
- **Enregistré, jamais pénalisé :** les sorties d'onglet, et la taille des collages venus d'ailleurs, jamais leur contenu. Un copier-coller à l'intérieur du brouillon ne compte pas.
- **Au rendu :**
    - la réponse finale est comparée par SymPy à celle de l'exercice, sur une grammaire restreinte : les réponses ne sont jamais évaluées comme du Python libre ;
    - la justification devient une solution « entraînement », qui part en relecture ;
    - le temps est comparé à la médiane des autres sessions ;
    - une auto-évaluation de 1 à 5 affine la difficulté estimée.
- **Interface.**
    - Le chrono est fixé en haut. On peut le masquer : il ne reste alors que des rappels à 10, 5 et 1 minute, lus aussi par les lecteurs d'écran.
    - Il change discrètement de couleur à 5 minutes.
    - Sur mobile, des onglets séparent l'énoncé, la solution et l'aperçu.

## Tests

```bash
cd backend
uv run python manage.py test
```

Les tests couvrent :

- le ledger : idempotence, plafonds quotidiens, annulations, plagiat ;
- la relecture par les pairs : tirage au sort, quorum, contestation, verdicts « avec lacunes » ;
- les votes dégressifs ;
- l'authentification : inscription, vérification d'email, CSRF, limitation de débit ;
- l'API en lecture et en écriture, avec ses droits ;
- la détection des doublons : normalisation, signatures, bandes, choix de l'auteur, scan, fusion et son annulation, file d'arbitrage dans l'admin. L'embedding y est simulé ;
- les classements : semaines en heure de Paris (changement d'heure compris), niveaux, ex aequo, éligibilité, consolidation, voisins, « mes pairs », masquage ;
- les badges et le passage au niveau Membre ;
- le fil d'accueil : scores T et P, répartition 12 / 5 / 3, exposition des moins vus, tris de la liste ;
- les signalements : conséquences de chaque motif, décision motivée, doublons via la file, admin ; les comptes liés : détection, neutralisation des votes, relecteurs, fil ;
- l'entraînement chronométré : réponses équivalentes et entrées hostiles, chrono arrêté onglet fermé, pauses, grâce à l'échéance, rendu et relecture, médiane, auto-évaluation, tiers-temps.

## Où en est le MVP

En place :

- modèle de données des comptes, niveaux, exercices, solutions, relectures, votes et points ;
- ledger des points en ajout seul, avec le barème du document de conception ;
- publication, tirage au sort de 3 relecteurs, règle de validation et rémunération ;
- comptes par session Django : inscription, connexion par pseudo ou email, vérification de l'adresse par lien signé, limitation de débit ;
- API d'écriture réservée aux comptes vérifiés :
    - publier un exercice (brouillon puis publication) ;
    - proposer une solution en déclarant l'usage de l'IA ;
    - relire de façon anonyme et à l'aveugle, avec un commentaire obligatoire pour un verdict négatif ;
    - voter ;
- macros LaTeX libres (`\def`, `\newcommand`…) et commandes de lien refusées à l'écriture ;
- détection des doublons v1 : normalisation, MinHash et LSH, embedding bge-m3 optionnel, bandes, écran « Cet exercice existe peut-être déjà », variantes liées, file d'arbitrage dans l'admin, fusion réversible, scan nocturne ;
- classements hebdomadaires par niveau et global, Panthéon, les 8 badges, profils publics, passage automatique au niveau Membre ;
- fil d'accueil Tendances / À résoudre / exploration, et catalogue triable (récents, populaires, sans solution) ;
- signalements (5 motifs, décision motivée dans l'admin, doublons via la file d'arbitrage) et comptes liés par réciprocité des votes ;
- entraînement chronométré non classé, réponse finale vérifiée par SymPy ;
- front, au design « terminal » de `frontend/DESIGN-opencode.ai.md` : fil d'accueil, catalogue, inscription, connexion, publication avec aperçu LaTeX et exercices proches, solutions et retours des relecteurs, page Relectures, votes, variantes, classements, badges, profils, signalements, entraînement chronométré, solutions validées repliées pour inciter à chercher d'abord.

Reste à faire pour le MVP :

- page de réglages (tiers-temps, préférences de notification) : le tiers-temps se déclare pour l'instant sur l'écran des règles du chronométré ;
- notifications dans l'application et par email (dont le motif d'un retrait, à transmettre à l'auteur du contenu) ;
- appel d'une décision de modération, et échelle des sanctions (avertissement, exclusion des classements, suspension).
