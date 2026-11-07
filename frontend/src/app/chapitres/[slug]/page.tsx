import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { type ExerciseSummary, type Level, type Topic, fetchExercises, fetchLevels, fetchTopics } from "@/lib/api";
import { plural } from "@/lib/labels";
import { chapterPath, levelPath, notionsOf, ofChapter, topicIntro } from "@/lib/seo-pages";
import { SHARE_IMAGE } from "@/lib/site";

type Props = { params: Promise<{ slug: string }> };

// Au-delà, le titre passerait la longueur qu'un moteur affiche.
const TITLE_LEVELS = 4;

async function load(slug: string) {
  const topics = await fetchTopics();
  const topic = topics.find((item) => item.slug === slug);
  if (!topic) return null;
  const parent = topic.parent ? (topics.find((item) => item.slug === topic.parent) ?? null) : null;
  return { topic, parent, topics };
}

/** Niveaux des exercices présents, dans l'ordre du site (L1… puis la prépa). */
function levelsOf(exercises: ExerciseSummary[], levels: Level[]) {
  const present = new Set(exercises.flatMap((exercise) => exercise.levels));
  return levels.filter((level) => present.has(level.code));
}

/** Chapitre : « Exercices d'analyse, de la L1 au M2 et en prépa ». Notion : « Exercices de
 * séries entières (L2, MP, PC, PSI…) », les niveaux qu'on y trouve vraiment. */
function title(topic: Topic, reached: Level[]) {
  const heading = `Exercices ${ofChapter(topic.name)}`;
  if (topic.parent === null) return `${heading}, de la L1 au M2 et en prépa`;
  if (reached.length === 0) return heading;
  const codes = reached.slice(0, TITLE_LEVELS).map((level) => level.code);
  return `${heading} (${codes.join(", ")}${reached.length > TITLE_LEVELS ? "…" : ""})`;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const found = await load(slug).catch(() => null);
  if (!found) return { title: "Chapitre" };
  const { topic } = found;
  const [exercises, levels] = await Promise.all([
    fetchExercises(undefined, "recent", topic.slug).catch(() => []),
    fetchLevels().catch(() => []),
  ]);
  const heading = title(topic, levelsOf(exercises, levels));
  const description = `${topicIntro(topic.slug)} ${plural(exercises.length, "exercice")} avec indications.`.trim();
  return {
    title: heading,
    description,
    alternates: { canonical: chapterPath(topic.slug) },
    openGraph: { title: heading, description, url: chapterPath(topic.slug), images: [SHARE_IMAGE] },
    // Une notion encore vide n'a rien à proposer à un moteur.
    ...(exercises.length === 0 ? { robots: { index: false, follow: true } } : {}),
  };
}

function TopicChips({ label, topics }: { label: string; topics: Topic[] }) {
  if (topics.length === 0) return null;
  return (
    <p className="mt-6 flex flex-wrap items-center gap-2 text-sm">
      <span className="mr-1 text-mute">{label}</span>
      {topics.map((topic) => (
        <Link
          key={topic.slug}
          href={chapterPath(topic.slug)}
          className="rounded-full bg-surface-card px-3 py-1 text-ink hover:bg-surface-dark-elevated"
        >
          {topic.name} <span className="text-mute">{topic.exercises}</span>
        </Link>
      ))}
    </p>
  );
}

export default async function ChapterPage({ params }: Props) {
  const { slug } = await params;
  let data;
  try {
    const found = await load(slug);
    if (!found) notFound();
    const [exercises, levels] = await Promise.all([
      fetchExercises(undefined, "recent", found.topic.slug),
      fetchLevels(),
    ]);
    data = { ...found, exercises, levels };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { topic, parent, topics, exercises, levels } = data;
  const reached = levelsOf(exercises, levels);
  const trail: [string, string][] = [
    ["Accueil", "/"],
    ["Exercices", "/exercices"],
    ...(parent ? [[parent.name, chapterPath(parent.slug)] as [string, string]] : []),
    [topic.name, chapterPath(topic.slug)],
  ];

  return (
    <>
      <JsonLd data={breadcrumb(trail)} />
      <nav aria-label="Fil d'Ariane" className="text-sm text-mute">
        <Link href="/exercices" className="hover:text-ink">
          Exercices
        </Link>
        {parent && (
          <>
            {" "}
            /{" "}
            <Link href={chapterPath(parent.slug)} className="hover:text-ink">
              {parent.name}
            </Link>
          </>
        )}{" "}
        / {topic.name}
      </nav>
      <h1 className="mt-3">Exercices {ofChapter(topic.name)}</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">{topicIntro(topic.slug)}</p>

      {/* Un chapitre s'ouvre sur ses notions, comme un sommaire ; une notion garde ses
          voisines pour après la liste, qui est ce qu'on vient chercher. */}
      {!parent && <TopicChips label="Par notion :" topics={notionsOf(topics, topic.slug)} />}

      {reached.length > 0 && (
        <p className="mt-4 flex flex-wrap items-center gap-2 text-sm">
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
          <p className="text-mute">
            Aucun exercice {parent ? "sur cette notion" : "dans ce chapitre"} pour l&apos;instant.
          </p>
        ) : (
          <ExerciseList exercises={exercises} />
        )}
      </section>

      {parent && (
        <TopicChips
          label={`Autres notions ${ofChapter(parent.name)} :`}
          topics={notionsOf(topics, parent.slug).filter((notion) => notion.slug !== topic.slug)}
        />
      )}
    </>
  );
}
