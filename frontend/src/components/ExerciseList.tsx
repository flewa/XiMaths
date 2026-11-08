import Link from "next/link";

import type { ExerciseSummary, FeedItem } from "@/lib/api";

import { Difficulty } from "./ExerciseMeta";

function solutionsLabel(count: number) {
  return count === 0 ? "aucune solution" : `${count} solution${count > 1 ? "s" : ""}`;
}

type Tag = { label: string; className: string };

/** Ce qui distingue l'exercice : en vogue, ou tout juste publié. Les autres raisons du fil
 * (« à résoudre », « à découvrir ») restent internes : l'élève voit l'état de l'exercice,
 * pas la mécanique qui l'a choisi. */
function tagOf(exercise: ExerciseSummary | FeedItem): Tag | null {
  if ("reason" in exercise && exercise.reason === "tendance") return { label: "Tendance", className: "text-body" };
  if (exercise.is_new) return { label: "Nouveau", className: "text-success" };
  return null;
}

// Sur téléphone, les deux premiers niveaux, puis « +n ».
const PHONE_LEVELS = 2;

const levelPill = "rounded-full bg-surface-card px-2 py-px text-xs font-medium text-body";

/** Liste d'exercices : titre, puis chapitre, niveaux et difficulté ; à droite, ce qui le
 * distingue et ses solutions validées, en gris : rien n'y crie. */
export function ExerciseList({ exercises }: { exercises: (ExerciseSummary | FeedItem)[] }) {
  return (
    <ul className="divide-y divide-hairline">
      {exercises.map((exercise) => {
        const tag = tagOf(exercise);
        const moreLevels = exercise.levels.length - PHONE_LEVELS;
        return (
          <li key={exercise.id}>
            <Link
              href={`/exercices/${exercise.id}`}
              className="-mx-3 flex items-center gap-5 rounded-xl px-3 py-4 hover:bg-hover"
            >
              <span className="min-w-0 flex-1">
                <span className="block font-serif text-[1.1875rem] leading-snug text-ink-deep">{exercise.title}</span>
                <span className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1.5 text-[13px] text-mute">
                  {exercise.topics.length > 0 && (
                    <>
                      <span>{exercise.topics.join(", ")}</span>
                      <span aria-hidden="true">·</span>
                    </>
                  )}
                  <span className="sr-only">Niveaux : {exercise.levels.join(", ")}.</span>
                  {exercise.levels.map((level, index) => (
                    <span
                      key={level}
                      aria-hidden="true"
                      className={`${levelPill} ${index >= PHONE_LEVELS ? "max-sm:hidden" : ""}`}
                    >
                      {level}
                    </span>
                  ))}
                  {moreLevels > 0 && (
                    <span aria-hidden="true" className={`${levelPill} sm:hidden`}>
                      +{moreLevels}
                    </span>
                  )}
                  <span aria-hidden="true">·</span>
                  <Difficulty value={exercise.difficulty} short />
                  <span className="ml-auto flex gap-2 sm:hidden">
                    {tag && <span className={tag.className}>{tag.label}</span>}
                    <span>{solutionsLabel(exercise.validated_solutions)}</span>
                  </span>
                </span>
              </span>
              <span className="hidden w-28 shrink-0 text-right text-[13px] sm:block">
                {tag && <span className={`block ${tag.className}`}>{tag.label}</span>}
                <span className="block text-mute">{solutionsLabel(exercise.validated_solutions)}</span>
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
