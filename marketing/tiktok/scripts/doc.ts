// Écrit SCRIPTS.md, la fiche de tournage des douze vidéos, depuis src/videos.ts.
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { VIDEOS, type Visual } from "../src/videos";
import { estimateWords, TAIL, TRANSITION } from "../src/words";

const FPS = 30;

function screen(visual: Visual): string {
  const strip = (text: string) =>
    text
      .replace(/~([^~]+)~/g, "~~$1~~")
      .replace(/\*/g, "")
      .replace(/\n/g, " / ");
  switch (visual.kind) {
    case "title":
      return `Texte : « ${strip(visual.text)} »`;
    case "phone":
      return `Téléphone, capture \`${visual.shot}\`, zoom sur \`${visual.focus ?? "—"}\`${visual.label ? ` : « ${visual.label} »` : ""}`;
    case "reviewers":
      return `Trois relecteurs tirés au sort${visual.verdicts ? ", verdicts et commentaire" : ""}${visual.title ? ` : « ${visual.title} »` : ""}`;
    case "timer":
      return `Chrono ${visual.minutes}:00${visual.extra ? ` (${visual.extra})` : ""}`;
    case "proof":
      return `Copie${visual.title ? ` « ${visual.title} »` : ""}${visual.stamp ? `, note ${visual.stamp}` : ""}${visual.headline ? `, titre « ${strip(visual.headline)} »` : ""}`;
    case "handwriting":
      return visual.source
        ? "Photo de la copie, transcription dans l'éditeur, aperçu LaTeX"
        : "Copie manuscrite qui s'écrit";
    case "streakBreak":
      return `Série quotidienne de ${visual.days} jours qui s'éteint`;
    case "weeks":
      return visual.mode === "joker"
        ? "Semaines : une semaine sauvée par un joker"
        : "Semaines : 3 jours actifs suffisent";
    case "skills":
      return `Carte de compétences${visual.next ? `, prochain exercice en ${visual.next}` : ""}`;
    case "chat":
      return `Réponse d'IA fausse, tampon « ${visual.verdict} »`;
    case "leaderboard":
      return "Classement : tu passes devant";
    case "goal":
      return `Objectif « ${visual.title} » ${visual.done}/${visual.target}, ${visual.deadline}`;
    case "chips":
      return `${visual.title ? `${visual.title} : ` : ""}${visual.items.join(" · ")}`;
    case "cta":
      return `Fin : [ξ] XiMaths, \`${visual.prompt}\`, « ${visual.line} », lien en bio`;
  }
}

const lines = [
  "# Vidéos TikTok de XiMaths",
  "",
  "Fiche générée par `npm run scripts-doc` depuis `src/videos.ts` : c'est là qu'on modifie un texte.",
  "Durées estimées sans la voix ; avec elle, chaque scène prend la durée de sa phrase.",
  "",
  "Pour chaque publication : cocher « contenu généré par IA » (la voix est synthétique), mettre",
  "la légende et les hashtags ci-dessous, choisir la première image comme couverture, et ajouter",
  "un son tendance très bas sous la voix si l'un colle au ton.",
  "",
];

for (const video of VIDEOS) {
  let frames = 0;
  const rows = video.scenes.map((scene, index) => {
    const words = estimateWords(scene.voice);
    const seconds = words[words.length - 1].end + TAIL;
    const start = frames / FPS;
    frames += Math.max(45, Math.ceil(seconds * FPS)) - TRANSITION;
    return `| ${index + 1} | ${start.toFixed(1)} s | ${screen(scene.visual).replace(/\|/g, "\\|")} | ${scene.voice} |`;
  });
  lines.push(
    `## ${video.id}`,
    "",
    `**Besoin :** ${video.need}. **Pour :** ${video.audience}. **Durée :** ~${Math.round((frames + TRANSITION) / FPS)} s.`,
    "",
    "| # | Début | À l'écran | Voix off |",
    "| --- | --- | --- | --- |",
    ...rows,
    "",
    `**Légende :** ${video.caption}`,
    "",
    `**Hashtags :** ${video.hashtags.map((tag) => `#${tag}`).join(" ")}`,
    "",
  );
}

const out = join(dirname(fileURLToPath(import.meta.url)), "..", "SCRIPTS.md");
writeFileSync(out, lines.join("\n"));
console.log(out);
