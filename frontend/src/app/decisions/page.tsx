import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AppealForm } from "@/components/ContributionForms";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Tag } from "@/components/Tag";
import { fetchMyDecisions } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Mes décisions" };

function day(value: string) {
  return dateFormat.format(new Date(value));
}

export default async function MyDecisionsPage() {
  let decisions;
  try {
    decisions = await fetchMyDecisions();
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!decisions) redirect("/connexion?suivant=/decisions");

  return (
    <>
      <h1>Mes décisions</h1>
      <p className="mt-2 text-body">
        Les décisions de modération qui te concernent, toujours prises par un humain et motivées. Tu
        peux faire appel sous 14 jours : un autre modérateur examine ta demande et répond sous 7 jours.
      </p>

      {decisions.length === 0 ? (
        <p className="mt-8 text-mute">Aucune décision de modération ne te concerne.</p>
      ) : (
        <ul className="mt-10 divide-y divide-hairline border-y border-hairline">
          {decisions.map((decision) => (
            <li key={`${decision.type}-${decision.id}`} className="py-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-medium">{decision.title}</span>
                {decision.appeal_status_label && (
                  <Tag strong={decision.appeal_status === "annulee"}>Appel : {decision.appeal_status_label}</Tag>
                )}
              </div>
              <p className="mt-1 text-sm text-mute">
                {decision.decided_at && <>Le {day(decision.decided_at)}</>}
                {decision.ends_at && <> · jusqu&apos;au {day(decision.ends_at)}</>}
              </p>
              {decision.reason && <p className="mt-2 whitespace-pre-line text-body">Motif : {decision.reason}</p>}
              {decision.appeal_note && (
                <p className="mt-2 whitespace-pre-line text-body">Réponse à ton appel : {decision.appeal_note}</p>
              )}
              {decision.can_appeal && (
                <>
                  {decision.appeal_deadline && (
                    <p className="mt-2 text-sm text-mute">Appel possible jusqu&apos;au {day(decision.appeal_deadline)}.</p>
                  )}
                  <AppealForm type={decision.type} id={decision.id} />
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
