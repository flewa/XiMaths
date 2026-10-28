"use client";

import { useRouter } from "next/navigation";
import { useDeferredValue, useState } from "react";

import type { AiUsage } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { AI_USAGE_OPTIONS, SOLUTION_STATUS_LABELS } from "@/lib/labels";

import { LATEX_HELP } from "./ExerciseForm";
import { Field, FormMessage, SubmitButton, inputClass } from "./Form";
import { MathMarkdown } from "./MathMarkdown";

export function SolutionForm({ exerciseId }: { exerciseId: number }) {
  const router = useRouter();
  const [body, setBody] = useState("");
  const preview = useDeferredValue(body);
  const [aiUsage, setAiUsage] = useState<AiUsage>("aucune");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const result = await apiPost(`/exercises/${exerciseId}/solutions`, { body, ai_usage: aiUsage });
    setPending(false);
    if (!result.ok) return setError(result.error);
    setBody("");
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="mt-3 space-y-4">
      <Field label="Ta solution" htmlFor="solution-body" hint={LATEX_HELP}>
        <textarea
          id="solution-body"
          required
          minLength={20}
          rows={8}
          value={body}
          onChange={(event) => setBody(event.target.value)}
          className={`${inputClass} font-mono`}
        />
      </Field>
      {preview.trim() && (
        <div aria-label="Aperçu de la solution" className="border-l-2 border-hairline-strong bg-surface-soft px-4">
          <MathMarkdown>{preview}</MathMarkdown>
        </div>
      )}
      <fieldset className="space-y-2">
        <legend className="font-medium">As-tu utilisé une IA ?</legend>
        {AI_USAGE_OPTIONS.map((option) => (
          <label key={option.value} className="flex gap-2">
            <input
              type="radio"
              name="ai_usage"
              value={option.value}
              checked={aiUsage === option.value}
              onChange={() => setAiUsage(option.value)}
              className="shrink-0"
            />
            <span>
              {option.label} <span className="text-mute">· {option.help}</span>
            </span>
          </label>
        ))}
      </fieldset>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Envoyer en relecture</SubmitButton>
    </form>
  );
}

const VERDICTS = [
  { value: "correcte", label: "Correcte", help: "La preuve est complète et juste." },
  {
    value: "lacunes",
    label: "Correcte avec lacunes",
    help: "L'idée est juste, mais une étape manque de justification.",
  },
  { value: "incorrecte", label: "Incorrecte", help: "Une erreur invalide le raisonnement." },
];

export function ReviewForm({ reviewId }: { reviewId: number }) {
  const [verdict, setVerdict] = useState("correcte");
  const [feedback, setFeedback] = useState("");
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);
  const needsFeedback = verdict !== "correcte";

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const response = await apiPost<{ solution_status: keyof typeof SOLUTION_STATUS_LABELS }>(
      `/reviews/${reviewId}`,
      { verdict, feedback },
    );
    setPending(false);
    if (!response.ok) return setResult({ error: response.error });
    // Pas de router.refresh() : la relecture quitterait la liste avec ce message.
    setResult({
      success: `Merci ! Statut de la solution : ${SOLUTION_STATUS_LABELS[response.data.solution_status].toLowerCase()}.`,
    });
  }

  if (result.success) return <FormMessage success={result.success} />;
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <fieldset className="space-y-2">
        <legend className="font-medium">Ton verdict</legend>
        {VERDICTS.map((option) => (
          <label key={option.value} className="flex gap-2">
            <input
              type="radio"
              name={`verdict-${reviewId}`}
              value={option.value}
              checked={verdict === option.value}
              onChange={() => setVerdict(option.value)}
              className="shrink-0"
            />
            <span>
              {option.label} <span className="text-mute">· {option.help}</span>
            </span>
          </label>
        ))}
      </fieldset>
      <Field
        label={needsFeedback ? "Ce qui manque ou ce qui est faux" : "Commentaire (facultatif)"}
        htmlFor={`feedback-${reviewId}`}
        hint="Visible par l'auteur une fois la relecture close. Reste factuel et bienveillant."
      >
        <textarea
          id={`feedback-${reviewId}`}
          required={needsFeedback}
          rows={3}
          maxLength={5000}
          value={feedback}
          onChange={(event) => setFeedback(event.target.value)}
          className={inputClass}
        />
      </Field>
      <FormMessage error={result.error} />
      <SubmitButton pending={pending}>Envoyer ma relecture</SubmitButton>
    </form>
  );
}

export function VoteButton({
  path,
  count,
  disabledReason,
}: {
  path: string;
  count: number;
  disabledReason: string | null;
}) {
  const [votes, setVotes] = useState(count);
  const [voted, setVoted] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const label = `Utile · ${votes}`;

  if (disabledReason) {
    return (
      <span title={disabledReason} className="rounded-sm bg-surface-card px-3 text-sm leading-7 text-ash">
        ▲ {label}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-2">
      <button
        type="button"
        aria-pressed={voted}
        disabled={voted}
        onClick={async () => {
          const result = await apiPost(path);
          if (result.ok) {
            setVotes(votes + 1);
            setVoted(true);
          } else if (result.status === 409) {
            setVoted(true);
          } else {
            setMessage(result.error);
          }
        }}
        className="rounded-sm border border-hairline-strong px-3 text-sm font-medium leading-7 active:bg-surface-card aria-pressed:bg-surface-card"
      >
        ▲ {label}
      </button>
      {message && <span role="alert" className="text-sm text-mute">{message}</span>}
    </span>
  );
}
