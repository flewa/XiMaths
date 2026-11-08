import type { Metadata } from "next";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { FilterChip, Tabs } from "@/components/FilterChip";
import { SearchBox } from "@/components/SearchBox";
import { fetchExercises, fetchLevels, type ExerciseSort } from "@/lib/api";
import { plural } from "@/lib/labels";
import { levelPath } from "@/lib/seo-pages";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ niveau?: string }>;
}): Promise<Metadata> {
  const { niveau } = await searchParams;
  return {
    title: "Parcourir les exercices",
    description:
      "Tous les exercices de maths du supérieur publiés sur XiMaths, de la L1 au M2 et en prépa : récents, populaires, ou sans solution validée.",
    // Les variantes filtrées ou triées renvoient à une seule adresse : la page du niveau, ou le catalogue.
    alternates: { canonical: niveau ? levelPath(niveau) : "/exercices" },
  };
}

// Valeurs de ?tri= dans l'adresse, et tri correspondant de l'API.
const SORTS: { value: string; sort: ExerciseSort; label: string }[] = [
  { value: "recents", sort: "recent", label: "Récents" },
  { value: "populaires", sort: "popular", label: "Populaires" },
  { value: "sans-solution", sort: "unsolved", label: "Sans solution validée" },
];

function browseHref(niveau: string | undefined, tri: string, q?: string) {
  const query = new URLSearchParams();
  if (q) query.set("q", q);
  if (niveau) query.set("niveau", niveau);
  if (tri !== SORTS[0].value) query.set("tri", tri);
  const search = query.toString();
  return search ? `/exercices?${search}` : "/exercices";
}

export default async function BrowsePage({
  searchParams,
}: {
  searchParams: Promise<{ niveau?: string; tri?: string; q?: string }>;
}) {
  const { niveau, tri } = await searchParams;
  const q = (await searchParams).q?.trim() || undefined;
  const current = SORTS.find((sort) => sort.value === tri) ?? SORTS[0];
  let data;
  try {
    data = await Promise.all([fetchLevels(), fetchExercises(niveau, current.sort, undefined, q)]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [levels, exercises] = data;

  return (
    <>
      <h1>Parcourir les exercices</h1>
      <p className="mt-2 text-body">
        Populaires : classés par nombre de solutions et de votes, de façon logarithmique, pour que
        les exercices déjà très vus n&apos;écrasent pas les autres.
      </p>
      <SearchBox id="recherche-catalogue" defaultValue={q ?? ""} className="mt-6 max-w-[28rem]" />
      {q && (
        <p className="mt-4 text-body">
          {plural(exercises.length, "exercice")} pour « {q} ».{" "}
          <a href={browseHref(niveau, current.value)} className="text-mute underline underline-offset-4 hover:text-ink">
            Effacer la recherche
          </a>
        </p>
      )}

      <Tabs label="Filtrer par niveau" className="mt-10">
        <FilterChip href={browseHref(undefined, current.value, q)} label="Tous" active={!niveau} />
        {levels.map((level) => (
          <FilterChip
            key={level.code}
            href={browseHref(level.code, current.value, q)}
            label={level.code}
            title={level.name}
            active={niveau === level.code}
          />
        ))}
      </Tabs>
      <Tabs label="Trier" className="mt-2">
        {SORTS.map((sort) => (
          <FilterChip
            key={sort.value}
            href={browseHref(niveau, sort.value, q)}
            label={sort.label}
            active={sort.value === current.value}
          />
        ))}
      </Tabs>

      {exercises.length === 0 ? (
        <p className="py-6 text-mute">Aucun exercice ici pour l&apos;instant.</p>
      ) : (
        <ExerciseList exercises={exercises} />
      )}
    </>
  );
}
