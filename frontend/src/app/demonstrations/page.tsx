import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { type CourseNoteSummary, fetchDemonstrations, fetchMe, nullOnError } from "@/lib/api";
import { PROOF_STATUS, demonstrationPath, proofSections } from "@/lib/course-notes";

export const metadata: Metadata = {
  title: "Démonstrations de théorèmes, niveau MP et L2",
  description:
    "Les démonstrations complètes des grands théorèmes de MP et de L2 : réduction, séries entières, suites de fonctions, probabilités, et des classiques hors programme.",
  alternates: { canonical: "/demonstrations" },
};

function ProofList({ proofs, review }: { proofs: CourseNoteSummary[]; review: boolean }) {
  return (
    <ol className="mt-3 border-t border-hairline">
      {proofs.map((proof) => (
        <li key={proof.slug} className="border-b border-hairline">
          <Link
            href={demonstrationPath(proof.slug)}
            className="-mx-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 rounded-lg px-3 py-3 hover:bg-hover"
          >
            <span className="font-serif text-lg text-ink-deep">{proof.title}</span>
            {proof.topic_name && <span className="text-sm text-mute">{proof.topic_name}</span>}
            <span className="ml-auto flex flex-wrap gap-2">
              {proof.status === "preuve-hors-programme" && (
                <span className="rounded-full bg-surface-card px-2 py-0.5 text-xs font-medium text-body">
                  {PROOF_STATUS[proof.status].short}
                </span>
              )}
              {review && (
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    proof.published ? "bg-surface-card text-body" : "bg-accent-soft text-accent-text"
                  }`}
                >
                  {proof.published ? "Publiée" : "Brouillon"}
                </span>
              )}
            </span>
          </Link>
        </li>
      ))}
    </ol>
  );
}

export default async function DemonstrationsPage() {
  let data;
  try {
    const [proofs, me] = await Promise.all([fetchDemonstrations(), fetchMe().catch(nullOnError)]);
    data = { proofs, me };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { proofs, me } = data;
  // Rien de publié, et pas de l'équipe : la page n'existe pas encore pour ce visiteur.
  if (proofs.length === 0) notFound();
  const review = me?.is_staff ?? false;
  const drafts = proofs.filter((proof) => !proof.published).length;

  return (
    <>
      <h1>Démonstrations</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">
        Les démonstrations complètes des grands théorèmes de deuxième année (MP, MPI) et de L2, étape par étape,
        puis quelques classiques qui sortent du cours.
      </p>
      <p className="mt-3 max-w-[65ch] text-sm text-mute">
        Chaque démonstration indique sa place dans le programme de prépa (MPSI, MP) : à savoir refaire, énoncé au
        programme dont la preuve ne l&apos;est pas, ou hors programme.
      </p>
      {review && drafts > 0 && (
        <p className="mt-6 rounded-lg bg-accent-soft px-3 py-2 text-sm text-accent-text">
          {drafts} {drafts > 1 ? "démonstrations en brouillon, visibles" : "démonstration en brouillon, visible"} de
          l&apos;équipe seulement. Ouvre-les, relis-les, puis publie-les depuis leur page.
        </p>
      )}

      {proofSections(proofs).map((section) => (
        <section key={section.id} aria-labelledby={`partie-${section.id}`} className="mt-10">
          <h2 id={`partie-${section.id}`}>{section.title}</h2>
          <ProofList proofs={section.proofs} review={review} />
        </section>
      ))}
    </>
  );
}
