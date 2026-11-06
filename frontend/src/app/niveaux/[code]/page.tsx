import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { fetchExercises, fetchLevels, fetchTopics, type Level } from "@/lib/api";
import { plural } from "@/lib/labels";
import { LEVEL_INTROS, chapterPath, levelPath } from "@/lib/seo-pages";
import { SHARE_IMAGE } from "@/lib/site";

type Props = { params: Promise<{ code: string }> };

async function findLevel(slug: string) {
  const levels = await fetchLevels();
  return levels.find((level) => level.code.toLowerCase() === slug.toLowerCase()) ?? null;
}

/** « Exercices de maths en MPSI », « Exercices de maths en L1 (Licence 1) ». */
function heading(level: Level) {
  return level.track === "prepa"
    ? `Exercices de maths en ${level.code}`
    : `Exercices de maths en ${level.code} (${level.name})`;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { code } = await params;
  const level = await findLevel(code).catch(() => null);
  if (!level) return { title: "Niveau" };
  const count = (await fetchExercises(level.code).catch(() => [])).length;
  const description = `${LEVEL_INTROS[level.code] ?? ""} ${plural(count, "exercice")} avec indications.`.trim();
  return {
    title: heading(level),
    description,
    alternates: { canonical: levelPath(level.code) },
    openGraph: { title: heading(level), description, url: levelPath(level.code), images: [SHARE_IMAGE] },
  };
}

export default async function LevelPage({ params }: Props) {
  const { code } = await params;
  let data;
  try {
    const level = await findLevel(code);
    if (!level) notFound();
    const [exercises, topics] = await Promise.all([fetchExercises(level.code), fetchTopics()]);
    data = { level, exercises, topics };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { level, exercises, topics } = data;
  // Les chapitres présents à ce niveau, dans l'ordre du catalogue.
  const present = new Set(exercises.flatMap((exercise) => exercise.topics));
  const chapters = topics.filter((topic) => present.has(topic.name));
  const browse = `/exercices?niveau=${level.code}`;

  return (
    <>
      <JsonLd data={breadcrumb([["Accueil", "/"], ["Exercices", "/exercices"], [level.name, levelPath(level.code)]])} />
      <nav aria-label="Fil d'Ariane" className="text-sm text-mute">
        <Link href="/exercices" className="hover:text-ink">
          Exercices
        </Link>{" "}
        / {level.name}
      </nav>
      <h1 className="mt-3">{heading(level)}</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">{LEVEL_INTROS[level.code]}</p>

      {chapters.length > 0 && (
        <p className="mt-6 flex flex-wrap items-center gap-2 text-sm">
          <span className="mr-1 text-mute">Par chapitre :</span>
          {chapters.map((topic) => (
            <Link
              key={topic.slug}
              href={chapterPath(topic.slug)}
              className="rounded-full bg-surface-card px-3 py-1 text-ink hover:bg-surface-dark-elevated"
            >
              {topic.name}
            </Link>
          ))}
        </p>
      )}

      <section aria-labelledby="liste" className="mt-10">
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h2 id="liste">{plural(exercises.length, "exercice")}</h2>
          <p className="flex gap-4 text-sm text-mute">
            <Link href={`${browse}&tri=populaires`} className="hover:text-ink">
              Les plus populaires
            </Link>
            <Link href={`${browse}&tri=sans-solution`} className="hover:text-ink">
              Sans solution validée
            </Link>
          </p>
        </div>
        {exercises.length === 0 ? (
          <p className="text-mute">
            Aucun exercice à ce niveau pour l&apos;instant.{" "}
            <Link href="/exercices/nouveau" className="text-ink underline decoration-stone underline-offset-4">
              Publier le premier
            </Link>
          </p>
        ) : (
          <ExerciseList exercises={exercises} />
        )}
      </section>
    </>
  );
}
