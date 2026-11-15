import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import { CourseNoteReview } from "@/components/CourseNotes";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { MathMarkdown } from "@/components/MathMarkdown";
import { fetchCourseNote, fetchCourseNotes, fetchDemonstrations, fetchMe, nullOnError } from "@/lib/api";
import { PROOF_STATUS, courseNotePath, demonstrationPath, frenchSpacing, neighbours } from "@/lib/course-notes";
import { chapterPath, ofChapter } from "@/lib/seo-pages";
import { SHARE_IMAGE } from "@/lib/site";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const proof = await fetchCourseNote(slug).catch(nullOnError);
  if (!proof || proof.kind !== "demonstration") return { title: "Démonstrations" };
  const title = `${proof.title} : démonstration`;
  const description = `Démonstration complète, étape par étape : ${proof.title} (niveau ${proof.programs}).`;
  return {
    title,
    description,
    alternates: { canonical: demonstrationPath(proof.slug) },
    openGraph: { title, description, url: demonstrationPath(proof.slug), images: [SHARE_IMAGE] },
    // Un brouillon n'est servi qu'à l'équipe ; il ne doit jamais être indexé.
    ...(proof.published ? {} : { robots: { index: false, follow: false } }),
  };
}

export default async function DemonstrationPage({ params }: Props) {
  const { slug } = await params;
  let data;
  try {
    const [proof, proofs, me] = await Promise.all([
      fetchCourseNote(slug),
      fetchDemonstrations(),
      fetchMe().catch(nullOnError),
    ]);
    if (!proof) notFound();
    // Une fiche de rappels a sa propre adresse.
    if (proof.kind !== "demonstration") permanentRedirect(courseNotePath(proof.slug));
    // La fiche du même chapitre, pour revoir le cours autour du théorème.
    const notes = proof.topic ? await fetchCourseNotes(proof.topic) : [];
    data = { proof, proofs, me, notes };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { proof, proofs, me, notes } = data;
  const { previous, next } = neighbours(proofs, proof.slug);
  const status = proof.status ? PROOF_STATUS[proof.status] : null;

  return (
    <article>
      {proof.published && (
        <JsonLd
          data={breadcrumb([
            ["Accueil", "/"],
            ["Démonstrations", "/demonstrations"],
            [proof.title, demonstrationPath(proof.slug)],
          ])}
        />
      )}
      <nav aria-label="Fil d'Ariane" className="text-sm text-mute">
        <Link href="/demonstrations" className="hover:text-ink">
          Démonstrations
        </Link>
        {proof.topic_name && <> / {proof.topic_name}</>}
      </nav>
      <h1 className="mt-3">{proof.title}</h1>
      <p className="mt-3 text-mute">
        {status ? status.label : "Démonstration"} · niveau {proof.programs}
      </p>
      {me?.is_staff && <CourseNoteReview slug={proof.slug} published={proof.published} noun="démonstration" />}

      <div className="course-note mt-8">
        <MathMarkdown>{frenchSpacing(proof.body)}</MathMarkdown>
      </div>

      {(notes.length > 0 || (proof.topic && proof.topic_name)) && (
        <div className="mt-10 space-y-2 rounded-xl bg-surface-soft px-5 py-4">
          {notes.map((note) => (
            <p key={note.slug}>
              <Link href={courseNotePath(note.slug)} className="font-medium text-ink underline underline-offset-4">
                Revoir le cours : {note.title}
              </Link>
            </p>
          ))}
          {proof.topic && proof.topic_name && (
            <p>
              <Link href={chapterPath(proof.topic)} className="font-medium text-ink underline underline-offset-4">
                S&apos;entraîner : exercices {ofChapter(proof.topic_name)}
              </Link>
            </p>
          )}
        </div>
      )}

      {(previous || next) && (
        <nav aria-label="Démonstrations voisines" className="mt-8 flex flex-wrap justify-between gap-4 text-sm">
          {previous ? (
            <Link href={demonstrationPath(previous.slug)} className="text-mute hover:text-ink">
              ← {previous.title}
            </Link>
          ) : (
            <span />
          )}
          {next && (
            <Link href={demonstrationPath(next.slug)} className="text-mute hover:text-ink">
              {next.title} →
            </Link>
          )}
        </nav>
      )}
    </article>
  );
}
