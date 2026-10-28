import type { DailyChallenge, Progress, Skill } from "./api";

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

/** La semaine en cours en une ligne : ■ jour actif, □ jour passé sans activité, · à venir. */
export function weekLine(days: Progress["days"]) {
  return days.map((day) => (day.active ? "■" : day.future ? "·" : "□")).join(" ");
}
