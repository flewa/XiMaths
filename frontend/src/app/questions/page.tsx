import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { AnswerQuestion, OpenQuestion } from "@/components/Questions";
import { Tag } from "@/components/Tag";
import { type ComprehensionQuestion, fetchMyQuestions } from "@/lib/api";

export const metadata: Metadata = { title: "Questions de compréhension" };

const dateTime = new Intl.DateTimeFormat("fr-FR", { dateStyle: "long", timeStyle: "short" });

const OUTCOMES: Partial<Record<ComprehensionQuestion["status"], string>> = {
  repondue: "[~] Réponse envoyée : un relecteur expérimenté l'évalue.",
  reussie: "[+] Réponse validée : les points de ta solution sont accordés.",
  insuffisante: "[-] Réponse jugée insuffisante : ta solution reste publiée, sans ses points de classement. Ce n'est pas une sanction.",
  sans_reponse: "[-] Pas de réponse dans le délai : ta solution reste publiée, sans ses points de classement. Ce n'est pas une sanction.",
};

function QuestionCard({ question }: { question: ComprehensionQuestion }) {
  return (
    <li className="py-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Link href={`/exercices/${question.exercise_id}`} className="font-medium hover:underline">
          {question.exercise_title}
        </Link>
        <Tag strong={question.status === "envoyee" || question.status === "ouverte"}>{question.status_label}</Tag>
      </div>
      {question.status === "envoyee" && (
        <div className="mt-3 space-y-3">
          {question.open_until && (
            <p className="text-sm text-mute">À ouvrir avant le {dateTime.format(new Date(question.open_until))}.</p>
          )}
          <OpenQuestion questionId={question.id} />
        </div>
      )}
      {question.status === "ouverte" && <AnswerQuestion question={question} />}
      {OUTCOMES[question.status] && <p className="mt-3 text-body">{OUTCOMES[question.status]}</p>}
      {question.question && question.status !== "ouverte" && (
        <p className="mt-2 text-sm text-mute">Question : {question.question}</p>
      )}
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

  return (
    <div className="max-w-[720px]">
      <h1>Questions de compréhension</h1>
      <p className="mt-2 text-body">
        Parfois, sur une solution classée ou qui rapporte beaucoup, on te pose une question courte
        sur ta propre solution. Ce n&apos;est jamais une accusation : on vérifie la compréhension, et
        la réussite accorde les points, avec 30 jours sans nouvelle question.
      </p>
      <ul className="mt-6 space-y-2 text-body">
        <li className="flex gap-2">
          <span className="shrink-0 text-mute">[+]</span>
          <span>72 heures pour ouvrir la question, puis 5 minutes pour répondre, sans document.</span>
        </li>
        <li className="flex gap-2">
          <span className="shrink-0 text-mute">[+]</span>
          <span>Un relecteur expérimenté évalue ta réponse ; une décision humaine, toujours.</span>
        </li>
        <li className="flex gap-2">
          <span className="shrink-0 text-mute">[+]</span>
          <span>Sans réponse ou insuffisante : ta solution reste publiée, sans ses points de classement. Aucune sanction.</span>
        </li>
      </ul>
      {questions.length === 0 ? (
        <p className="mt-10 text-mute">Aucune question pour toi.</p>
      ) : (
        <ul className="mt-10 divide-y divide-hairline border-y border-hairline">
          {questions.map((question) => (
            <QuestionCard key={question.id} question={question} />
          ))}
        </ul>
      )}
    </div>
  );
}
