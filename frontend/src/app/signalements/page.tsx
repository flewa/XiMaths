import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Tag } from "@/components/Tag";
import { fetchMyReports } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Mes signalements" };

export default async function MyReportsPage() {
  let reports;
  try {
    reports = await fetchMyReports();
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!reports) redirect("/connexion?suivant=/signalements");

  return (
    <>
      <h1>Mes signalements</h1>
      <p className="mt-2 text-body">
        Un modérateur examine chaque signalement. Un doublon, un plagiat ou une erreur confirmés
        rapportent 3 points. Tes signalements restent confidentiels.
      </p>

      {reports.length === 0 ? (
        <p className="mt-8 text-mute">
          Aucun signalement. Le bouton « Signaler » se trouve sous chaque exercice et chaque solution.
        </p>
      ) : (
        <ul className="mt-10 divide-y divide-hairline border-y border-hairline">
          {reports.map((report) => (
            <li key={report.id} className="flex flex-wrap items-center justify-between gap-2 py-3">
              <span>
                <Link href={`/exercices/${report.exercise_id}`} className="font-medium hover:underline">
                  {report.title}
                </Link>
                <span className="block text-sm text-mute">
                  {report.reason_label} · le {dateFormat.format(new Date(report.created_at))}
                </span>
              </span>
              <Tag strong={report.status === "confirme"}>{report.status_label}</Tag>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
