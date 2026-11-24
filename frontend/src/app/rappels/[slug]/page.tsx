import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import { CourseNoteReview } from "@/components/CourseNotes";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { MathMarkdown } from "@/components/MathMarkdown";
import { Outline } from "@/components/Outline";
import { fetchCourseNote, fetchCourseNotes, fetchDemonstrations, fetchMe, nullOnError } from "@/lib/api";
import {
  courseNotePath,
  cycleOf,
  demonstrationPath,
  frenchSpacing,
  neighbours,
  noteData,
  outline,
} from "@/lib/course-notes";
import { chapterPath, ofChapter } from "@/lib/seo-pages";
import { SHARE_IMAGE, SITE_URL } from "@/lib/site";

// Ce que tapent les élèves : « formulaire de trigonométrie », « primitives usuelles »,
// « résumé de cours » plutôt que « rappels ».
const FORMULA_SHEET = /usuel|classiques/i;

function noteHeading(title: string) {
  if (/^formulaire/i.test(title)) return title;
  return FORMULA_SHEET.test(title) ? `${title} : formulaire` : `${title} : résumé de cours`;
}

function describeNote(note: { title: string; programs: string }, cycle: string) {
  if (/^formulaire/i.test(note.title) || FORMULA_SHEET.test(note.title)) {
    return `${note.title} : toutes les formules à connaître en prépa ${cycle.toLowerCase()} et en licence (${note.programs}), avec leurs conditions de validité et les pièges fréquents.`;
  }
  return `${note.title} : résumé de cours de prépa ${cycle.toLowerCase()} (${note.programs}). Définitions, théorèmes avec leurs hypothèses exactes, formules, méthodes et pièges fréquents.`;
}

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const note = await fetchCourseNote(slug).catch(nullOnError);
  if (!note) return { title: "Rappels de cours" };
  const cycle = cycleOf(note);
  const title = `${noteHeading(note.title)} (${note.programs})`;
  const description = describeNote(note, cycle.short);
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
  const parts = outline(note.body);

  return (
    <article>
      {note.published && (
        <JsonLd
          data={[
            breadcrumb([
              ["Accueil", "/"],
              ["Rappels de cours", "/rappels"],
              [note.title, courseNotePath(note.slug)],
            ]),
            noteData(note, {
              url: courseNotePath(note.slug),
              description: describeNote(note, cycle.short),
              siteUrl: SITE_URL,
              topicUrl: note.topic ? `${SITE_URL}${chapterPath(note.topic)}` : null,
            }),
          ]}
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

      <Outline items={parts} />

      <div className="course-note mt-8">
        <MathMarkdown headingIds={parts.map((part) => part.id)}>{frenchSpacing(note.body)}</MathMarkdown>
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
            <Link href={courseNotePath(previous.slug)} className="inline-flex min-h-10 items-center text-body hover:text-ink">
              ← {previous.title}
            </Link>
          ) : (
            <span />
          )}
          {next && (
            <Link href={courseNotePath(next.slug)} className="inline-flex min-h-10 items-center text-body hover:text-ink">
              {next.title} →
            </Link>
          )}
        </nav>
      )}
    </article>
  );
}
