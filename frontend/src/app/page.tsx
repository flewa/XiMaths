import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { FilterChip, Tabs } from "@/components/FilterChip";
import { fetchFeed, fetchLevels, fetchMe, type FeedItem } from "@/lib/api";

// Valeur de ?niveau= pour le fil de tous les niveaux.
const ALL_LEVELS = "tous";

function composition(feed: FeedItem[]) {
  const count = (reason: FeedItem["reason"]) => feed.filter((item) => item.reason === reason).length;
  return `${count("tendance")} tendances · ${count("a_resoudre")} à résoudre · ${count("exploration")} à découvrir`;
}

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
    data = { levels, level, feed: await fetchFeed(level) };
  } catch (error) {
    console.error(error);
    return <ApiUnavailable />;
  }
  const { levels, level, feed } = data;
  if (!feed) notFound();
  const browseHref = level ? `/exercices?niveau=${level}` : "/exercices";

  return (
    <>
      {/* La seule surface sombre de la page : un terminal qui annonce le fil. */}
      <section aria-labelledby="accroche" className="-mx-4 bg-surface-dark px-4 py-10 text-on-dark sm:mx-0 sm:px-8 sm:py-14">
        <p className="text-sm text-ash">ximaths ~ fil {level ? `--niveau ${level}` : "--tous-niveaux"}</p>
        <h1 id="accroche" className="mt-3 max-w-[30ch]">
          Des maths du supérieur, résolues et relues par la communauté.
        </h1>
        <p className="mt-8 rounded-sm bg-surface-dark-elevated px-3 py-2">
          <span className="text-ash">│ </span>
          {feed.length === 0 ? "aucun exercice à ce niveau pour l'instant" : composition(feed)}
        </p>
        <p className="mt-4 flex flex-wrap gap-x-6 gap-y-1 text-sm text-ash">
          <Link href="/exercices/nouveau" className="hover:text-on-dark">
            [+] publier un exercice
          </Link>
          <Link href={browseHref} className="hover:text-on-dark">
            [&gt;] parcourir le catalogue
          </Link>
          <Link href="/classements" className="hover:text-on-dark">
            [#] classements
          </Link>
        </p>
      </section>

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
