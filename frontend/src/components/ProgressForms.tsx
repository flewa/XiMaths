"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { Topic } from "@/lib/api";
import { apiDelete, apiPost, apiPut } from "@/lib/client-api";

import { Field, FormMessage, SubmitButton, inputClass, secondaryButtonClass } from "./Form";

/** Objectif de la série : de 2 à 7 jours actifs par semaine. */
export function WeeklyGoalForm({ days }: { days: number }) {
  const router = useRouter();
  const [value, setValue] = useState(days);
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const saved = await apiPut("/progress/goal", { days: value });
    setPending(false);
    setResult(saved.ok ? { success: "Objectif enregistré." } : { error: saved.error });
    if (saved.ok) router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
      <Field label="Objectif" htmlFor="weekly-goal">
        <select
          id="weekly-goal"
          value={value}
          onChange={(event) => setValue(Number(event.target.value))}
          className={inputClass}
        >
          {[2, 3, 4, 5, 6, 7].map((n) => (
            <option key={n} value={n}>
              {n} jours actifs par semaine
            </option>
          ))}
        </select>
      </Field>
      <SubmitButton pending={pending}>Enregistrer</SubmitButton>
      <div className="basis-full">
        <FormMessage error={result.error} success={result.success} />
      </div>
    </form>
  );
}

function isoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

/** Mode examens ou vacances : la série est suspendue, 4 semaines au plus. */
export function VacationForm({ until }: { until: string | null }) {
  const router = useRouter();
  const [today] = useState(() => new Date());
  const [value, setValue] = useState(() => isoDate(new Date(today.getTime() + 14 * 86_400_000)));
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function toggle(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const saved = until ? await apiDelete("/progress/vacation") : await apiPost("/progress/vacation", { until: value });
    setPending(false);
    if (!saved.ok) return setError(saved.error);
    setError(null);
    router.refresh();
  }

  return (
    <form onSubmit={toggle} className="flex flex-wrap items-end gap-3">
      {!until && (
        <Field label="Jusqu'au" htmlFor="vacation-until">
          <input
            id="vacation-until"
            type="date"
            required
            min={isoDate(today)}
            max={isoDate(new Date(today.getTime() + 28 * 86_400_000))}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            className={inputClass}
          />
        </Field>
      )}
      <SubmitButton pending={pending}>{until ? "Reprendre la série" : "Activer"}</SubmitButton>
      <div className="basis-full">
        <FormMessage error={error} />
      </div>
    </form>
  );
}

/** Nouvel objectif personnel : un nombre d'exercices d'ici une date, ou des chronos par semaine. */
export function GoalForm({ topics }: { topics: Topic[] }) {
  const router = useRouter();
  const [kind, setKind] = useState<"solutions" | "chrono_semaine">("solutions");
  const [target, setTarget] = useState(10);
  const [deadline, setDeadline] = useState("");
  const [topic, setTopic] = useState("");
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const created = await apiPost("/goals", {
      kind,
      target,
      deadline,
      title,
      topic: kind === "solutions" && topic ? topic : null,
    });
    setPending(false);
    if (!created.ok) return setError(created.error);
    setError(null);
    setTitle("");
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-4 sm:grid-cols-2">
      <Field label="Type" htmlFor="goal-kind">
        <select
          id="goal-kind"
          value={kind}
          onChange={(event) => setKind(event.target.value as typeof kind)}
          className={inputClass}
        >
          <option value="solutions">Résoudre des exercices d&apos;ici une date</option>
          <option value="chrono_semaine">Des exercices chronométrés chaque semaine</option>
        </select>
      </Field>
      <Field label={kind === "solutions" ? "Nombre d'exercices" : "Chronos par semaine"} htmlFor="goal-target">
        <input
          id="goal-target"
          type="number"
          required
          min={1}
          max={200}
          value={target}
          onChange={(event) => setTarget(Number(event.target.value))}
          className={inputClass}
        />
      </Field>
      <Field label={kind === "solutions" ? "D'ici le" : "Jusqu'au"} htmlFor="goal-deadline">
        <input
          id="goal-deadline"
          type="date"
          required
          value={deadline}
          onChange={(event) => setDeadline(event.target.value)}
          className={inputClass}
        />
      </Field>
      {kind === "solutions" && (
        <Field label="Chapitre (facultatif)" htmlFor="goal-topic">
          <select id="goal-topic" value={topic} onChange={(event) => setTopic(event.target.value)} className={inputClass}>
            <option value="">Tous</option>
            {topics.map((item) => (
              <option key={item.slug} value={item.slug}>
                {item.name}
              </option>
            ))}
          </select>
        </Field>
      )}
      <div className="sm:col-span-2">
        <Field label="Intitulé (facultatif)" htmlFor="goal-title" hint="Par exemple : « Partiel d'algèbre linéaire ».">
          <input
            id="goal-title"
            maxLength={120}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className={inputClass}
          />
        </Field>
      </div>
      <div className="space-y-3 sm:col-span-2">
        <FormMessage error={error} />
        <SubmitButton pending={pending}>Ajouter l&apos;objectif</SubmitButton>
      </div>
    </form>
  );
}

export function DeleteGoalButton({ goalId }: { goalId: number }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  return (
    <button
      type="button"
      disabled={pending}
      onClick={async () => {
        setPending(true);
        const deleted = await apiDelete(`/goals/${goalId}`);
        setPending(false);
        if (deleted.ok) router.refresh();
      }}
      className={`${secondaryButtonClass} h-7 px-3 text-sm leading-[26px]`}
    >
      Retirer
    </button>
  );
}
