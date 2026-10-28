import type { AiUsage, SolutionStatus } from "@/lib/api";

export const AI_USAGE_OPTIONS: { value: AiUsage; label: string; help: string }[] = [
  { value: "aucune", label: "Aucune", help: "Raisonnement et rédaction personnels." },
  {
    value: "relecture",
    label: "Relecture ou mise en forme",
    help: "L'IA a corrigé la forme, pas le raisonnement. Points pleins.",
  },
  {
    value: "aide_idee",
    label: "Aide sur une idée",
    help: "L'IA t'a débloqué sur une étape. Points divisés par deux.",
  },
  {
    value: "generee",
    label: "Solution générée",
    help: "Publiée avec une étiquette, sans points.",
  },
];

/** Étiquette publique d'une solution ; rien quand l'IA n'a pas servi. */
export const AI_USAGE_BADGES: Record<AiUsage, string | null> = {
  aucune: null,
  relecture: "IA : relecture",
  aide_idee: "IA : aide sur une idée",
  generee: "Générée par IA",
};

export const SOLUTION_STATUS_LABELS: Record<SolutionStatus, string> = {
  held: "En vérification",
  under_review: "En relecture par des pairs",
  contested: "Avis partagés : un expert tranche",
  validated: "Validée",
  needs_work: "À compléter",
  hidden: "Masquée",
};

export const dateFormat = new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" });

/** Une décimale, à la française : « 2,4 ». */
export const oneDecimal = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

const monthFormat = new Intl.DateTimeFormat("fr-FR", { month: "long", timeZone: "UTC" });

/** « 1 tendance », « 3 tendances » : en français, 0 et 1 restent au singulier. */
export function plural(count: number, singular: string, pluralForm = `${singular}s`) {
  return `${count} ${count > 1 ? pluralForm : singular}`;
}

/** « à l'instant », « il y a 5 min », « il y a 3 h », « hier », « il y a 4 jours », puis la date.
 * `now` vient du serveur, pour que le rendu du navigateur soit le même. */
export function relativeTime(iso: string, now: string) {
  const minutes = Math.floor((new Date(now).getTime() - new Date(iso).getTime()) / 60_000);
  if (minutes < 1) return "à l'instant";
  if (minutes < 60) return `il y a ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `il y a ${hours} h`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "hier";
  if (days < 7) return `il y a ${days} jours`;
  return dateFormat.format(new Date(iso));
}

/** 1er, 2e, 3e… */
export function ordinal(rank: number) {
  return rank === 1 ? "1er" : `${rank}e`;
}

/** « du 19 au 25 octobre », « du 26 octobre au 1er novembre », depuis deux dates ISO. */
export function weekRange(start: string, end: string) {
  const [from, to] = [start, end].map((iso) => new Date(`${iso}T00:00:00Z`));
  const day = (date: Date) => (date.getUTCDate() === 1 ? "1er" : String(date.getUTCDate()));
  const month = (date: Date) => monthFormat.format(date);
  return month(from) === month(to)
    ? `du ${day(from)} au ${day(to)} ${month(to)}`
    : `du ${day(from)} ${month(from)} au ${day(to)} ${month(to)}`;
}

/** Barre de progression façon terminal : « [######----] ». Pleine au-delà de la cible. */
export function progressBar(done: number, target: number, width = 20) {
  const filled = target > 0 ? Math.min(width, Math.round((done / target) * width)) : 0;
  return `[${"#".repeat(filled)}${"-".repeat(width - filled)}]`;
}
