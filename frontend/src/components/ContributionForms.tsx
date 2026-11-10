"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { AiUsage, DecisionType } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { AI_USAGE_OPTIONS, SOLUTION_STATUS_LABELS } from "@/lib/labels";

import { CopyPhotoPicker, type PickedPhotos } from "./CopyPhotoPicker";
import { Checkbox, Field, FormMessage, SubmitButton, inputClass, secondaryButtonClass } from "./Form";
import { MODEL_CONSENT_LABEL } from "./ModelCopy";

// Une solution est la copie manuscrite, en photos : rien ne se tape.
const NO_PHOTOS: PickedPhotos = { token: null, count: 0 };
const PHOTOS_NEEDED = "Joins les photos de ta copie : scanne le QR code avec ton téléphone.";

/** Usage de l'IA, déclaré par l'auteur : il module les points, jamais la relecture. */
export function AiUsageChoice({
  name,
  value,
  onChange,
}: {
  name: string;
  value: AiUsage;
  onChange: (value: AiUsage) => void;
}) {
  return (
    <fieldset className="space-y-2">
      <legend className="font-medium">As-tu utilisé une IA ?</legend>
      {AI_USAGE_OPTIONS.map((option) => (
        <label key={option.value} className="flex gap-2">
          <input
            type="radio"
            name={name}
            value={option.value}
            checked={value === option.value}
            onChange={() => onChange(option.value)}
            className="shrink-0"
          />
          <span>
            {option.label} <span className="text-mute">· {option.help}</span>
          </span>
        </label>
      ))}
    </fieldset>
  );
}

export function SolutionForm({ exerciseId }: { exerciseId: number }) {
  const router = useRouter();
  const [aiUsage, setAiUsage] = useState<AiUsage>("aucune");
  const [picked, setPicked] = useState<PickedPhotos>(NO_PHOTOS);
  const [modelConsent, setModelConsent] = useState(false);
  // Changée après l'envoi : un nouvel envoi de photos pour la prochaine solution.
  const [round, setRound] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (picked.count === 0 || !picked.token) return setError(PHOTOS_NEEDED);
    setPending(true);
    setError(null);
    const result = await apiPost(`/exercises/${exerciseId}/solutions`, {
      ai_usage: aiUsage,
      photo_upload: picked.token,
      model_consent: modelConsent,
    });
    setPending(false);
    if (!result.ok) return setError(result.error);
    setPicked(NO_PHOTOS);
    setRound((value) => value + 1);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="mt-3 space-y-6">
      <fieldset className="space-y-2">
        <legend className="font-medium">Ta copie, écrite à la main</legend>
        <CopyPhotoPicker key={round} source={{ exerciseId }} onChange={setPicked} />
      </fieldset>
      <AiUsageChoice name="ai_usage" value={aiUsage} onChange={setAiUsage} />
      <div className="text-sm text-body">
        <Checkbox checked={modelConsent} onChange={setModelConsent}>
          {MODEL_CONSENT_LABEL} <span className="text-mute">Facultatif, et modifiable ensuite.</span>
        </Checkbox>
      </div>
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
        label="Ton commentaire pour l'auteur"
        htmlFor={`feedback-${reviewId}`}
        hint="Ce qui est juste, ce qui manque, ce qui est faux. L'auteur le lit dès que tu l'envoies : aucune solution n'étant publique, c'est la seule correction qu'il recevra. Reste factuel et bienveillant."
      >
        <textarea
          id={`feedback-${reviewId}`}
          required
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
      <span title={disabledReason} className="rounded-sm bg-surface-card px-3 text-sm leading-7 text-mute">
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
        Faire appel
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
export function ReviseSolution({
  solutionId,
  exerciseId,
  validated,
}: {
  solutionId: number;
  exerciseId: number;
  validated: boolean;
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [picked, setPicked] = useState<PickedPhotos>(NO_PHOTOS);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)} className="mt-2 text-sm underline underline-offset-4">
        {validated ? "Remplacer ma copie" : "Compléter ma copie"}
      </button>
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (picked.count === 0 || !picked.token) return setError(PHOTOS_NEEDED);
    setPending(true);
    const saved = await apiPost(`/solutions/${solutionId}/revise`, { photo_upload: picked.token });
    setPending(false);
    if (!saved.ok) return setError(saved.error);
    setOpen(false);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="mt-3 space-y-4">
      <fieldset className="space-y-2">
        <legend className="font-medium">Nouvelles photos de ta copie, complète</legend>
        <p className="text-sm text-mute">
          Elles remplacent les précédentes, et ta solution repart en relecture
          {validated ? "" : ", auprès de trois nouveaux relecteurs"}.
        </p>
        <CopyPhotoPicker source={{ exerciseId }} onChange={setPicked} />
      </fieldset>
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

/** Choisir de relire une copie en attente : elle rejoint « mes relectures ». */
export function VolunteerButton({ solutionId, label = "Je relis" }: { solutionId: number; label?: string }) {
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
        {label}
      </button>
      {error && <span role="alert" className="text-sm text-danger-text">{error}</span>}
    </span>
  );
}
