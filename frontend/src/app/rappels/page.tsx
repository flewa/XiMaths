import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { type CourseNoteSummary, fetchCourseNotes, fetchMe, nullOnError } from "@/lib/api";
import { CONVENTIONS, CYCLES, courseNotePath, frenchSpacing } from "@/lib/course-notes";

export const metadata: Metadata = {
  title: "Rappels de cours de prépa, sup et spé",
  description:
    "Le programme de prépa scientifique chapitre par chapitre : définitions, théorèmes avec leurs hypothèses exactes, méthodes et pièges fréquents.",
  alternates: { canonical: "/rappels" },
};

function NoteList({ notes, review }: { notes: CourseNoteSummary[]; review: boolean }) {
  return (
    <ol className="mt-3 border-t border-hairline">
      {notes.map((note) => (
        <li key={note.slug} className="border-b border-hairline">
          <Link
            href={courseNotePath(note.slug)}
            className="-mx-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 rounded-lg px-3 py-3 hover:bg-hover"
          >
            <span className="font-serif text-lg text-ink-deep">{note.title}</span>
            <span className="text-sm text-mute">{note.programs}</span>
            {review && (
              <span
                className={`ml-auto rounded-full px-2 py-0.5 text-xs font-medium ${
                  note.published ? "bg-surface-card text-body" : "bg-accent-soft text-accent-text"
                }`}
              >
                {note.published ? "Publiée" : "Brouillon"}
              </span>
            )}
          </Link>
        </li>
      ))}
    </ol>
  );
}

export default async function CourseNotesPage() {
  let data;
  try {
    const [notes, me] = await Promise.all([fetchCourseNotes(), fetchMe().catch(nullOnError)]);
    data = { notes, me };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { notes, me } = data;
  // Rien de publié, et pas de l'équipe : la page n'existe pas encore pour ce visiteur.
  if (notes.length === 0) notFound();
  // L'équipe voit l'état de chaque fiche, brouillons compris.
  const review = me?.is_staff ?? false;
  const drafts = notes.filter((note) => !note.published).length;

  return (
    <>
      <h1>Rappels de cours</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">
        Le programme de prépa scientifique, chapitre par chapitre : définitions, théorèmes avec leurs hypothèses
        exactes, méthodes et pièges fréquents. De quoi revoir le cours avant d&apos;attaquer les exercices.
      </p>
      <p className="mt-3 max-w-[65ch] text-sm text-mute">
        Pour l&apos;instant, les fiches couvrent la prépa scientifique (MPSI, PCSI, MP, PSI). La licence, le master,
        la BCPST et les prépas ECG et B/L viendront ensuite ; leurs exercices sont déjà sur le site.
      </p>
      {review && drafts > 0 && (
        <p className="mt-6 rounded-lg bg-accent-soft px-3 py-2 text-sm text-accent-text">
          {drafts} {drafts > 1 ? "fiches en brouillon, visibles" : "fiche en brouillon, visible"} de l&apos;équipe
          seulement. Ouvre une fiche, relis-la, puis publie-la depuis sa page.
        </p>
      )}

      <details className="mt-8 text-sm">
        <summary className="font-medium text-ink">Conventions communes aux fiches</summary>
        <div className="mt-2 text-body">
          <MathMarkdown>{frenchSpacing(CONVENTIONS)}</MathMarkdown>
        </div>
      </details>

      {CYCLES.map(({ cycle, label }) => {
        const ofCycle = notes.filter((note) => note.cycle === cycle);
        if (ofCycle.length === 0) return null;
        return (
          <section key={cycle} aria-labelledby={`cycle-${cycle}`} className="mt-10">
            <h2 id={`cycle-${cycle}`}>{label}</h2>
            <NoteList notes={ofCycle} review={review} />
          </section>
        );
      })}
    </>
  );
}
