import type { CourseNoteSummary, DailyChallenge, ExerciseSort, Skill } from "./api";

/** Chapitre où proposer le prochain exercice : celui où le membre a le plus résolu
 * (on continue sur sa lancée), puis le mieux maîtrisé ; null s'il n'y a rien à proposer. */
export function nextSkill(skills: Skill[]): Skill | null {
  const candidates = skills.filter((skill) => skill.next !== null);
  if (candidates.length === 0) return null;
  return candidates.reduce((best, skill) =>
    skill.solved > best.solved || (skill.solved === best.solved && skill.mastery > best.mastery) ? skill : best,
  );
}

/** Le défi du jour du niveau déclaré, s'il reste à relever. */
export function openChallenge(challenges: DailyChallenge[], level: string | null) {
  const mine = challenges.find((challenge) => challenge.level === level) ?? null;
  return mine && mine.attempt === null ? mine : null;
}

/** Valeur de ?niveau= pour le fil de tous les niveaux. */
export const ALL_LEVELS = "tous";

/** Vues des exercices de l'accueil (?vue=) ; la première, le fil, est celle par défaut. */
export const HOME_VIEWS: { value: string; label: string; sort: ExerciseSort | null; intro: string }[] = [
  {
    value: "pour-toi",
    label: "Pour toi",
    sort: null,
    intro: "Ceux dont on parle, ceux qui attendent leur première solution, et quelques nouveautés au hasard.",
  },
  {
    value: "sans-solution",
    label: "Sans solution",
    sort: "unsolved",
    intro: "Personne ne les a encore résolus : à toi d'ouvrir la voie.",
  },
  {
    value: "tendance",
    label: "Tendance",
    sort: "trending",
    intro: "Ceux qui ont reçu le plus de solutions et de votes ces dernières semaines.",
  },
  { value: "nouveaux", label: "Nouveaux", sort: "recent", intro: "Les derniers publiés." },
];

export function homeView(value: string | undefined) {
  return HOME_VIEWS.find((view) => view.value === value) ?? HOME_VIEWS[0];
}

/** Adresse de l'accueil pour une vue et un niveau (?niveau= tel quel : un code, « tous », ou rien). */
export function homeHref(view: string, niveau: string | undefined) {
  const query = new URLSearchParams();
  if (niveau) query.set("niveau", niveau);
  if (view !== HOME_VIEWS[0].value) query.set("vue", view);
  const search = query.toString();
  return search ? `/?${search}` : "/";
}

/** Rappels de cours à proposer : publiés, d'abord ceux des chapitres et notions du fil,
 * puis ceux du cycle du niveau déclaré (1re année : sup, 2e : spé). */
export function suggestedNotes(
  notes: CourseNoteSummary[],
  { year, topics }: { year: number | null; topics: string[] },
  count = 3,
) {
  const cycle = year === 1 ? "sup" : year === 2 ? "spe" : null;
  const rank = (note: CourseNoteSummary) =>
    (note.topic_name && topics.includes(note.topic_name) ? 0 : 2) + (cycle && note.cycle !== cycle ? 1 : 0);
  return notes
    .filter((note) => note.published)
    .map((note, index) => ({ note, index }))
    .sort((a, b) => rank(a.note) - rank(b.note) || a.index - b.index)
    .slice(0, count)
    .map(({ note }) => note);
}

const DAY_FORMAT = new Intl.DateTimeFormat("fr-FR", {
  weekday: "long",
  day: "numeric",
  month: "long",
  timeZone: "Europe/Paris",
});

/** « Dimanche 8 novembre », à l'heure de Paris. */
export function dayLabel(date: Date) {
  const label = DAY_FORMAT.format(date);
  return label.charAt(0).toUpperCase() + label.slice(1);
}
