import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Icon } from "@/components/Icon";
import { MathText } from "@/components/MathText";
import { PageIntro } from "@/components/PageIntro";
import { type MyReport, fetchMyReports } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Mes signalements" };

function day(iso: string) {
  return dateFormat.format(new Date(iso));
}

const STATUS: Record<MyReport["status"], { label: string; className: string }> = {
  ouvert: { label: "À traiter", className: "bg-surface-card text-body" },
  confirme: { label: "Confirmé", className: "text-success" },
  rejete: { label: "Non retenu", className: "text-mute" },
};

/** Ce qu'un signalement confirmé change, selon son motif. */
const OUTCOMES = [
  ["Erreur dans un énoncé", "le modérateur corrige l'exercice lui-même."],
  ["Doublon", "les deux exercices sont fusionnés, ou liés comme variantes."],
  ["Plagiat, contenu inapproprié", "le contenu est retiré ; son auteur en reçoit le motif et peut faire appel."],
  ["IA non déclarée", "les points de la copie sont annulés ; son auteur peut faire appel."],
];

function ReportRow({ report }: { report: MyReport }) {
  const status = STATUS[report.status];
  return (
    <li className="flex flex-wrap items-center gap-x-4 gap-y-1.5 py-3.5">
      <span className="min-w-0 flex-1 basis-64">
        <Link href={`/exercices/${report.exercise_id}`} className="font-medium text-ink hover:underline">
          <MathText>{report.title}</MathText>
        </Link>
        <span className="block text-sm text-mute">
          {report.reason_label} · signalé le {day(report.created_at)}
          {report.decided_at && ` · tranché le ${day(report.decided_at)}`}
        </span>
      </span>
      <span className="flex items-center gap-2 text-sm">
        {report.points > 0 && <span className="tabular-nums text-ink">+{report.points} points</span>}
        <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 font-medium ${status.className}`}>
          {report.status === "confirme" && <Icon name="check" size={14} />}
          {status.label}
        </span>
      </span>
    </li>
  );
}

export default async function MyReportsPage() {
  let reports;
  try {
    reports = await fetchMyReports();
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!reports) redirect("/connexion?suivant=/signalements");

  const open = reports.filter((report) => report.status === "ouvert");
  const settled = reports.filter((report) => report.status !== "ouvert");
  const confirmed = settled.filter((report) => report.status === "confirme").length;
  const points = reports.reduce((total, report) => total + report.points, 0);

  return (
    <div className="max-w-[720px]">
      <h1>Mes signalements</h1>
      <PageIntro id="signalements">
        Un modérateur examine chaque signalement, à la main. Un doublon, un plagiat ou une erreur confirmés
        rapportent 3 points. Personne d&apos;autre ne sait que c&apos;est toi qui as signalé.
      </PageIntro>

      {reports.length > 0 && (
        <dl className="mt-8 grid grid-cols-3 gap-3">
          {[
            { value: open.length, label: "à traiter" },
            { value: confirmed, label: confirmed > 1 ? "confirmés" : "confirmé" },
            { value: points, label: points > 1 ? "points gagnés" : "point gagné" },
          ].map((tile) => (
            <div key={tile.label} className="flex flex-col-reverse rounded-2xl bg-surface-soft px-4 py-3">
              <dt className="text-sm text-mute">{tile.label}</dt>
              <dd className="font-serif text-[2rem] leading-tight text-ink-deep tabular-nums">{tile.value}</dd>
            </div>
          ))}
        </dl>
      )}

      {reports.length === 0 ? (
        <div className="mt-8 rounded-2xl border border-dashed border-hairline-strong px-6 py-8">
          <p className="font-medium text-ink">Aucun signalement pour l&apos;instant.</p>
          <ul className="mt-3 space-y-1.5 text-sm text-body">
            <li>
              Sous chaque exercice, « Signaler » : une erreur dans l&apos;énoncé, un doublon, un plagiat.
            </li>
            <li>
              Quand tu relis une copie, « Signaler cette copie » : un plagiat, ou une IA non déclarée. Une copie
              fausse, elle, se juge dans ta relecture.
            </li>
          </ul>
        </div>
      ) : (
        <>
          {open.length > 0 && (
            <section aria-labelledby="a-traiter" className="mt-10">
              <h2 id="a-traiter">À traiter</h2>
              <ul className="mt-2 divide-y divide-hairline border-b border-hairline">
                {open.map((report) => (
                  <ReportRow key={report.id} report={report} />
                ))}
              </ul>
            </section>
          )}
          {settled.length > 0 && (
            <section aria-labelledby="traites" className="mt-10">
              <h2 id="traites">Traités</h2>
              <ul className="mt-2 divide-y divide-hairline border-b border-hairline">
                {settled.map((report) => (
                  <ReportRow key={report.id} report={report} />
                ))}
              </ul>
            </section>
          )}
        </>
      )}

      <details className="mt-10 text-sm text-mute">
        <summary className="hover:text-ink">Que se passe-t-il quand un signalement est confirmé ?</summary>
        <ul className="mt-3 space-y-1.5">
          {OUTCOMES.map(([reason, outcome]) => (
            <li key={reason}>
              <span className="text-ink">{reason}</span> : {outcome}
            </li>
          ))}
        </ul>
        <p className="mt-3">
          Le motif d&apos;une décision reste entre la modération et l&apos;auteur du contenu : tu vois l&apos;issue,
          pas le détail.
        </p>
      </details>
    </div>
  );
}
