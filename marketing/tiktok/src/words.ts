// Mots d'une phrase dans le temps, sans dépendance à Remotion : les scripts Node
// (voix, fiche des scripts) s'en servent aussi.

export type Word = { text: string; start: number; end: number };

/** Silence avant la première syllabe, et après la dernière, en secondes. */
export const LEAD_IN = 0.12;
export const TAIL = 0.42;
/** Recouvrement des scènes pendant les transitions, en images. */
export const TRANSITION = 8;

const PAUSES: [RegExp, number][] = [
  [/[.?!…]$/, 0.3],
  [/[:;]$/, 0.22],
  [/,$/, 0.14],
];

/** Débit d'une voix off rapide : environ 15 caractères par seconde, avec les pauses. */
export function estimateWords(text: string): Word[] {
  const words: Word[] = [];
  let time = LEAD_IN;
  for (const token of text.split(/\s+/).filter(Boolean)) {
    const letters = token.replace(/[^\p{L}\p{N}]/gu, "").length;
    const end = time + 0.08 + letters * 0.052;
    words.push({ text: token, start: time, end });
    time = end + (PAUSES.find(([pattern]) => pattern.test(token))?.[1] ?? 0.02);
  }
  return words;
}
