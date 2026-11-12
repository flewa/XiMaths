import Link from "next/link";

import type { ExerciseSummary, FeedItem } from "@/lib/api";

import { Avatar } from "./Avatar";
import { Difficulty } from "./ExerciseMeta";
import { MathText } from "./MathText";

/** Solutions envoyées : un compteur, les solutions elles-mêmes restent privées. Rien quand il
 * n'y en a pas : « aucune solution » sur chaque ligne ferait croire le site vide. */
function solutionsLabel(count: number) {
  return count === 0 ? null : `${count} solution${count > 1 ? "s" : ""} envoyée${count > 1 ? "s" : ""}`;
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

// Les premiers niveaux, puis « +n » : deux sur téléphone, quatre sur ordinateur. Un exercice
// de 1re année en compte jusqu'à huit, qui noyaient le titre.
const PHONE_LEVELS = 2;
const DESKTOP_LEVELS = 4;

const levelPill = "rounded-full bg-surface-card px-2 py-px text-xs font-medium text-body";

/** Liste d'exercices : titre, puis auteur (quand c'est un membre), chapitre, niveaux et
 * difficulté ; à droite, ce qui le distingue et le nombre de solutions envoyées, en gris : rien
 * n'y crie. Toute la ligne mène à l'exercice ; le pseudo de l'auteur, à son profil.
 * `showAuthor` à faux : la liste d'un seul auteur (sur son profil). */
export function ExerciseList({
  exercises,
  showAuthor = true,
}: {
  exercises: (ExerciseSummary | FeedItem)[];
  showAuthor?: boolean;
}) {
  return (
    <ul className="divide-y divide-hairline">
      {exercises.map((exercise) => {
        const tag = tagOf(exercise);
        const morePhone = exercise.levels.length - PHONE_LEVELS;
        const moreDesktop = exercise.levels.length - DESKTOP_LEVELS;
        const author = showAuthor ? exercise.author_profile : null;
        const sent = solutionsLabel(exercise.submitted_solutions);
        return (
          <li key={exercise.id}>
            <div className="relative -mx-3 flex items-center gap-5 rounded-xl px-3 py-4 hover:bg-hover">
              <span className="min-w-0 flex-1">
                {/* Le lien s'étend à toute la ligne (after:) ; le pseudo de l'auteur passe au-dessus. */}
                <Link
                  href={`/exercices/${exercise.id}`}
                  className="block font-serif text-[1.1875rem] leading-snug text-ink-deep after:absolute after:inset-0 after:rounded-xl"
                >
                  <MathText>{exercise.title}</MathText>
                </Link>
                <span className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1.5 text-[13px] text-mute">
                  {author && (
                    <>
                      <Link
                        href={`/membres/${encodeURIComponent(author.username)}`}
                        className="relative z-10 inline-flex min-h-6 items-center gap-1.5 text-body hover:text-ink hover:underline"
                      >
                        <Avatar avatar={author.avatar} size={18} />
                        <span className="sr-only">Par </span>
                        {author.username}
                      </Link>
                      <span aria-hidden="true">·</span>
                    </>
                  )}
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
                      className={`${levelPill} ${index >= DESKTOP_LEVELS ? "hidden" : index >= PHONE_LEVELS ? "max-sm:hidden" : ""}`}
                    >
                      {level}
                    </span>
                  ))}
                  {morePhone > 0 && (
                    <span aria-hidden="true" className={`${levelPill} sm:hidden`}>
                      +{morePhone}
                    </span>
                  )}
                  {moreDesktop > 0 && (
                    <span aria-hidden="true" title={exercise.levels.slice(DESKTOP_LEVELS).join(", ")} className={`${levelPill} max-sm:hidden`}>
                      +{moreDesktop}
                    </span>
                  )}
                  <span aria-hidden="true">·</span>
                  <Difficulty value={exercise.difficulty} short />
                  {(tag || sent) && (
                    <span className="ml-auto flex gap-2 sm:hidden">
                      {tag && <span className={tag.className}>{tag.label}</span>}
                      {sent && <span>{sent}</span>}
                    </span>
                  )}
                </span>
              </span>
              <span className="hidden w-36 shrink-0 text-right text-[13px] sm:block">
                {tag && <span className={`block ${tag.className}`}>{tag.label}</span>}
                {sent && <span className="block text-mute">{sent}</span>}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
