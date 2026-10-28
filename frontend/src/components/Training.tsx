"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import type { AiUsage, TrainingOptions, TrainingSession } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { AI_USAGE_OPTIONS, SOLUTION_STATUS_LABELS } from "@/lib/labels";

import { LATEX_HELP } from "./ExerciseForm";
import { Field, FormMessage, SubmitButton, inputClass, primaryButtonClass, secondaryButtonClass } from "./Form";
import { MathMarkdown } from "./MathMarkdown";

// Sauvegarde automatique, qui sert aussi de signe de vie au chrono du serveur.
const SAVE_EVERY_MS = 10_000;
// Rappels annoncés au lecteur d'écran, et seuls visibles quand le chrono est masqué.
const REMINDERS_S = [600, 300, 60];
const WARNING_S = 300;

/** 754 s → « 12:34 » ; 3725 s → « 1:02:05 ». */
export function clock(seconds: number) {
  const total = Math.max(0, Math.round(seconds));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const pad = (n: number) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
}

function storageKey(id: number) {
  return `ximaths:entrainement:${id}`;
}

/** Écran des règles : durée, tiers-temps, puis « Commencer ». */
export function TrainingStart({
  exerciseId,
  options,
  tiersTemps,
}: {
  exerciseId: number;
  options: TrainingOptions;
  tiersTemps: boolean;
}) {
  const router = useRouter();
  const [minutes, setMinutes] = useState(options.recommended);
  const [extraTime, setExtraTime] = useState(tiersTemps);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    if (extraTime !== tiersTemps) {
      const saved = await apiPost("/auth/preferences", { tiers_temps: extraTime });
      if (!saved.ok) {
        setPending(false);
        return setError(saved.error);
      }
    }
    const started = await apiPost<TrainingSession>("/training/sessions", {
      exercise_id: exerciseId,
      minutes,
    });
    if (!started.ok) {
      setPending(false);
      return setError(started.error);
    }
    router.push(`/entrainement/${started.data.id}`);
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <fieldset className="space-y-2">
        <legend className="font-medium">Durée</legend>
        {options.durations.map((value) => (
          <label key={value} className="flex gap-2">
            <input
              type="radio"
              name="minutes"
              value={value}
              checked={minutes === value}
              onChange={() => setMinutes(value)}
              className="shrink-0"
            />
            <span>
              {value} min{value === options.recommended && <span className="text-mute"> · temps conseillé</span>}
            </span>
          </label>
        ))}
      </fieldset>
      <label className="group flex cursor-pointer gap-2">
        <input
          type="checkbox"
          checked={extraTime}
          onChange={(event) => setExtraTime(event.target.checked)}
          className="sr-only"
        />
        <span aria-hidden="true" className="shrink-0 text-ash group-has-checked:hidden">
          [ ]
        </span>
        <span aria-hidden="true" className="hidden shrink-0 font-bold group-has-checked:inline">
          [x]
        </span>
        <span>
          J&apos;ai un tiers-temps <span className="text-mute">· durée ×1,33, comme aux concours</span>
        </span>
      </label>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Commencer</SubmitButton>
    </form>
  );
}

type Panel = "enonce" | "solution" | "apercu";
const PANELS: { value: Panel; label: string }[] = [
  { value: "enonce", label: "Énoncé" },
  { value: "solution", label: "Solution" },
  { value: "apercu", label: "Aperçu" },
];

/** La session : chrono fixé en haut, énoncé, brouillon, aperçu, rendu. */
export function TrainingRoom({ initial }: { initial: TrainingSession }) {
  const [session, setSession] = useState(initial);
  const [draft, setDraft] = useState(initial.draft);
  const [answer, setAnswer] = useState(initial.final_answer);
  const [aiUsage, setAiUsage] = useState<AiUsage>("aucune");
  const [remaining, setRemaining] = useState(initial.remaining_s);
  const [hidden, setHidden] = useState(false);
  const [panel, setPanel] = useState<Panel>("enonce");
  const [announce, setAnnounce] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  // Compteurs envoyés à la prochaine sauvegarde.
  const unsent = useRef({ focusLosses: 0, pasteChars: 0 });
  const lastInternalCopy = useRef("");
  const latest = useRef({ draft, answer, aiUsage });
  const autoSubmitted = useRef(false);
  const running = session.status === "en_cours";

  useEffect(() => {
    latest.current = { draft, answer, aiUsage };
  }, [draft, answer, aiUsage]);
  const open = running || session.status === "en_pause";

  // Brouillon gardé aussi dans le navigateur, si le réseau tombe.
  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(storageKey(initial.id));
      if (stored && !initial.draft) setDraft(stored);
    } catch {
      // Stockage indisponible (navigation privée) : le serveur garde la copie.
    }
  }, [initial.id, initial.draft]);

  useEffect(() => {
    try {
      window.localStorage.setItem(storageKey(session.id), draft);
    } catch {
      // Idem : sans stockage local, la sauvegarde serveur suffit.
    }
  }, [draft, session.id]);

  const call = useCallback(
    async (path: string, body?: unknown) => {
      const result = await apiPost<TrainingSession>(`/training/sessions/${session.id}${path}`, body);
      if (!result.ok) {
        setError(result.error);
        return null;
      }
      setError(null);
      setSession(result.data);
      setRemaining(result.data.remaining_s);
      return result.data;
    },
    [session.id],
  );

  const submit = useCallback(async () => {
    setPending(true);
    const { draft: body, answer: finalAnswer, aiUsage: usage } = latest.current;
    await call("/submit", { draft: body, final_answer: finalAnswer, ai_usage: usage });
    setPending(false);
  }, [call]);

  // Seconde par seconde, en local ; la sauvegarde recale sur le serveur.
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      setRemaining((value) => {
        const next = value - 1;
        const crossed = REMINDERS_S.find((threshold) => value > threshold && next <= threshold);
        if (crossed) setAnnounce(`Il reste ${crossed / 60} minute${crossed > 60 ? "s" : ""}.`);
        return next;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [running]);

  // Échéance : rendu automatique de la dernière version, une seule fois. Si l'appel
  // échoue, la sauvegarde suivante arrivera après l'échéance et le serveur rendra seul.
  useEffect(() => {
    if (running && remaining <= 0 && !autoSubmitted.current) {
      autoSubmitted.current = true;
      void submit();
    }
  }, [running, remaining, submit]);

  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      const counters = unsent.current;
      unsent.current = { focusLosses: 0, pasteChars: 0 };
      void call("/save", {
        draft: latest.current.draft,
        final_answer: latest.current.answer,
        focus_losses: counters.focusLosses,
        external_paste_chars: counters.pasteChars,
      });
    }, SAVE_EVERY_MS);
    return () => clearInterval(timer);
  }, [running, call]);

  // Sorties d'onglet : comptées et affichées, jamais pénalisées.
  useEffect(() => {
    function onVisibility() {
      if (document.hidden && running) unsent.current.focusLosses += 1;
    }
    document.addEventListener("visibilitychange", onVisibility);
    return () => document.removeEventListener("visibilitychange", onVisibility);
  }, [running]);

  if (!open) return <TrainingResult session={session} />;

  const panelClass = (value: Panel) => (panel === value ? "block" : "hidden md:block");
  const warning = remaining <= WARNING_S;

  return (
    <div>
      <div className="sticky top-0 z-10 -mx-4 flex flex-wrap items-center justify-between gap-x-6 gap-y-2 bg-surface-dark px-4 py-3 text-on-dark sm:mx-0">
        <p className="font-medium">
          <span className="text-ash">chrono </span>
          {hidden ? (
            <span className="text-ash">masqué · rappels à 10, 5 et 1 min</span>
          ) : (
            <span className={`tabular-nums ${warning ? "text-warning" : ""}`}>{clock(remaining)}</span>
          )}
          {session.status === "en_pause" && <span className="text-ash"> [pause]</span>}
        </p>
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
          <button type="button" onClick={() => setHidden(!hidden)} className="text-ash hover:text-on-dark">
            [{hidden ? "afficher" : "masquer"}]
          </button>
          {running ? (
            <button
              type="button"
              disabled={session.pauses_left === 0}
              onClick={() => call("/pause")}
              className="text-ash hover:text-on-dark disabled:opacity-50"
            >
              [pause · {session.pauses_left} restante{session.pauses_left > 1 ? "s" : ""}]
            </button>
          ) : (
            <button type="button" onClick={() => call("/resume")} className="text-on-dark underline">
              [reprendre]
            </button>
          )}
        </p>
      </div>
      <p aria-live="polite" className="sr-only">
        {announce}
      </p>

      <h1 className="mt-8">{session.exercise_title}</h1>
      <p className="mt-2 text-sm text-mute">
        Entraînement non classé · documents autorisés · sauvegarde toutes les 10 s · sorties
        d&apos;onglet : {session.focus_losses}
      </p>

      <div role="tablist" aria-label="Sections" className="mt-6 flex border-b border-hairline-strong md:hidden">
        {PANELS.map((item) => (
          <button
            key={item.value}
            type="button"
            role="tab"
            aria-selected={panel === item.value}
            onClick={() => setPanel(item.value)}
            className={`-mb-px border-b-2 px-4 py-1 font-medium leading-8 ${
              panel === item.value ? "border-ink text-ink" : "border-transparent text-mute"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {session.status === "en_pause" ? (
        <p className="mt-8 border-l-2 border-ink pl-3">
          [pause] L&apos;énoncé et ton brouillon sont masqués pendant la pause.
        </p>
      ) : (
        <>
          <section aria-label="Énoncé" className={`mt-6 ${panelClass("enonce")}`}>
            <h2 className="border-b border-hairline pb-2 font-bold">Énoncé</h2>
            <MathMarkdown>{session.statement}</MathMarkdown>
            {session.hints.map((hint, index) => (
              <details key={index} className="border-b border-hairline py-3">
                <summary className="font-medium">Indication {index + 1}</summary>
                <MathMarkdown>{hint}</MathMarkdown>
              </details>
            ))}
          </section>

          <section aria-label="Solution" className={`mt-10 space-y-4 ${panelClass("solution")}`}>
            <h2 className="border-b border-hairline pb-2 font-bold">Ta solution</h2>
            <Field
              label="Justification"
              htmlFor="training-draft"
              hint={`${LATEX_HELP} Les collages venus d'ailleurs sont comptés (leur taille, jamais leur contenu).`}
            >
              <textarea
                id="training-draft"
                rows={12}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                // Un copier-coller à l'intérieur du brouillon n'est pas un collage externe.
                onCopy={(event) => {
                  const area = event.currentTarget;
                  lastInternalCopy.current = area.value.slice(area.selectionStart, area.selectionEnd);
                }}
                onCut={(event) => {
                  const area = event.currentTarget;
                  lastInternalCopy.current = area.value.slice(area.selectionStart, area.selectionEnd);
                }}
                onPaste={(event) => {
                  const text = event.clipboardData.getData("text");
                  if (text && text !== lastInternalCopy.current) unsent.current.pasteChars += text.length;
                }}
                className={inputClass}
              />
            </Field>
            {session.has_final_answer && (
              <Field
                label="Réponse finale"
                htmlFor="training-answer"
                hint="Une valeur, par exemple 2, sqrt(2)/2 ou pi/4. Elle est vérifiée au rendu."
              >
                <input
                  id="training-answer"
                  value={answer}
                  maxLength={200}
                  onChange={(event) => setAnswer(event.target.value)}
                  className={inputClass}
                />
              </Field>
            )}
            <fieldset className="space-y-2">
              <legend className="font-medium">As-tu utilisé une IA ?</legend>
              {AI_USAGE_OPTIONS.map((option) => (
                <label key={option.value} className="flex gap-2">
                  <input
                    type="radio"
                    name="training-ai"
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
          </section>

          <section aria-label="Aperçu" className={`mt-10 ${panelClass("apercu")}`}>
            <h2 className="border-b border-hairline pb-2 font-bold">Aperçu</h2>
            {draft.trim() ? (
              <div className="border-l-2 border-hairline-strong bg-surface-soft px-4">
                <MathMarkdown>{draft}</MathMarkdown>
              </div>
            ) : (
              <p className="mt-3 text-mute">Ton brouillon s&apos;affichera ici.</p>
            )}
          </section>
        </>
      )}

      <div className="mt-10 flex flex-wrap items-center gap-4 border-t border-hairline pt-6">
        <button type="button" disabled={pending} onClick={submit} className={primaryButtonClass}>
          {pending ? "Un instant…" : "Rendre ma copie"}
        </button>
        <button
          type="button"
          onClick={() => {
            if (window.confirm("Abandonner cette session ? Ton brouillon ne sera pas envoyé.")) void call("/abandon");
          }}
          className={secondaryButtonClass}
        >
          Abandonner
        </button>
      </div>
      <div className="mt-4">
        <FormMessage error={error} />
      </div>
    </div>
  );
}

function TrainingResult({ session }: { session: TrainingSession }) {
  const [rated, setRated] = useState(session.self_rating);
  const [error, setError] = useState<string | null>(null);

  if (session.status === "abandonnee") {
    return (
      <div>
        <h1>{session.exercise_title}</h1>
        <p className="mt-4">[-] Session abandonnée. Rien n&apos;a été envoyé.</p>
        <p className="mt-6">
          <Link href={`/exercices/${session.exercise_id}`} className="underline underline-offset-4">
            Revenir à l&apos;exercice
          </Link>
        </p>
      </div>
    );
  }

  const median = session.median_elapsed_s;
  const verdict =
    session.answer_correct === true
      ? "[+] Réponse finale juste."
      : session.answer_correct === false
        ? "[x] Réponse finale différente de celle attendue."
        : session.has_final_answer
          ? "[-] Réponse finale absente ou illisible : rien à vérifier automatiquement."
          : "[-] Cet exercice n'a pas de réponse finale à vérifier.";

  return (
    <div>
      <p className="text-sm text-mute">Entraînement rendu</p>
      <h1>{session.exercise_title}</h1>

      <dl className="mt-8 grid grid-cols-2 border-y border-hairline">
        <div className="flex flex-col-reverse py-4">
          <dt className="text-sm text-mute">temps utilisé, sur {clock(session.limit_s)}</dt>
          <dd className="text-[28px] font-bold leading-normal tabular-nums">{clock(session.elapsed_s)}</dd>
        </div>
        <div className="flex flex-col-reverse border-l border-hairline px-4 py-4">
          <dt className="text-sm text-mute">médiane des autres sessions</dt>
          <dd className="text-[28px] font-bold leading-normal tabular-nums">{median === null ? "—" : clock(median)}</dd>
        </div>
      </dl>

      <ul className="mt-6 space-y-2">
        <li>{verdict}</li>
        <li>
          {session.solution_status
            ? `[+] Ta justification est envoyée : ${SOLUTION_STATUS_LABELS[session.solution_status].toLowerCase()}. Trois membres la liront.`
            : "[-] Justification trop courte : elle n'a pas été envoyée en relecture."}
        </li>
        <li className="text-mute">
          [i] Sorties d&apos;onglet : {session.focus_losses}. Elles ne sont jamais pénalisées.
        </li>
      </ul>

      <section aria-labelledby="auto-evaluation" className="mt-12">
        <h2 id="auto-evaluation" className="border-b border-hairline pb-2 font-bold">
          Quelle difficulté, pour toi ?
        </h2>
        {rated ? (
          <p className="mt-3">[+] Merci : tu as noté {rated} sur 5. Cela affine la difficulté de l&apos;exercice.</p>
        ) : (
          <div className="mt-3 flex flex-wrap gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <button
                key={value}
                type="button"
                onClick={async () => {
                  const result = await apiPost<TrainingSession>(`/training/sessions/${session.id}/rating`, {
                    rating: value,
                  });
                  if (result.ok) setRated(value);
                  else setError(result.error);
                }}
                className={secondaryButtonClass}
              >
                {value}
              </button>
            ))}
          </div>
        )}
        <div className="mt-3">
          <FormMessage error={error} />
        </div>
      </section>

      <p className="mt-12 flex flex-wrap gap-x-6 gap-y-2">
        <Link href={`/exercices/${session.exercise_id}#solutions`} className="underline underline-offset-4">
          Voir les solutions validées
        </Link>
        <Link href="/" className="underline underline-offset-4">
          Un autre exercice
        </Link>
      </p>
    </div>
  );
}
