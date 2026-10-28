"use client";

import Link from "next/link";
import { useState } from "react";

import type { SimilarExercise, SimilarityBand } from "@/lib/api";

import { Field, FormMessage, SubmitButton, inputClass } from "./Form";
import { MathMarkdown } from "./MathMarkdown";
import { Tag } from "./Tag";

export type PublishChoice =
  | { choice: "variante"; target_id: number }
  | { choice: "different"; note: string };

// Bandes les plus proches : étiquette sombre.
const STRONG_BANDS: SimilarityBand[] = ["quasi_copie", "tres_similaire"];

function solutionsLabel(count: number) {
  if (count === 0) return "aucune solution validée";
  return `${count} solution${count > 1 ? "s" : ""} validée${count > 1 ? "s" : ""}`;
}

function SimilarHeader({ exercise }: { exercise: SimilarExercise }) {
  return (
    <p className="flex flex-wrap items-center gap-x-3 gap-y-1">
      <Tag strong={STRONG_BANDS.includes(exercise.band)}>{exercise.band_label}</Tag>
      <Link
        href={`/exercices/${exercise.id}`}
        target="_blank"
        className="font-medium underline underline-offset-4"
      >
        {exercise.title}
      </Link>
      <span className="text-sm text-mute">
        [{exercise.primary_level}] · {solutionsLabel(exercise.validated_solutions)}
      </span>
    </p>
  );
}

/** Panneau « Exercices proches », mis à jour pendant la rédaction. */
export function SimilarPanel({ exercises }: { exercises: SimilarExercise[] }) {
  if (exercises.length === 0) return null;
  return (
    <aside aria-labelledby="exercices-proches" className="border border-hairline px-4 py-3">
      <h2 id="exercices-proches" className="font-bold">
        [!] Exercices proches
      </h2>
      <p className="text-sm text-mute">
        Vérifie que ton exercice n&apos;existe pas déjà. Rien n&apos;est bloqué pour autant.
      </p>
      <ul className="mt-2 space-y-2">
        {exercises.map((exercise) => (
          <li key={exercise.id}>
            <SimilarHeader exercise={exercise} />
            <details>
              <summary className="text-sm text-mute">Voir l&apos;énoncé</summary>
              <MathMarkdown>{exercise.statement}</MathMarkdown>
            </details>
          </li>
        ))}
      </ul>
    </aside>
  );
}

/** Écran « Cet exercice existe peut-être déjà », après une publication refusée en 409. */
export function DuplicateScreen({
  candidates,
  pending,
  error,
  onPublish,
  onBack,
}: {
  candidates: SimilarExercise[];
  pending: boolean;
  error: string | null;
  onPublish: (choice: PublishChoice) => void;
  onBack: () => void;
}) {
  const variant = candidates.find((candidate) => candidate.band === "variante");
  const [answer, setAnswer] = useState<"meme" | "variante" | "different" | null>(
    variant ? "variante" : null,
  );
  const [targetId, setTargetId] = useState(variant?.id ?? candidates[0].id);
  const [note, setNote] = useState("");
  const several = candidates.length > 1;

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (answer === "variante") onPublish({ choice: "variante", target_id: targetId });
    if (answer === "different") onPublish({ choice: "different", note });
  }

  const choiceClass = "flex gap-2 rounded-sm border border-hairline px-3 py-2 has-checked:border-ink has-checked:bg-surface-soft";

  return (
    <section aria-labelledby="doublon" className="space-y-5">
      <div>
        <h2 id="doublon" className="text-xl font-bold">
          Cet exercice existe peut-être déjà
        </h2>
        <p className="mt-1 text-sm text-mute">
          {several ? "Des exercices publiés ressemblent" : "Un exercice publié ressemble"} beaucoup au
          tien. Ton exercice n&apos;est pas encore publié : dis-nous ce qu&apos;il en est.
        </p>
      </div>

      {candidates.map((candidate) => (
        <article key={candidate.id} className="border border-hairline px-4 py-3">
          <SimilarHeader exercise={candidate} />
          <MathMarkdown>{candidate.statement}</MathMarkdown>
        </article>
      ))}

      <form onSubmit={onSubmit} className="space-y-3">
        <fieldset className="space-y-2">
          <legend className="font-medium">Par rapport {several ? "à ces exercices" : "à cet exercice"}, le tien est…</legend>

          <label className={choiceClass}>
            <input
              type="radio"
              name="answer"
              value="meme"
              checked={answer === "meme"}
              onChange={() => setAnswer("meme")}
              className="shrink-0"
            />
            <span>
              Le même exercice
              <span className="block text-mute">
                Va voir ses solutions, ou propose la tienne : c&apos;est là qu&apos;elle sera lue.
              </span>
            </span>
          </label>
          {answer === "meme" && (
            <ul className="space-y-1 pl-6">
              {candidates.map((candidate) => (
                <li key={candidate.id}>
                  <Link href={`/exercices/${candidate.id}`} className="underline underline-offset-4">
                    Ouvrir « {candidate.title} »
                  </Link>
                </li>
              ))}
            </ul>
          )}

          <label className={choiceClass}>
            <input
              type="radio"
              name="answer"
              value="variante"
              checked={answer === "variante"}
              onChange={() => setAnswer("variante")}
              className="shrink-0"
            />
            <span>
              Une variante
              <span className="block text-mute">
                Une autre valeur, une hypothèse en plus ou en moins : il sera publié en lien avec l&apos;existant.
              </span>
            </span>
          </label>
          {answer === "variante" && several && (
            <div className="space-y-1 pl-6">
              {candidates.map((candidate) => (
                <label key={candidate.id} className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="target"
                    value={candidate.id}
                    checked={targetId === candidate.id}
                    onChange={() => setTargetId(candidate.id)}
                    className="shrink-0"
                  />
                  Variante de « {candidate.title} »
                </label>
              ))}
            </div>
          )}

          <label className={choiceClass}>
            <input
              type="radio"
              name="answer"
              value="different"
              checked={answer === "different"}
              onChange={() => setAnswer("different")}
              className="shrink-0"
            />
            <span>
              Un exercice différent
              <span className="block text-mute">
                Il est publié tout de suite. Un modérateur regardera la paire, sans pénalité pour toi.
              </span>
            </span>
          </label>
          {answer === "different" && (
            <div className="pl-6">
              <Field label="Ce qui change, en une phrase" htmlFor="duplicate-note">
                <input
                  id="duplicate-note"
                  required
                  maxLength={300}
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  className={inputClass}
                />
              </Field>
            </div>
          )}
        </fieldset>

        <FormMessage error={error} />
        <div className="flex flex-wrap items-center gap-4">
          {answer === "variante" && <SubmitButton pending={pending}>Publier comme variante</SubmitButton>}
          {answer === "different" && <SubmitButton pending={pending}>Publier mon exercice</SubmitButton>}
          <button type="button" onClick={onBack} className="underline underline-offset-4">
            Revenir à mon énoncé
          </button>
        </div>
      </form>
    </section>
  );
}
