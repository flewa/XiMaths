import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AppealForm } from "@/components/ContributionForms";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathText } from "@/components/MathText";
import { type Decision, fetchMyDecisions } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Mes décisions" };

function day(value: string) {
  return dateFormat.format(new Date(value));
}

const pill = "inline-flex items-center rounded-full px-2.5 py-0.5 text-sm font-medium";

/** Où en est la décision : la sanction court-elle encore, et l'appel ? */
function DecisionState({ decision }: { decision: Decision }) {
  const chips: { text: string; className: string }[] = [];
  if (decision.state === "en_cours") {
    chips.push({
      text: decision.ends_at ? `En cours jusqu'au ${day(decision.ends_at)}` : "En cours",
      className: "bg-accent-soft text-accent-text",
    });
  } else if (decision.state === "levee") {
    chips.push({ text: "Levée", className: "text-success" });
  } else if (decision.state === "terminee") {
    chips.push({ text: "Terminée", className: "text-mute" });
  }
  if (decision.appeal_status) {
    chips.push({
      text: `Appel : ${decision.appeal_status_label}`,
      className:
        decision.appeal_status === "annulee"
          ? "text-success"
          : decision.appeal_status === "en_attente"
            ? "bg-surface-card text-body"
            : "text-mute",
    });
  }
  if (chips.length === 0) return null;
  return (
    <span className="flex flex-wrap gap-2">
      {chips.map((chip) => (
        <span key={chip.text} className={`${pill} ${chip.className}`}>
          {chip.text}
        </span>
      ))}
    </span>
  );
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
    <div className="max-w-[720px]">
      <h1>Mes décisions</h1>
      <p className="mt-2 text-body">
        Les décisions de modération qui te concernent, toujours prises par un humain et motivées. Tu peux faire
        appel sous 14 jours : un autre modérateur examine ta demande et répond sous 7 jours.
      </p>

      {decisions.length === 0 ? (
        <p className="mt-8 rounded-2xl bg-surface-soft px-5 py-4 text-body">
          Aucune décision de modération ne te concerne. Si un jour un de tes contenus est retiré, ou une sanction
          prise, tu verras ici son motif, et tu pourras faire appel.
        </p>
      ) : (
        <ul className="mt-8 space-y-3">
          {decisions.map((decision) => (
            <li key={`${decision.type}-${decision.id}`} className="rounded-2xl border border-hairline p-5">
              <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
                <span className="min-w-0 flex-1 basis-64 font-medium text-ink">
                  <MathText>{decision.title}</MathText>
                </span>
                <DecisionState decision={decision} />
              </div>
              {decision.decided_at && <p className="mt-1 text-sm text-mute">Décidé le {day(decision.decided_at)}</p>}
              {decision.reason && (
                <p className="mt-3 whitespace-pre-line text-body">
                  <span className="text-mute">Motif : </span>
                  {decision.reason}
                </p>
              )}
              {decision.appeal_note && (
                <p className="mt-3 whitespace-pre-line rounded-xl bg-surface-soft px-4 py-3 text-body">
                  <span className="text-mute">Réponse à ton appel : </span>
                  {decision.appeal_note}
                </p>
              )}
              {decision.can_appeal && (
                <div className="mt-4 border-t border-hairline pt-3">
                  {decision.appeal_deadline && (
                    <p className="text-sm text-mute">
                      Tu peux faire appel jusqu&apos;au <span className="text-ink">{day(decision.appeal_deadline)}</span>.
                      Explique pourquoi la décision te semble injuste : un autre modérateur la réexamine.
                    </p>
                  )}
                  <AppealForm type={decision.type} id={decision.id} />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
