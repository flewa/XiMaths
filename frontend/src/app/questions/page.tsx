import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Icon } from "@/components/Icon";
import { MathText } from "@/components/MathText";
import { AnswerQuestion, OpenQuestion } from "@/components/Questions";
import { PageIntro } from "@/components/PageIntro";
import { type ComprehensionQuestion, fetchMyQuestions } from "@/lib/api";

export const metadata: Metadata = { title: "Questions de compréhension" };

const dateTime = new Intl.DateTimeFormat("fr-FR", { dateStyle: "long", timeStyle: "short" });

const WAITING: ComprehensionQuestion["status"][] = ["envoyee", "ouverte"];

const OUTCOMES: Partial<Record<ComprehensionQuestion["status"], { text: string; className: string }>> = {
  repondue: { text: "Réponse envoyée : un relecteur expérimenté l'évalue.", className: "bg-surface-card text-body" },
  reussie: { text: "Réponse validée : les points de ta solution sont accordés.", className: "text-success" },
  insuffisante: {
    text: "Réponse jugée insuffisante : ta solution reste publiée, sans ses points de classement. Ce n'est pas une sanction.",
    className: "text-mute",
  },
  sans_reponse: {
    text: "Pas de réponse dans le délai : ta solution reste publiée, sans ses points de classement. Ce n'est pas une sanction.",
    className: "text-mute",
  },
};

const RULES = [
  "72 heures pour ouvrir la question, puis 5 minutes pour répondre, sans document.",
  "Un relecteur expérimenté évalue ta réponse : une décision humaine, toujours.",
  "Réussie : les points de ta solution sont accordés, et 30 jours sans nouvelle question.",
  "Sans réponse ou insuffisante : ta solution reste publiée, sans ses points de classement. Aucune sanction.",
];

function ExerciseLink({ question }: { question: ComprehensionQuestion }) {
  return (
    <Link href={`/exercices/${question.exercise_id}`} className="font-medium text-ink hover:underline">
      <MathText>{question.exercise_title}</MathText>
    </Link>
  );
}

/** Une question qui attend le membre : à ouvrir, ou ouverte (le chrono tourne). */
function WaitingQuestion({ question }: { question: ComprehensionQuestion }) {
  return (
    <li className="rounded-2xl border border-accent bg-surface-soft p-5">
      <p className="text-sm text-accent-text">
        {question.status === "ouverte" ? "Question ouverte : réponds avant la fin du chrono" : "Une question sur ta solution"}
      </p>
      <p className="mt-1">
        <ExerciseLink question={question} />
      </p>
      {question.status === "envoyee" ? (
        <div className="mt-4 space-y-3">
          {question.open_until && (
            <p className="text-sm text-body">
              À ouvrir avant le <span className="text-ink">{dateTime.format(new Date(question.open_until))}</span>.
              Une fois ouverte, tu as 5 minutes, sans document : choisis un moment au calme.
            </p>
          )}
          <OpenQuestion questionId={question.id} />
        </div>
      ) : (
        <AnswerQuestion question={question} />
      )}
    </li>
  );
}

function PastQuestion({ question }: { question: ComprehensionQuestion }) {
  const outcome = OUTCOMES[question.status];
  return (
    <li className="py-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <ExerciseLink question={question} />
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-sm font-medium ${outcome?.className ?? ""}`}
        >
          {question.status === "reussie" && <Icon name="check" size={14} />}
          {question.status_label}
        </span>
      </div>
      {outcome && <p className="mt-2 text-sm text-body">{outcome.text}</p>}
      {question.question && <p className="mt-2 text-sm text-mute">Question : {question.question}</p>}
      {question.evaluation_note && <p className="mt-1 text-sm text-mute">Motif : {question.evaluation_note}</p>}
    </li>
  );
}

export default async function QuestionsPage() {
  let questions;
  try {
    questions = await fetchMyQuestions();
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!questions) redirect("/connexion?suivant=/questions");

  // Le serveur range déjà les questions en attente en tête.
  const waiting = questions.filter((question) => WAITING.includes(question.status));
  const past = questions.filter((question) => !WAITING.includes(question.status));

  return (
    <div className="max-w-[720px]">
      <h1>Questions de compréhension</h1>
      <PageIntro id="questions">
        Parfois, sur une solution classée ou qui rapporte beaucoup, on te pose une question courte sur ta propre
        solution. Ce n&apos;est jamais une accusation : on vérifie que tu l&apos;as comprise, et la réussite
        accorde ses points.
      </PageIntro>

      {waiting.length > 0 && (
        <section aria-labelledby="en-attente" className="mt-8">
          <h2 id="en-attente" className="sr-only">
            En attente
          </h2>
          <ul className="space-y-3">
            {waiting.map((question) => (
              <WaitingQuestion key={question.id} question={question} />
            ))}
          </ul>
        </section>
      )}

      {questions.length === 0 ? (
        <p className="mt-8 rounded-2xl bg-surface-soft px-5 py-4 text-body">
          Aucune question pour toi. Si l&apos;une t&apos;est posée, une notification te préviendra, et un email
          sauf si tu les as coupés dans tes réglages.
        </p>
      ) : (
        past.length > 0 && (
          <section aria-labelledby="historique" className="mt-10">
            <h2 id="historique">Historique</h2>
            <ul className="mt-2 divide-y divide-hairline border-b border-hairline">
              {past.map((question) => (
                <PastQuestion key={question.id} question={question} />
              ))}
            </ul>
          </section>
        )
      )}

      <section aria-labelledby="regles" className="mt-10">
        <h2 id="regles" className="font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-ink">
          Comment ça marche
        </h2>
        <ul className="mt-3 space-y-2 text-sm text-body">
          {RULES.map((rule) => (
            <li key={rule} className="flex gap-2">
              <span aria-hidden="true" className="mt-[0.55em] size-1.5 shrink-0 rounded-full bg-stone" />
              <span>{rule}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
