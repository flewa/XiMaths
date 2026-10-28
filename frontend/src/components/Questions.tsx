"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import type { ComprehensionQuestion } from "@/lib/api";
import { apiPost } from "@/lib/client-api";

import { Field, FormMessage, SubmitButton, inputClass, primaryButtonClass, secondaryButtonClass } from "./Form";
import { MathMarkdown } from "./MathMarkdown";
import { clock } from "./Training";

/** Ouvrir la question : les 5 minutes partent de là, comptées par le serveur. */
export function OpenQuestion({ questionId }: { questionId: number }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  return (
    <div className="space-y-3">
      <button
        type="button"
        disabled={pending}
        onClick={async () => {
          setPending(true);
          const opened = await apiPost(`/questions/${questionId}/open`);
          setPending(false);
          if (!opened.ok) return setError(opened.error);
          router.refresh();
        }}
        className={primaryButtonClass}
      >
        {pending ? "Un instant…" : "Ouvrir la question · 5 minutes"}
      </button>
      <FormMessage error={error} />
    </div>
  );
}

function secondsLeft(deadline: string) {
  return Math.max(0, (Date.parse(deadline) - Date.now()) / 1000);
}

/** Répondre, en 5 minutes. Le chrono s'affiche ; à zéro, le serveur refuse la réponse. */
export function AnswerQuestion({ question }: { question: ComprehensionQuestion }) {
  const router = useRouter();
  const [answer, setAnswer] = useState("");
  const [remaining, setRemaining] = useState(() => secondsLeft(question.answer_until!));
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setRemaining(secondsLeft(question.answer_until!)), 1000);
    return () => clearInterval(timer);
  }, [question.answer_until]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const sent = await apiPost(`/questions/${question.id}/answer`, { answer });
    setPending(false);
    if (!sent.ok) return setError(sent.error);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="mt-4 space-y-4">
      <p className="font-medium">
        <span className="text-mute">temps restant </span>
        {/* Calculé au rendu serveur puis dans le navigateur : une seconde d'écart est normale. */}
        <span suppressHydrationWarning className={`tabular-nums ${remaining <= 60 ? "text-warning" : ""}`}>
          {clock(remaining)}
        </span>
      </p>
      <p className="border-l-2 border-ink pl-3 font-medium">{question.question}</p>
      <Field label="Ta réponse" htmlFor={`question-${question.id}`} hint="Quelques phrases suffisent : on cherche ton raisonnement, pas une rédaction parfaite.">
        <textarea
          id={`question-${question.id}`}
          required
          maxLength={3000}
          rows={6}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          className={inputClass}
        />
      </Field>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Envoyer ma réponse</SubmitButton>
      <details className="plain border-t border-hairline pt-3">
        <summary className="cursor-pointer text-sm text-mute">Revoir l&apos;énoncé et ma solution</summary>
        {question.statement && <MathMarkdown>{question.statement}</MathMarkdown>}
        {question.solution_body && (
          <div className="border-l-2 border-hairline-strong bg-surface-soft px-4">
            <MathMarkdown>{question.solution_body}</MathMarkdown>
          </div>
        )}
      </details>
    </form>
  );
}

/** Évaluation par un expert ou un modérateur : la décision reste humaine. */
export function EvaluateQuestion({ questionId }: { questionId: number }) {
  const [note, setNote] = useState("");
  const [done, setDone] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function decide(passed: boolean) {
    const result = await apiPost(`/questions/${questionId}/evaluate`, { passed, note });
    if (result.ok) setDone(passed ? "Réponse validée : les points sont accordés." : "Réponse jugée insuffisante.");
    else setError(result.error);
  }

  if (done) return <FormMessage success={done} />;
  return (
    <div className="space-y-3">
      <Field label="Motif (facultatif)" htmlFor={`evaluation-${questionId}`}>
        <input
          id={`evaluation-${questionId}`}
          maxLength={1000}
          value={note}
          onChange={(event) => setNote(event.target.value)}
          className={inputClass}
        />
      </Field>
      <div className="flex flex-wrap gap-3">
        <button type="button" onClick={() => decide(true)} className={primaryButtonClass}>
          Réponse convaincante
        </button>
        <button type="button" onClick={() => decide(false)} className={secondaryButtonClass}>
          Insuffisante
        </button>
      </div>
      <FormMessage error={error} />
    </div>
  );
}
