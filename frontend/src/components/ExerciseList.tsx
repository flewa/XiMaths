import Link from "next/link";

import type { ExerciseSummary, FeedItem } from "@/lib/api";

import { Difficulty, LevelTags } from "./ExerciseMeta";

function solutionsLabel(count: number) {
  if (count === 0) return "aucune solution pour l'instant";
  return `${count} solution${count > 1 ? "s" : ""} validée${count > 1 ? "s" : ""}`;
}

const REASON_STYLES: Record<FeedItem["reason"], string> = {
  // « À résoudre » ressort : c'est là que la communauté attend une première solution.
  a_resoudre: "text-accent-text before:bg-accent",
  tendance: "text-mute before:bg-stone",
  exploration: "text-success before:bg-success",
};

/** Liste d'exercices ; dans le fil d'accueil, chacun dit pourquoi il est là. */
export function ExerciseList({ exercises }: { exercises: (ExerciseSummary | FeedItem)[] }) {
  return (
    <ul className="divide-y divide-hairline border-y border-hairline">
      {exercises.map((exercise) => (
        <li key={exercise.id}>
          <Link href={`/exercices/${exercise.id}`} className="-mx-3 block rounded-lg px-3 py-4 hover:bg-hover">
            <span className="flex items-baseline gap-4">
              <span className="min-w-0 flex-1 font-serif text-xl leading-snug text-ink-deep">{exercise.title}</span>
              {"reason" in exercise && (
                <span
                  className={`inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap text-[13px] before:size-1.5 before:rounded-full ${REASON_STYLES[exercise.reason]}`}
                >
                  {exercise.reason_label}
                </span>
              )}
            </span>
            <span className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-mute">
              <LevelTags levels={exercise.levels} />
              {exercise.topics.length > 0 && <span>{exercise.topics.join(", ")}</span>}
              <Difficulty value={exercise.difficulty} />
              <span className={exercise.validated_solutions === 0 ? "text-accent-text" : undefined}>
                {solutionsLabel(exercise.validated_solutions)}
              </span>
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
