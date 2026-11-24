import type { Metadata } from "next";
import Link from "next/link";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Icon } from "@/components/Icon";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { type CourseNoteSummary, fetchCourseNotes, fetchDemonstrations } from "@/lib/api";
import { courseNotePath, demonstrationPath, isFormulaSheet } from "@/lib/course-notes";
import { pdfPath } from "@/lib/fiches-pdf";

export const metadata: Metadata = {
  title: "Fiches de révision de maths en PDF : prépa et licence",
  description:
    "Formulaires, résumés de cours et démonstrations de maths à télécharger en PDF et à imprimer : MPSI, MP2I, PCSI, MP, PSI, licence. Gratuit, sans inscription.",
  alternates: { canonical: "/fiches-revision" },
};

type Group = { id: string; title: string; intro: string; notes: CourseNoteSummary[] };

function Row({ note }: { note: CourseNoteSummary }) {
  const href = note.kind === "demonstration" ? demonstrationPath(note.slug) : courseNotePath(note.slug);
  return (
    <li className="flex flex-wrap items-center gap-x-4 gap-y-1 border-b border-hairline py-3">
      <span className="min-w-0 flex-1">
        <Link href={href} className="font-medium text-ink hover:underline">
          {note.title}
        </Link>
        <span className="block text-sm text-mute">{note.programs}</span>
      </span>
      <a
        href={pdfPath(note.slug)!}
        className="inline-flex min-h-10 items-center gap-1.5 rounded-lg bg-surface-card px-3 text-sm font-medium text-ink hover:bg-surface-dark-elevated"
        data-umami-event="fiche-pdf"
        data-umami-event-fiche={note.slug}
      >
        <Icon name="download" size={16} />
        PDF
      </a>
    </li>
  );
}

/** Toutes les fiches en PDF sur une page : ce que cherchent les élèves (« fiche révision
 * maths prépa pdf »), et ce qu'ils s'envoient. */
export default async function RevisionSheetsPage() {
  let data;
  try {
    data = await Promise.all([fetchCourseNotes(), fetchDemonstrations()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [notes, proofs] = data.map((list) => list.filter((note) => note.published && pdfPath(note.slug)));
  const groups: Group[] = [
    {
      id: "formulaires",
      title: "Formulaires",
      intro: "Les formules à connaître par cœur, avec leurs conditions de validité.",
      notes: notes.filter((note) => isFormulaSheet(note)),
    },
    {
      id: "sup",
      title: "Résumés de cours de première année",
      intro: "MPSI, MP2I, PCSI et L1 : définitions, théorèmes avec leurs hypothèses exactes, méthodes et pièges.",
      notes: notes.filter((note) => note.cycle === "sup" && !isFormulaSheet(note)),
    },
    {
      id: "spe",
      title: "Résumés de cours de deuxième année",
      intro: "MP, PSI et L2 : réduction, séries, intégrales à paramètre, probabilités…",
      notes: notes.filter((note) => note.cycle === "spe" && !isFormulaSheet(note)),
    },
    {
      id: "demonstrations",
      title: "Démonstrations",
      intro: "Les grands théorèmes prouvés pas à pas : énoncé, idée, démonstration complète.",
      notes: proofs,
    },
  ].filter((group) => group.notes.length > 0);

  return (
    <>
      <JsonLd
        data={breadcrumb([
          ["Accueil", "/"],
          ["Fiches de révision en PDF", "/fiches-revision"],
        ])}
      />
      <h1>Fiches de révision en PDF</h1>
      <p className="mt-4 max-w-[65ch] text-lg text-body">
        Formulaires, résumés de cours et démonstrations, à télécharger et à imprimer. Gratuit et sans inscription :
        partage-les avec ta classe.
      </p>
      <p className="mt-3 max-w-[65ch] text-sm text-mute">
        Chaque fiche renvoie, avec un QR code, à sa version en ligne et aux exercices du chapitre, que d&apos;autres
        étudiants corrigent.
      </p>
      <nav aria-label="Sections" className="mt-6 flex flex-wrap gap-2 text-sm">
        {groups.map((group) => (
          <a
            key={group.id}
            href={`#${group.id}`}
            className="inline-flex min-h-8 items-center rounded-full bg-surface-card px-3 text-body hover:bg-hover hover:text-ink"
          >
            {group.title} · {group.notes.length}
          </a>
        ))}
      </nav>
      {groups.map((group) => (
        <section key={group.id} id={group.id} aria-labelledby={`${group.id}-titre`} className="mt-12 scroll-mt-20">
          <h2 id={`${group.id}-titre`}>{group.title}</h2>
          <p className="mt-1 text-sm text-body">{group.intro}</p>
          <ul className="mt-3 border-t border-hairline">
            {group.notes.map((note) => (
              <Row key={note.slug} note={note} />
            ))}
          </ul>
        </section>
      ))}
    </>
  );
}
