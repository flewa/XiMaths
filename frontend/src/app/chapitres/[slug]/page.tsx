import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { fetchExercises, fetchLevels, fetchTopics, type Topic } from "@/lib/api";
import { plural } from "@/lib/labels";
import { CHAPTER_INTROS, chapterPath, levelPath, ofChapter } from "@/lib/seo-pages";
import { SHARE_IMAGE } from "@/lib/site";

type Props = { params: Promise<{ slug: string }> };

async function findTopic(slug: string) {
  const topics = await fetchTopics();
  return topics.find((topic) => topic.slug === slug) ?? null;
}

/** « Exercices d'algèbre linéaire, de la L1 au M2 et en prépa ». */
function heading(topic: Topic) {
  return `Exercices ${ofChapter(topic.name)}`;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const topic = await findTopic(slug).catch(() => null);
  if (!topic) return { title: "Chapitre" };
  const count = (await fetchExercises(undefined, "recent", topic.slug).catch(() => [])).length;
  const title = `${heading(topic)}, de la L1 au M2 et en prépa`;
  const description = `${CHAPTER_INTROS[topic.slug] ?? ""} ${plural(count, "exercice")} avec indications.`.trim();
  return {
    title,
    description,
    alternates: { canonical: chapterPath(topic.slug) },
    openGraph: { title, description, url: chapterPath(topic.slug), images: [SHARE_IMAGE] },
  };
}

export default async function ChapterPage({ params }: Props) {
  const { slug } = await params;
  let data;
  try {
    const topic = await findTopic(slug);
    if (!topic) notFound();
    const [exercises, levels] = await Promise.all([fetchExercises(undefined, "recent", topic.slug), fetchLevels()]);
    data = { topic, exercises, levels };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { topic, exercises, levels } = data;
  const present = new Set(exercises.flatMap((exercise) => exercise.levels));
  const reached = levels.filter((level) => present.has(level.code));

  return (
    <>
      <JsonLd data={breadcrumb([["Accueil", "/"], ["Exercices", "/exercices"], [topic.name, chapterPath(topic.slug)]])} />
      <nav aria-label="Fil d'Ariane" className="text-sm text-mute">
        <Link href="/exercices" className="hover:text-ink">
          Exercices
        </Link>{" "}
        / {topic.name}
      </nav>
      <h1 className="mt-3">{heading(topic)}</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">{CHAPTER_INTROS[topic.slug]}</p>

      {reached.length > 0 && (
        <p className="mt-6 flex flex-wrap items-center gap-2 text-sm">
          <span className="mr-1 text-mute">Par niveau :</span>
          {reached.map((level) => (
            <Link
              key={level.code}
              href={levelPath(level.code)}
              title={level.name}
              className="rounded-full bg-surface-card px-3 py-1 text-ink hover:bg-surface-dark-elevated"
            >
              {level.code}
            </Link>
          ))}
        </p>
      )}

      <section aria-labelledby="liste" className="mt-10">
        <h2 id="liste" className="mb-4">
          {plural(exercises.length, "exercice")}
        </h2>
        {exercises.length === 0 ? (
          <p className="text-mute">Aucun exercice dans ce chapitre pour l&apos;instant.</p>
        ) : (
          <ExerciseList exercises={exercises} />
        )}
      </section>
    </>
  );
}
