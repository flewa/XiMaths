"use client";

import { useRouter } from "next/navigation";
import { useDeferredValue, useEffect, useState } from "react";

import type { Level, SimilarExercise, Topic } from "@/lib/api";
import { apiPost, apiPut } from "@/lib/client-api";

import { DuplicateScreen, SimilarPanel, type PublishChoice } from "./Duplicates";
import { Field, FormMessage, SubmitButton, inputClass } from "./Form";
import { MathEditor } from "./MathEditor";
import { MathMarkdown } from "./MathMarkdown";

const DIFFICULTIES = [
  { value: 1, label: "1 · Application directe du cours" },
  { value: 2, label: "2 · Exercice classique" },
  { value: 3, label: "3 · Demande une idée" },
  { value: 4, label: "4 · Difficile" },
  { value: 5, label: "5 · Très difficile" },
];

const SOURCES = [
  { value: "personnel", label: "Création personnelle" },
  { value: "inspire", label: "Inspiré d'un ouvrage ou d'un sujet" },
  { value: "reproduit", label: "Reproduit avec autorisation" },
];

const MAX_HINTS = 5;
// Recherche des exercices proches pendant la rédaction : dès 80 caractères, 2 s après la frappe.
const SIMILAR_MIN_LENGTH = 80;
const SIMILAR_DELAY_MS = 2000;

function duplicateCandidates(body: unknown) {
  const candidates = (body as { candidates?: SimilarExercise[] } | null)?.candidates;
  return Array.isArray(candidates) && candidates.length > 0 ? candidates : null;
}

export const LATEX_HELP =
  "Markdown et LaTeX : $x^2$ dans le texte, $$\\sum_n u_n$$ en bloc. Macros disponibles : \\R, \\N, \\Z, \\Q, \\C, \\K.";

/** Case à cocher façon terminal : [ ] ou [x]. */
function Chip({ name, value, label }: { name: string; value: string; label: string }) {
  return (
    <label className="group cursor-pointer rounded-sm px-2 py-1 hover:bg-surface-soft has-focus-visible:outline has-focus-visible:outline-1 has-focus-visible:outline-ink">
      <input type="checkbox" name={name} value={value} className="sr-only" />
      <span aria-hidden="true" className="text-ash group-has-checked:hidden">
        [ ]
      </span>
      <span aria-hidden="true" className="hidden font-bold group-has-checked:inline">
        [x]
      </span>{" "}
      <span className="group-has-checked:font-medium">{label}</span>
    </label>
  );
}

export function ExerciseForm({
  levels,
  topics,
  defaultLevel,
}: {
  levels: Level[];
  topics: Topic[];
  defaultLevel: string | null;
}) {
  const router = useRouter();
  const [statement, setStatement] = useState("");
  const preview = useDeferredValue(statement);
  const [primaryLevel, setPrimaryLevel] = useState(defaultLevel ?? levels[0]?.code ?? "");
  const [sourceType, setSourceType] = useState("personnel");
  const [hints, setHints] = useState<string[]>([""]);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  // Brouillon déjà enregistré : après l'écran des doublons, on le modifie au lieu d'en créer un autre.
  const [draftId, setDraftId] = useState<number | null>(null);
  const [similar, setSimilar] = useState<SimilarExercise[]>([]);
  const [candidates, setCandidates] = useState<SimilarExercise[] | null>(null);

  // Énoncé trop court : le panneau se vide, sans attendre de réponse.
  const longEnough = statement.trim().length >= SIMILAR_MIN_LENGTH;

  useEffect(() => {
    if (!longEnough) return;
    let cancelled = false;
    const timer = setTimeout(async () => {
      const result = await apiPost<SimilarExercise[]>("/exercises/similar", {
        statement,
        exercise_id: draftId,
      });
      // Pas de message en cas d'échec : le panneau est une aide, la publication revérifie.
      if (!cancelled && result.ok) setSimilar(result.data);
    }, SIMILAR_DELAY_MS);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [statement, draftId, longEnough]);

  async function publish(id: number, choice?: PublishChoice) {
    setPending(true);
    setError(null);
    const published = await apiPost(`/exercises/${id}/publish`, choice ?? {});
    if (published.ok) {
      router.push(`/exercices/${id}`);
      router.refresh();
      return;
    }
    setPending(false);
    const found = published.status === 409 ? duplicateCandidates(published.body) : null;
    if (found) {
      setCandidates(found);
      window.scrollTo({ top: 0 });
    } else {
      setError(published.error);
    }
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (statement.trim().length < 10) return setError("L'énoncé fait au moins 10 caractères.");
    const form = new FormData(event.currentTarget);
    setPending(true);
    setError(null);
    const payload = {
      title: form.get("title"),
      statement,
      difficulty: Number(form.get("difficulty")),
      primary_level: primaryLevel,
      levels: form.getAll("levels"),
      topics: form.getAll("topics"),
      hints,
      final_answer: form.get("final_answer") ?? "",
      source_type: sourceType,
      source_reference: form.get("source_reference") ?? "",
    };
    // Brouillon puis publication : la publication vérifie les doublons.
    const draft =
      draftId === null
        ? await apiPost<{ id: number }>("/exercises", payload)
        : await apiPut<{ id: number }>(`/exercises/${draftId}`, payload);
    if (!draft.ok) {
      setPending(false);
      return setError(draft.error);
    }
    setDraftId(draft.data.id);
    await publish(draft.data.id);
  }

  return (
    <>
      {candidates && (
        <DuplicateScreen
          candidates={candidates}
          pending={pending}
          error={error}
          onPublish={(choice) => draftId !== null && publish(draftId, choice)}
          onBack={() => {
            setCandidates(null);
            setError(null);
          }}
        />
      )}
      {/* Masqué et non démonté pendant l'écran des doublons : les champs gardent leur saisie. */}
      <form onSubmit={onSubmit} hidden={candidates !== null} className="space-y-6">
        <Field label="Titre" htmlFor="title">
          <input id="title" name="title" required minLength={3} maxLength={200} className={inputClass} />
        </Field>

        <Field label="Énoncé" htmlFor="statement" hint={LATEX_HELP}>
          <MathEditor id="statement" label="Énoncé" value={statement} onChange={setStatement} />
        </Field>
        {preview.trim() && (
          <div aria-label="Aperçu de l'énoncé" className="border-l-2 border-hairline-strong bg-surface-soft px-4">
            <MathMarkdown>{preview}</MathMarkdown>
          </div>
        )}
        <SimilarPanel exercises={longEnough ? similar : []} />

        <div className="grid gap-6 sm:grid-cols-2">
          <Field label="Niveau principal" htmlFor="primary_level">
            <select
              id="primary_level"
              value={primaryLevel}
              onChange={(event) => setPrimaryLevel(event.target.value)}
              className={inputClass}
            >
              {levels.map((level) => (
                <option key={level.code} value={level.code}>
                  {level.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Difficulté" htmlFor="difficulty">
            <select id="difficulty" name="difficulty" defaultValue={2} className={inputClass}>
              {DIFFICULTIES.map((difficulty) => (
                <option key={difficulty.value} value={difficulty.value}>
                  {difficulty.label}
                </option>
              ))}
            </select>
          </Field>
        </div>

        <fieldset className="space-y-2">
          <legend className="font-medium">Aussi adapté à</legend>
          <div className="flex flex-wrap gap-2">
            {levels
              .filter((level) => level.code !== primaryLevel)
              .map((level) => (
                <Chip key={level.code} name="levels" value={level.code} label={level.code} />
              ))}
          </div>
        </fieldset>

        <fieldset className="space-y-2">
          <legend className="font-medium">Chapitres</legend>
          <div className="flex flex-wrap gap-2">
            {topics.map((topic) => (
              <Chip key={topic.slug} name="topics" value={topic.slug} label={topic.name} />
            ))}
          </div>
        </fieldset>

        <fieldset className="space-y-2">
          <legend className="font-medium">Indications progressives</legend>
          <p className="text-sm text-mute">Facultatives. Chacune est dévoilée à la demande.</p>
          {hints.map((hint, index) => (
            <textarea
              key={index}
              aria-label={`Indication ${index + 1}`}
              rows={2}
              value={hint}
              onChange={(event) =>
                setHints(hints.map((value, i) => (i === index ? event.target.value : value)))
              }
              className={`${inputClass} font-mono`}
            />
          ))}
          {hints.length < MAX_HINTS && (
            <button
              type="button"
              onClick={() => setHints([...hints, ""])}
              className="text-sm underline underline-offset-4"
            >
              Ajouter une indication
            </button>
          )}
        </fieldset>

        <Field
          label="Réponse finale (facultative)"
          htmlFor="final_answer"
          hint="Une valeur vérifiable, par exemple R = 2. Elle servira aux défis chronométrés et n'est pas affichée."
        >
          <input id="final_answer" name="final_answer" maxLength={500} className={inputClass} />
        </Field>

        <fieldset className="space-y-2">
          <legend className="font-medium">Origine de l&apos;exercice</legend>
          {SOURCES.map((source) => (
            <label key={source.value} className="flex items-center gap-2">
              <input
                type="radio"
                name="source_type"
                value={source.value}
                checked={sourceType === source.value}
                onChange={() => setSourceType(source.value)}
                className="shrink-0"
              />
              {source.label}
            </label>
          ))}
          {sourceType !== "personnel" && (
            <input
              name="source_reference"
              required
              maxLength={300}
              aria-label="Référence de la source"
              placeholder="Ouvrage, sujet ou auteur d'origine"
              className={inputClass}
            />
          )}
          <p className="text-sm text-mute">
            Reformule avec tes mots : la formulation d&apos;un énoncé publié ailleurs est protégée.
            Ta contribution est publiée sous licence CC BY-SA 4.0.
          </p>
        </fieldset>

        <FormMessage error={candidates ? null : error} />
        <SubmitButton pending={pending}>Publier l&apos;exercice</SubmitButton>
      </form>
    </>
  );
}
