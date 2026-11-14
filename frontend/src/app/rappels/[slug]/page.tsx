import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import { CourseNoteReview } from "@/components/CourseNotes";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { MathMarkdown } from "@/components/MathMarkdown";
import { fetchCourseNote, fetchCourseNotes, fetchDemonstrations, fetchMe, nullOnError } from "@/lib/api";
import { courseNotePath, cycleOf, demonstrationPath, frenchSpacing, neighbours } from "@/lib/course-notes";
import { chapterPath, ofChapter } from "@/lib/seo-pages";
import { SHARE_IMAGE } from "@/lib/site";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const note = await fetchCourseNote(slug).catch(nullOnError);
  if (!note) return { title: "Rappels de cours" };
  const cycle = cycleOf(note);
  const title = `${note.title} : rappels de cours (${cycle.short}, ${note.programs})`;
  const description = `${note.title}, rappels de cours de prépa ${cycle.short.toLowerCase()} (${note.programs}) : définitions, théorèmes avec leurs hypothèses, méthodes et pièges fréquents.`;
  return {
    title,
    description,
    alternates: { canonical: courseNotePath(note.slug) },
    openGraph: { title, description, url: courseNotePath(note.slug), images: [SHARE_IMAGE] },
    // Un brouillon n'est servi qu'à l'équipe ; il ne doit jamais être indexé.
    ...(note.published ? {} : { robots: { index: false, follow: false } }),
  };
}

export default async function CourseNotePage({ params }: Props) {
  const { slug } = await params;
  let data;
  try {
    const [note, notes, me] = await Promise.all([
      fetchCourseNote(slug),
      fetchCourseNotes(),
      fetchMe().catch(nullOnError),
    ]);
    if (!note) notFound();
    // Une démonstration a sa propre adresse.
    if (note.kind === "demonstration") permanentRedirect(demonstrationPath(note.slug));
    // Les démonstrations du même chapitre, pour aller plus loin que le rappel.
    const proofs = note.topic ? await fetchDemonstrations(note.topic) : [];
    data = { note, notes, me, proofs };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { note, notes, me, proofs } = data;
  const cycle = cycleOf(note);
  const { previous, next } = neighbours(notes, note.slug);

  return (
    <article>
      {note.published && (
        <JsonLd
          data={breadcrumb([
            ["Accueil", "/"],
            ["Rappels de cours", "/rappels"],
            [note.title, courseNotePath(note.slug)],
          ])}
        />
      )}
      <nav aria-label="Fil d'Ariane" className="text-sm text-mute">
        <Link href="/rappels" className="hover:text-ink">
          Rappels de cours
        </Link>{" "}
        / {cycle.label}
      </nav>
      <h1 className="mt-3">{note.title}</h1>
      <p className="mt-3 text-mute">
        {cycle.label} · {note.programs}
      </p>
      {me?.is_staff && <CourseNoteReview slug={note.slug} published={note.published} />}

      <div className="course-note mt-8">
        <MathMarkdown>{frenchSpacing(note.body)}</MathMarkdown>
      </div>

      {note.topic && note.topic_name && (
        <div className="mt-10 space-y-2 rounded-xl bg-surface-soft px-5 py-4">
          <p>
            <Link href={chapterPath(note.topic)} className="font-medium text-ink underline underline-offset-4">
              S&apos;entraîner : exercices {ofChapter(note.topic_name)}
            </Link>
          </p>
          {proofs.map((proof) => (
            <p key={proof.slug}>
              <Link href={demonstrationPath(proof.slug)} className="font-medium text-ink underline underline-offset-4">
                Démonstration : {proof.title}
              </Link>
            </p>
          ))}
        </div>
      )}

      {(previous || next) && (
        <nav aria-label="Fiches voisines" className="mt-8 flex flex-wrap justify-between gap-4 text-sm">
          {previous ? (
            <Link href={courseNotePath(previous.slug)} className="text-mute hover:text-ink">
              ← {previous.title}
            </Link>
          ) : (
            <span />
          )}
          {next && (
            <Link href={courseNotePath(next.slug)} className="text-mute hover:text-ink">
              {next.title} →
            </Link>
          )}
        </nav>
      )}
    </article>
  );
}
