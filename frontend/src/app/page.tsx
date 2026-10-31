import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { FilterChip, Tabs } from "@/components/FilterChip";
import { HowItWorks, MemberHero, VisitorHero } from "@/components/HomeHero";
import { fetchDailyChallenges, fetchFeed, fetchLevels, fetchMe, fetchProgress } from "@/lib/api";

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
      {/* La seule surface sombre de la page : un terminal, qui accueille ou dit quoi faire. */}
      {me ? (
        <MemberHero me={me} progress={progress} challenges={challenges} level={level} browseHref={browseHref} />
      ) : (
        <>
          <VisitorHero feed={feed} level={level} browseHref={browseHref} />
          <HowItWorks />
        </>
      )}

      <h2 className="sr-only">Le fil</h2>
      <Tabs label="Choisir un niveau" className="mt-12">
        <FilterChip href={`/?niveau=${ALL_LEVELS}`} label="Tous" active={!level} />
        {levels.map((item) => (
          <FilterChip
            key={item.code}
            href={`/?niveau=${item.code}`}
            label={item.code}
            title={item.name}
            active={level === item.code}
          />
        ))}
      </Tabs>

      <p className="py-3 text-sm text-mute">
        Le fil mélange les exercices en vogue, des exercices récents qui attendent leurs premières
        solutions, et des nouveautés tirées au hasard.
      </p>

      {feed.length === 0 ? (
        <p className="border-t border-hairline py-6">
          Aucun exercice publié à ce niveau.{" "}
          <Link href="/exercices/nouveau" className="underline underline-offset-4">
            Publier le premier
          </Link>
        </p>
      ) : (
        <div className="border-t border-hairline">
          <ExerciseList exercises={feed} />
        </div>
      )}

      <p className="mt-6">
        <Link href={browseHref} className="underline underline-offset-4">
          Tout le catalogue{level ? ` de ${level}` : ""} : récents, populaires, sans solution →
        </Link>
      </p>
    </>
  );
}
