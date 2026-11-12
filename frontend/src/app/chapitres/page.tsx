import type { Metadata } from "next";
import Link from "next/link";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { fetchTopics } from "@/lib/api";
import { plural } from "@/lib/labels";
import { chapterPath, notionsOf, topicIntro } from "@/lib/seo-pages";
import { SHARE_IMAGE } from "@/lib/site";

const description =
  "Tous les chapitres de maths du supérieur, de l'analyse aux probabilités, et leurs notions : choisis-en un pour voir ses exercices, de la L1 au M2 et en prépa.";

export const metadata: Metadata = {
  title: "Exercices par chapitre",
  description,
  alternates: { canonical: "/chapitres" },
  openGraph: { title: "Exercices par chapitre", description, url: "/chapitres", images: [SHARE_IMAGE] },
};

/** Sommaire des chapitres : la page qu'on attend en tapant l'adresse, et une entrée de plus
 * pour les moteurs. */
export default async function ChaptersPage() {
  let topics;
  try {
    topics = await fetchTopics();
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const chapters = topics.filter((topic) => topic.parent === null);

  return (
    <>
      <JsonLd
        data={breadcrumb([
          ["Accueil", "/"],
          ["Chapitres", "/chapitres"],
        ])}
      />
      <h1>Exercices par chapitre</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">
        Choisis un chapitre, ou directement une notion, pour voir ses exercices.
      </p>
      {chapters.length === 0 ? (
        <p className="mt-8 text-mute">Aucun chapitre pour l&apos;instant.</p>
      ) : (
        <ul className="mt-8 divide-y divide-hairline border-y border-hairline">
          {chapters.map((chapter) => {
            const notions = notionsOf(topics, chapter.slug);
            return (
              <li key={chapter.slug} className="py-5">
                <h2 className="text-xl">
                  <Link href={chapterPath(chapter.slug)} className="hover:underline">
                    {chapter.name}
                  </Link>{" "}
                  <span className="font-sans text-sm text-mute">{plural(chapter.exercises, "exercice")}</span>
                </h2>
                {topicIntro(chapter.slug) && <p className="mt-1 max-w-[65ch] text-sm text-body">{topicIntro(chapter.slug)}</p>}
                {notions.length > 0 && (
                  <p className="mt-3 flex flex-wrap gap-2 text-sm">
                    {notions.map((notion) => (
                      <Link
                        key={notion.slug}
                        href={chapterPath(notion.slug)}
                        className="inline-flex min-h-8 items-center rounded-full bg-surface-card px-3 text-ink hover:bg-surface-dark-elevated"
                      >
                        {notion.name}&nbsp;<span className="text-mute">{notion.exercises}</span>
                      </Link>
                    ))}
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
