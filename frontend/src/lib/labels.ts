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

const monthFormat = new Intl.DateTimeFormat("fr-FR", { month: "long", timeZone: "UTC" });

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
