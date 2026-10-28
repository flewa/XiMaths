# Vidéos TikTok

Douze vidéos verticales (1080 × 1920, 30 i/s, 20 à 28 s), une par besoin d'étudiant : retour sur ses rédactions en prépa, rédaction en L1, savoir si sa preuve est juste, défi chronométré, photo de copie en LaTeX, série sans culpabilité, carte de compétences, indications, IA et relecture humaine, publier ses exercices, classements, objectif de partiels.

Elles sont faites avec [Remotion](https://www.remotion.dev/) : chaque image est du code React, ce qui permet de changer un texte et de tout re-rendre.
Remotion est gratuit pour un particulier ou une entreprise de trois personnes au plus ; au-delà, il faut [une licence d'entreprise](https://www.remotion.pro/license).

- `SCRIPTS.md` : pour chaque vidéo, le besoin, les scènes (ce qu'on voit, ce que dit la voix), la légende et les hashtags. Fiche générée depuis `src/videos.ts`.
- `src/videos.ts` : le texte des vidéos, seule source à modifier.
- `public/shots/` : captures de l'application sur téléphone, et la position des éléments sur lesquels la caméra zoome.

## Rendre les vidéos

Node 24, comme le front.

```bash
npm install
npm run render                      # toutes, dans out/
```

```bash
npm run render -- 04-defi-chrono    # une seule
```

```bash
npm run studio                      # aperçu interactif dans le navigateur
```

Pour vérifier une vidéo sans la rendre en entier, `npm run preview -- 04-defi-chrono` écrit `out/preview/04-defi-chrono.png` : une image par scène, côte à côte (`HOOKS=1` : la première image de chaque vidéo citée).

Remotion télécharge son propre Chromium. Pour utiliser un Chromium déjà installé : `REMOTION_BROWSER=/chemin/vers/chrome-headless-shell npm run render`.

## Voix off

La voix vient d'[ElevenLabs](https://elevenlabs.io/) (modèle `eleven_multilingual_v2`). Le script envoie chaque phrase avec la précédente et la suivante, pour que le ton s'enchaîne, et récupère l'alignement mot à mot : les sous-titres suivent alors la voix, et chaque scène dure le temps de sa phrase.

La clé se donne par l'environnement, jamais dans un fichier du dépôt.

```bash
export ELEVENLABS_API_KEY=…
npm run voice -- --voices                 # liste les voix : en choisir une française
```

```bash
export ELEVENLABS_VOICE_ID=…
npm run voice                             # écrit public/voice/<vidéo>/<scène>.mp3 et .json
npm run render
```

Une scène dont le texte n'a pas changé n'est pas régénérée (`--force` pour tout refaire). La prononciation des mots difficiles (XiMaths, LaTeX, L1, M2) se règle dans `SAY`, en tête de `scripts/voice.ts`.

Sans voix, les vidéos se rendent quand même : la durée des scènes est estimée au débit d'une voix off rapide, et les sous-titres suivent cette estimation.

Un fond musical est facultatif : un fichier `public/music/fond.mp3`, dont on a les droits, est mixé sous la voix à 12 %.

## Captures de l'application

Les écrans du téléphone sont de vraies captures de XiMaths, sur la base de démonstration. Pour les refaire après un changement d'interface, lancer l'application (`./dev.sh` à la racine), puis :

```bash
npm run captures                    # toutes
npm run captures -- defi            # une seule
```

Le script utilise Playwright installé sur la machine (`npm i -g playwright`). Il se connecte avec les comptes de démonstration et crée un objectif pour `lea` s'il n'en a pas.

Les animations hors du téléphone (copie notée, relecteurs, série, classement, objectifs) illustrent les fonctions avec des valeurs d'exemple ; les règles qu'elles montrent sont celles de l'application (trois relecteurs, 72 h, 30 minutes et 40 avec un tiers-temps, deux jokers par mois, pause jusqu'à quatre semaines, −10 % de bonus par indication).

## Publier sur TikTok

- Cocher « contenu généré par IA » : la voix est synthétique.
- Légende et hashtags : dans `SCRIPTS.md`.
- Couverture : la première image, qui porte l'accroche.
- Le texte reste dans la zone que l'interface de TikTok ne couvre pas (`SAFE` dans `src/theme.ts`).
- Un son tendance peut s'ajouter dans TikTok, très bas sous la voix, s'il colle au ton.
