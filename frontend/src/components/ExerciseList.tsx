import Link from "next/link";

import type { ExerciseSummary, FeedItem } from "@/lib/api";

import { Difficulty, LevelTags } from "./ExerciseMeta";
import { Tag } from "./Tag";

function solutionsLabel(count: number) {
  if (count === 0) return "à résoudre";
  return `${count} solution${count > 1 ? "s" : ""} validée${count > 1 ? "s" : ""}`;
}

/** Liste d'exercices ; dans le fil d'accueil, chacun dit pourquoi il est là. */
export function ExerciseList({ exercises }: { exercises: (ExerciseSummary | FeedItem)[] }) {
  return (
    <ul className="divide-y divide-hairline border-b border-hairline">
      {exercises.map((exercise) => (
        <li key={exercise.id}>
          <Link href={`/exercices/${exercise.id}`} className="group block py-3 hover:bg-surface-soft">
            <span className="flex flex-wrap items-center gap-x-3 gap-y-1">
              {"reason" in exercise && (
                <Tag strong={exercise.reason === "tendance"}>{exercise.reason_label}</Tag>
              )}
              <span className="font-medium group-hover:underline group-hover:underline-offset-4">
                {exercise.title}
              </span>
            </span>
            <span className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-body">
              <LevelTags levels={exercise.levels} />
              <Difficulty value={exercise.difficulty} />
              {exercise.topics.length > 0 && <span>{exercise.topics.join(", ")}</span>}
              <span className="text-mute">· {solutionsLabel(exercise.validated_solutions)}</span>
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
