import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { HowItWorks, MemberHero, VisitorHero } from "@/components/HomeHero";
import { JsonLd } from "@/components/JsonLd";
import { LevelPicker } from "@/components/LevelPicker";
import { fetchDailyChallenges, fetchFeed, fetchLevels, fetchMe, fetchProgress } from "@/lib/api";
import { SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: { absolute: "XiMaths · Exercices de maths du supérieur, de la L1 au M2 et en prépa" },
  // Le fil filtré par niveau (?niveau=) reste la même page pour un moteur de recherche.
  alternates: { canonical: "/" },
};

// Nom du site et logo dans les résultats de recherche.
const SITE_DATA = [
  { "@context": "https://schema.org", "@type": "WebSite", name: "XiMaths", url: `${SITE_URL}/`, inLanguage: "fr" },
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "XiMaths",
    url: `${SITE_URL}/`,
    logo: `${SITE_URL}/icons/icon-512.png`,
  },
];

// Valeur de ?niveau= pour le fil de tous les niveaux.
const ALL_LEVELS = "tous";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ niveau?: string }>;
}) {
  const { niveau } = await searchParams;
  let data;
  try {
    const [levels, me] = await Promise.all([fetchLevels(), fetchMe()]);
    // Par défaut, le fil du niveau déclaré.
    const level = niveau === ALL_LEVELS ? undefined : (niveau ?? me?.declared_level ?? undefined);
    const [feed, progress, challenges] = await Promise.all([
      fetchFeed(level),
      me ? fetchProgress() : null,
      me ? fetchDailyChallenges() : [],
    ]);
    data = { levels, me, level, feed, progress, challenges };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { levels, me, level, feed, progress, challenges } = data;
  if (!feed) notFound();
  const browseHref = level ? `/exercices?niveau=${level}` : "/exercices";

  return (
    <>
      <JsonLd data={SITE_DATA} />
      {me ? (
        <MemberHero me={me} progress={progress} challenges={challenges} />
      ) : (
        <>
          <VisitorHero />
          <HowItWorks />
        </>
      )}

      <section aria-labelledby="fil" className="mt-14">
        <div className="flex items-baseline justify-between gap-4">
          <h2 id="fil">Exercices</h2>
          <LevelPicker
            levels={levels}
            current={level}
            hrefFor={(code) => `/?niveau=${code ?? ALL_LEVELS}`}
          />
        </div>
        <p className="mb-4 mt-1.5 text-sm text-mute">
          Ceux dont on parle, ceux qui attendent leur première solution, et quelques nouveautés au hasard.
        </p>

        {feed.length === 0 ? (
          <p className="border-t border-hairline py-6 text-mute">
            Aucun exercice publié à ce niveau.{" "}
            <Link href="/exercices/nouveau" className="text-ink underline decoration-stone underline-offset-4">
              Publier le premier
            </Link>
          </p>
        ) : (
          <ExerciseList exercises={feed} />
        )}

        <p className="mt-5">
          <Link href={browseHref} className="text-mute underline decoration-stone underline-offset-4 hover:text-ink">
            Voir tout le catalogue{level ? ` de ${level}` : ""}
          </Link>
        </p>
      </section>
    </>
  );
}
