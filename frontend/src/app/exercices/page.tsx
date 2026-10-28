import type { Metadata } from "next";

import { ApiUnavailable } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { FilterChip, Tabs } from "@/components/FilterChip";
import { fetchExercises, fetchLevels, type ExerciseSort } from "@/lib/api";

export const metadata: Metadata = { title: "Parcourir les exercices" };

// Valeurs de ?tri= dans l'adresse, et tri correspondant de l'API.
const SORTS: { value: string; sort: ExerciseSort; label: string }[] = [
  { value: "recents", sort: "recent", label: "Récents" },
  { value: "populaires", sort: "popular", label: "Populaires" },
  { value: "sans-solution", sort: "unsolved", label: "Sans solution validée" },
];

function browseHref(niveau: string | undefined, tri: string) {
  const query = new URLSearchParams();
  if (niveau) query.set("niveau", niveau);
  if (tri !== SORTS[0].value) query.set("tri", tri);
  const search = query.toString();
  return search ? `/exercices?${search}` : "/exercices";
}

export default async function BrowsePage({
  searchParams,
}: {
  searchParams: Promise<{ niveau?: string; tri?: string }>;
}) {
  const { niveau, tri } = await searchParams;
  const current = SORTS.find((sort) => sort.value === tri) ?? SORTS[0];
  let data;
  try {
    data = await Promise.all([fetchLevels(), fetchExercises(niveau, current.sort)]);
  } catch (error) {
    console.error(error);
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

      <Tabs label="Filtrer par niveau" className="mt-10">
        <FilterChip href={browseHref(undefined, current.value)} label="Tous" active={!niveau} />
        {levels.map((level) => (
          <FilterChip
            key={level.code}
            href={browseHref(level.code, current.value)}
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
            href={browseHref(niveau, sort.value)}
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
