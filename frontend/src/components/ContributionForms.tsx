"use client";

import { useRouter } from "next/navigation";
import { useDeferredValue, useRef, useState } from "react";

import type { AiUsage, DecisionType } from "@/lib/api";
import { apiPost, apiUpload } from "@/lib/client-api";
import { prepareImage } from "@/lib/image";
import { AI_USAGE_OPTIONS, SOLUTION_STATUS_LABELS } from "@/lib/labels";

import { LATEX_HELP } from "./ExerciseForm";
import { Field, FormMessage, SubmitButton, inputClass, primaryButtonClass, secondaryButtonClass } from "./Form";
import { MathEditor } from "./MathEditor";
import { MathMarkdown } from "./MathMarkdown";

// L'éditeur n'est pas un champ natif : la longueur minimale se vérifie avant l'envoi.
const SOLUTION_MIN_LENGTH = 20;
const TOO_SHORT = `Une solution fait au moins ${SOLUTION_MIN_LENGTH} caractères.`;

/** Photo d'une copie manuscrite, transcrite en LaTeX par Claude ; la photo n'est pas gardée. */
function PhotoTranscription({ exerciseId, onText }: { exerciseId: number; onText: (text: string) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);

  async function onFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = ""; // pour pouvoir reprendre la même photo
    if (!file) return;
    setPending(true);
    setResult({});
    const image = await prepareImage(file);
    if (!image) {
      setPending(false);
      return setResult({ error: "Format non reconnu : prends la photo en JPEG ou en PNG." });
    }
    const form = new FormData();
    form.append("photo", image, "copie.jpg");
    const transcribed = await apiUpload<{ text: string }>(`/exercises/${exerciseId}/transcription`, form);
    setPending(false);
    if (!transcribed.ok) return setResult({ error: transcribed.error });
    onText(transcribed.data.text);
    setResult({ success: "Transcription ajoutée à ta solution : relis-la et corrige-la avant d'envoyer." });
  }

  return (
    <div className="space-y-2">
      <input ref={input} type="file" accept="image/*" hidden onChange={onFile} />
      <button
        type="button"
        onClick={() => input.current?.click()}
        disabled={pending}
        className={secondaryButtonClass}
      >
        {pending ? "Transcription en cours… jusqu'à une minute" : "[▣] Photographier ma copie"}
      </button>
      <p className="text-sm text-mute">
        Écrite à la main ? Une page par photo, nette et bien éclairée. Claude la transcrit telle quelle, sans
        rien corriger, et la photo n&apos;est pas conservée. Ça compte comme une mise en forme par IA : points
        pleins.
      </p>
      <FormMessage error={result.error} success={result.success} />
    </div>
  );
}

export function SolutionForm({ exerciseId, transcription = false }: { exerciseId: number; transcription?: boolean }) {
  const router = useRouter();
  const [body, setBody] = useState("");
  const preview = useDeferredValue(body);
  const [aiUsage, setAiUsage] = useState<AiUsage>("aucune");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  function addTranscription(text: string) {
    setBody((current) => (current.trim() ? `${current.trimEnd()}\n\n${text}` : text));
    // La transcription est une mise en forme par IA : on le déclare, sans perdre de points.
    if (aiUsage === "aucune") setAiUsage("relecture");
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (body.trim().length < SOLUTION_MIN_LENGTH) return setError(TOO_SHORT);
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
      {transcription && <PhotoTranscription exerciseId={exerciseId} onText={addTranscription} />}
      <Field label="Rédaction" htmlFor="solution-body" hint={LATEX_HELP}>
        <MathEditor id="solution-body" label="Ta solution" value={body} onChange={setBody} />
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

/** Réponse à la question neutre d'une solution en vérification. */
export function IntegrityAnswer({ signalId, initial }: { signalId: number; initial: string | null }) {
  const [answer, setAnswer] = useState(initial ?? "");
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const saved = await apiPost(`/integrity/${signalId}/answer`, { answer });
    setPending(false);
    setResult(saved.ok ? { success: "Réponse transmise au modérateur." } : { error: saved.error });
  }

  return (
    <form onSubmit={onSubmit} className="mt-3 space-y-3">
      <Field label="Ta réponse" htmlFor={`integrity-${signalId}`}>
        <textarea
          id={`integrity-${signalId}`}
          required
          minLength={3}
          maxLength={2000}
          rows={3}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          className={inputClass}
        />
      </Field>
      <FormMessage error={result.error} success={result.success} />
      <SubmitButton pending={pending}>Répondre</SubmitButton>
    </form>
  );
}

/** Faire appel d'une décision : un autre modérateur l'examine sous 7 jours. */
export function AppealForm({ type, id }: { type: DecisionType; id: number }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [statement, setStatement] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)} className="mt-2 text-sm underline underline-offset-4">
        [!] Faire appel
      </button>
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const result = await apiPost("/appeals", { type, id, statement });
    setPending(false);
    if (!result.ok) return setError(result.error);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="mt-3 space-y-3">
      <Field label="Pourquoi la décision te semble injuste" htmlFor={`appeal-${type}-${id}`}>
        <textarea
          id={`appeal-${type}-${id}`}
          required
          minLength={10}
          maxLength={3000}
          rows={4}
          value={statement}
          onChange={(event) => setStatement(event.target.value)}
          className={inputClass}
        />
      </Field>
      <FormMessage error={error} />
      <div className="flex gap-3">
        <SubmitButton pending={pending}>Envoyer l&apos;appel</SubmitButton>
        <button type="button" onClick={() => setOpen(false)} className={secondaryButtonClass}>
          Annuler
        </button>
      </div>
    </form>
  );
}

/** Reprendre sa solution : à compléter, ou validée (plus de 20 % de changement la renvoie en relecture). */
export function ReviseSolution({ solutionId, body, validated }: { solutionId: number; body: string; validated: boolean }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [text, setText] = useState(body);
  const preview = useDeferredValue(text);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)} className="mt-2 text-sm underline underline-offset-4">
        [~] {validated ? "Modifier ma solution" : "Compléter ma solution"}
      </button>
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (text.trim().length < SOLUTION_MIN_LENGTH) return setError(TOO_SHORT);
    setPending(true);
    const saved = await apiPost(`/solutions/${solutionId}/revise`, { body: text });
    setPending(false);
    if (!saved.ok) return setError(saved.error);
    setOpen(false);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="mt-3 space-y-3">
      <Field
        label="Solution révisée"
        htmlFor={`revise-${solutionId}`}
        hint={validated ? "Une modification de plus de 20 % renvoie la solution en relecture." : "Elle repartira en relecture, auprès de trois nouveaux relecteurs."}
      >
        <MathEditor id={`revise-${solutionId}`} label="Solution révisée" value={text} onChange={setText} />
      </Field>
      {preview.trim() && (
        <div className="border-l-2 border-hairline-strong bg-surface-soft px-4">
          <MathMarkdown>{preview}</MathMarkdown>
        </div>
      )}
      <FormMessage error={error} />
      <div className="flex items-center gap-4">
        <SubmitButton pending={pending}>Envoyer</SubmitButton>
        <button type="button" onClick={() => setOpen(false)} className="text-sm text-mute hover:text-ink">
          Annuler
        </button>
      </div>
    </form>
  );
}

/** L'auteur de l'exercice recommande une solution validée : +5 pour son auteur, une fois. */
export function RecommendButton({ solutionId }: { solutionId: number }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  return (
    <span className="inline-flex items-center gap-2">
      <button
        type="button"
        onClick={async () => {
          if (!window.confirm("Recommander cette solution ? Tu ne pourras en recommander qu'une.")) return;
          const result = await apiPost(`/solutions/${solutionId}/recommend`);
          if (result.ok) router.refresh();
          else setError(result.error);
        }}
        className="text-sm underline underline-offset-4"
      >
        [★] Recommander
      </button>
      {error && <span role="alert" className="text-sm text-danger-text">{error}</span>}
    </span>
  );
}

/** Relecture spontanée d'une solution en attente (poids ½). */
export function VolunteerButton({ solutionId }: { solutionId: number }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  return (
    <span className="inline-flex items-center gap-2">
      <button
        type="button"
        onClick={async () => {
          const result = await apiPost(`/solutions/${solutionId}/volunteer`);
          if (result.ok) router.refresh();
          else setError(result.error);
        }}
        className={secondaryButtonClass}
      >
        Je relis
      </button>
      {error && <span role="alert" className="text-sm text-danger-text">{error}</span>}
    </span>
  );
}

/** Décision d'un expert sur une solution contestée. */
export function ArbitrationButtons({ solutionId }: { solutionId: number }) {
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function decide(validate: boolean) {
    const result = await apiPost<{ solution_status: keyof typeof SOLUTION_STATUS_LABELS }>(
      `/arbitrations/${solutionId}`,
      { validate_solution: validate },
    );
    if (result.ok) setStatus(SOLUTION_STATUS_LABELS[result.data.solution_status]);
    else setError(result.error);
  }

  if (status) return <FormMessage success={`Décision enregistrée : ${status.toLowerCase()}.`} />;
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3">
        <button type="button" onClick={() => decide(true)} className={primaryButtonClass}>
          Valider
        </button>
        <button type="button" onClick={() => decide(false)} className={secondaryButtonClass}>
          À compléter
        </button>
      </div>
      <FormMessage error={error} />
    </div>
  );
}
