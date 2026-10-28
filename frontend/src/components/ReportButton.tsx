"use client";

import Link from "next/link";
import { useState } from "react";

import type { ReportTarget } from "@/lib/api";
import { apiPost } from "@/lib/client-api";

import { Field, FormMessage, SubmitButton, inputClass } from "./Form";

const REASONS: Record<ReportTarget, { value: string; label: string; help: string }[]> = {
  exercise: [
    { value: "erreur", label: "Erreur dans l'énoncé", help: "Hypothèse manquante, énoncé faux ou ambigu." },
    { value: "doublon", label: "Doublon", help: "Le même exercice existe déjà sur XiMaths." },
    { value: "plagiat", label: "Plagiat", help: "Recopié d'un livre ou d'un site sans autorisation." },
    { value: "inapproprie", label: "Contenu inapproprié", help: "Hors sujet, injurieux ou illicite." },
  ],
  solution: [
    { value: "erreur", label: "Erreur dans la solution", help: "Une étape est fausse malgré la validation." },
    { value: "plagiat", label: "Plagiat", help: "Recopiée d'un livre, d'un site ou d'un autre membre." },
    { value: "ia_non_declaree", label: "IA non déclarée", help: "Semble générée sans que ce soit déclaré." },
    { value: "inapproprie", label: "Contenu inapproprié", help: "Hors sujet, injurieux ou illicite." },
  ],
};

/** « https://…/exercices/12 », « /exercices/12 » ou « 12 » → 12. */
function exerciseIdFrom(input: string) {
  const match = input.trim().match(/(\d+)\/?$/);
  return match ? Number(match[1]) : null;
}

export function ReportButton({
  target,
  targetId,
  canReportDuplicates,
}: {
  target: ReportTarget;
  targetId: number;
  canReportDuplicates: boolean;
}) {
  const reasons = REASONS[target].filter((reason) => reason.value !== "doublon" || canReportDuplicates);
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState(reasons[0].value);
  const [details, setDetails] = useState("");
  const [original, setOriginal] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [done, setDone] = useState(false);

  if (done) {
    return (
      <p role="status" className="text-sm text-mute">
        Merci : un modérateur va regarder.{" "}
        <Link href="/signalements" className="underline underline-offset-4">
          Suivre mes signalements
        </Link>
      </p>
    );
  }
  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="text-sm text-mute hover:text-ink hover:underline"
      >
        [!] signaler
      </button>
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    let duplicateOf: number | null = null;
    if (reason === "doublon") {
      duplicateOf = exerciseIdFrom(original);
      if (duplicateOf === null) return setError("Colle le lien de l'exercice d'origine, ou son numéro.");
    }
    setPending(true);
    setError(null);
    const result = await apiPost("/reports", {
      target,
      target_id: targetId,
      reason,
      details,
      duplicate_of: duplicateOf,
    });
    setPending(false);
    if (result.ok) setDone(true);
    else setError(result.error);
  }

  return (
    <form
      onSubmit={onSubmit}
      aria-label={target === "exercise" ? "Signaler l'exercice" : "Signaler la solution"}
      className="mt-2 w-full space-y-3 border border-hairline px-4 py-3"
    >
      <fieldset className="space-y-1.5">
        <legend className="font-medium">Que se passe-t-il ?</legend>
        {reasons.map((option) => (
          <label key={option.value} className="flex gap-2">
            <input
              type="radio"
              name={`reason-${target}-${targetId}`}
              value={option.value}
              checked={reason === option.value}
              onChange={() => setReason(option.value)}
              className="shrink-0"
            />
            <span>
              {option.label} <span className="text-mute">· {option.help}</span>
            </span>
          </label>
        ))}
      </fieldset>
      {reason === "doublon" && (
        <Field label="Exercice d'origine" htmlFor={`original-${targetId}`} hint="Son lien ou son numéro.">
          <input
            id={`original-${targetId}`}
            required
            value={original}
            onChange={(event) => setOriginal(event.target.value)}
            placeholder="https://ximaths…/exercices/12"
            className={inputClass}
          />
        </Field>
      )}
      <Field label="Précisions (facultatif)" htmlFor={`details-${target}-${targetId}`}>
        <textarea
          id={`details-${target}-${targetId}`}
          rows={2}
          maxLength={1000}
          value={details}
          onChange={(event) => setDetails(event.target.value)}
          className={inputClass}
        />
      </Field>
      <p className="text-sm text-mute">
        Ton signalement reste confidentiel : l&apos;auteur ne saura pas qui l&apos;a fait.
      </p>
      <FormMessage error={error} />
      <div className="flex items-center gap-4">
        <SubmitButton pending={pending}>Envoyer le signalement</SubmitButton>
        <button type="button" onClick={() => setOpen(false)} className="text-sm text-mute hover:text-ink">
          Annuler
        </button>
      </div>
    </form>
  );
}
