"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import type { AiUsage, TrainingOptions, TrainingSession } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { SOLUTION_STATUS_LABELS } from "@/lib/labels";

import { AiUsageChoice } from "./ContributionForms";
import { CopyPhotoPicker } from "./CopyPhotoPicker";
import { FormMessage, SubmitButton, primaryButtonClass, secondaryButtonClass } from "./Form";
import { MathMarkdown } from "./MathMarkdown";
import { MathText } from "./MathText";

// Signe de vie au chrono du serveur.
const SAVE_EVERY_MS = 10_000;
// Rappels annoncés au lecteur d'écran, et seuls visibles quand le chrono est masqué.
const REMINDERS_S = [600, 300, 60];
const WARNING_S = 300;

/** 754 s → « 12:34 » ; 3725 s → « 1:02:05 ». */
export function clock(seconds: number) {
  const total = Math.max(0, Math.round(seconds));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const pad = (n: number) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
}

/** Écran des règles : la durée, puis « Commencer ». */
export function TrainingStart({ exerciseId, options }: { exerciseId: number; options: TrainingOptions }) {
  const router = useRouter();
  const [minutes, setMinutes] = useState(options.recommended);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
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
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Commencer</SubmitButton>
    </form>
  );
}

/** « Commencer » un défi : le chrono part au clic, et la tentative est unique. */
export function ChallengeStart({ challengeId, minutes }: { challengeId: number; minutes: number }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function start() {
    setPending(true);
    setError(null);
    const started = await apiPost<TrainingSession>(`/challenges/${challengeId}/start`);
    if (!started.ok) {
      setPending(false);
      return setError(started.error);
    }
    router.push(`/entrainement/${started.data.id}`);
  }

  return (
    <div className="space-y-3">
      <button type="button" disabled={pending} onClick={start} className={primaryButtonClass}>
        {pending ? "Un instant…" : `Commencer · ${minutes} min`}
      </button>
      <FormMessage error={error} />
    </div>
  );
}

type Panel = "enonce" | "copie";
const PANELS: { value: Panel; label: string }[] = [
  { value: "enonce", label: "Énoncé" },
  { value: "copie", label: "Ma copie" },
];

// Après la fin du chrono, une minute pour que les dernières photos arrivent.
const GRACE_S = 60;

/** La session : chrono fixé en haut, énoncé, copie photographiée depuis le téléphone, rendu. */
export function TrainingRoom({ initial }: { initial: TrainingSession }) {
  const [session, setSession] = useState(initial);
  const [photoCount, setPhotoCount] = useState(initial.photo_count);
  const [aiUsage, setAiUsage] = useState<AiUsage>("aucune");
  const [remaining, setRemaining] = useState(initial.remaining_s);
  const [hidden, setHidden] = useState(false);
  const [panel, setPanel] = useState<Panel>("enonce");
  const [announce, setAnnounce] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  // Sorties d'onglet, envoyées au prochain signe de vie.
  const unsentFocusLosses = useRef(0);
  const latestAiUsage = useRef(aiUsage);
  const autoSubmitted = useRef(false);
  const running = session.status === "en_cours";
  // Défi du jour : classé, sans pause, sans IA.
  const ranked = session.kind === "defi";

  useEffect(() => {
    latestAiUsage.current = aiUsage;
  }, [aiUsage]);
  const open = running || session.status === "en_pause";

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
    await call("/submit", { ai_usage: latestAiUsage.current });
    setPending(false);
  }, [call]);

  // Seconde par seconde, en local ; le signe de vie recale sur le serveur. Le décompte
  // continue sous zéro pendant la minute de grâce.
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      setRemaining((value) => {
        const next = value - 1;
        const crossed = REMINDERS_S.find((threshold) => value > threshold && next <= threshold);
        if (crossed) setAnnounce(`Il reste ${crossed / 60} minute${crossed > 60 ? "s" : ""}.`);
        if (value > 0 && next <= 0) setAnnounce("Temps écoulé : une minute pour envoyer tes dernières photos.");
        return next;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [running]);

  // Fin de la minute de grâce : rendu automatique de ce qui est arrivé, une seule fois.
  // Si l'appel échoue, le signe de vie suivant arrivera trop tard et le serveur rendra seul.
  useEffect(() => {
    if (running && remaining <= -GRACE_S && !autoSubmitted.current) {
      autoSubmitted.current = true;
      void submit();
    }
  }, [running, remaining, submit]);

  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      const focusLosses = unsentFocusLosses.current;
      unsentFocusLosses.current = 0;
      void call("/save", { focus_losses: focusLosses });
    }, SAVE_EVERY_MS);
    return () => clearInterval(timer);
  }, [running, call]);

  // Sorties d'onglet : comptées et affichées, jamais pénalisées.
  useEffect(() => {
    function onVisibility() {
      if (document.hidden && running) unsentFocusLosses.current += 1;
    }
    document.addEventListener("visibilitychange", onVisibility);
    return () => document.removeEventListener("visibilitychange", onVisibility);
  }, [running]);

  if (!open) return <TrainingResult session={session} />;

  const panelClass = (value: Panel) => (panel === value ? "block" : "hidden md:block");
  const warning = remaining <= WARNING_S;
  const overtime = remaining <= 0;

  return (
    <div>
      <div className="sticky top-14 z-10 -mx-5 flex flex-wrap items-center justify-between gap-x-6 gap-y-2 bg-surface-dark px-5 py-3 text-on-dark sm:mx-0 sm:rounded-xl lg:top-2">
        <p className="font-medium">
          <span className="text-on-dark-mute">chrono </span>
          {overtime ? (
            <span className="text-warning">
              temps écoulé · dernières photos, encore {Math.max(0, GRACE_S + Math.round(remaining))} s
            </span>
          ) : hidden ? (
            <span className="text-on-dark-mute">masqué · rappels à 10, 5 et 1 min</span>
          ) : (
            <span className={`tabular-nums ${warning ? "text-warning" : ""}`}>{clock(remaining)}</span>
          )}
          {session.status === "en_pause" && <span className="text-on-dark-mute"> (en pause)</span>}
        </p>
        <p className="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
          <button type="button" onClick={() => setHidden(!hidden)} className="text-on-dark-mute hover:text-on-dark">
            [{hidden ? "afficher" : "masquer"}]
          </button>
          {ranked ? (
            <span className="text-on-dark-mute">défi · une seule tentative</span>
          ) : running ? (
            <button
              type="button"
              disabled={session.pauses_left === 0}
              onClick={() => call("/pause")}
              className="text-on-dark-mute hover:text-on-dark disabled:opacity-50"
            >
              Pause ({session.pauses_left} restante{session.pauses_left > 1 ? "s" : ""})
            </button>
          ) : (
            <button type="button" onClick={() => call("/resume")} className="text-on-dark underline">
              Reprendre
            </button>
          )}
        </p>
      </div>
      <p aria-live="polite" className="sr-only">
        {announce}
      </p>

      <h1 className="mt-8">
        <MathText>{session.exercise_title}</MathText>
      </h1>
      <p className="mt-2 text-sm text-mute">
        {ranked
          ? "Défi du jour classé · cours personnel autorisé · IA interdite · le chrono continue même onglet fermé"
          : "Entraînement non classé · documents autorisés"}{" "}
        · copie sur papier, photographiée avant la fin · sorties d&apos;onglet : {session.focus_losses}
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
        <p className="mt-8 border-l-2 border-ink pl-3">[pause] L&apos;énoncé est masqué pendant la pause.</p>
      ) : (
        <section aria-label="Énoncé" className={`mt-6 ${panelClass("enonce")}`}>
          <h2>Énoncé</h2>
          <MathMarkdown>{session.statement}</MathMarkdown>
          {ranked
            ? session.hints.map((hint, index) => (
                <div key={index} className="border-b border-hairline py-3">
                  <p className="font-medium">Indication {index + 1}</p>
                  <MathMarkdown>{hint}</MathMarkdown>
                </div>
              ))
            : session.hints.map((hint, index) => (
                <details key={index} className="border-b border-hairline py-3">
                  <summary className="font-medium">Indication {index + 1}</summary>
                  <MathMarkdown>{hint}</MathMarkdown>
                </details>
              ))}
          {ranked && session.hints_opened < session.hint_count && (
            <button type="button" onClick={() => call("/hint")} className="mt-3 underline underline-offset-4">
              Ouvrir l&apos;indication {session.hints_opened + 1} · −10 % de bonus de rapidité
            </button>
          )}
        </section>
      )}

      {/* La copie reste accessible en pause : les photos déjà prises s'y voient. */}
      <section aria-label="Ma copie" className={`mt-10 space-y-4 ${panelClass("copie")}`}>
        <h2>Ma copie</h2>
        <p className="text-body">
          Rédige sur papier. Quand tu as fini, photographie tes pages avec ton téléphone : elles doivent arriver avant
          la fin du temps, avec une minute de grâce.
        </p>
        <CopyPhotoPicker source={{ sessionId: session.id }} onChange={(picked) => setPhotoCount(picked.count)} />
        {ranked ? (
          <p className="text-sm text-mute">IA interdite pendant le défi : ta copie est relue par trois membres.</p>
        ) : (
          <AiUsageChoice name="training-ai" value={aiUsage} onChange={setAiUsage} />
        )}
      </section>

      <div className="mt-10 flex flex-wrap items-center gap-4 border-t border-hairline pt-6">
        <button
          type="button"
          disabled={pending}
          onClick={() => {
            if (
              photoCount === 0 &&
              !window.confirm("Aucune photo de ta copie n'est arrivée : rien ne partira en relecture. Rendre quand même ?")
            ) {
              return;
            }
            void submit();
          }}
          className={primaryButtonClass}
        >
          {pending ? "Un instant…" : `Rendre ma copie${photoCount > 0 ? ` (${photoCount} page${photoCount > 1 ? "s" : ""})` : ""}`}
        </button>
        <button
          type="button"
          onClick={() => {
            const question = ranked
              ? "Abandonner le défi ? Ta tentative sera consommée, sans autre pénalité."
              : "Abandonner cette session ? Tes photos ne seront pas envoyées.";
            if (window.confirm(question)) void call("/abandon");
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

  const ranked = session.kind === "defi";

  if (session.status === "abandonnee") {
    return (
      <div>
        <h1>
        <MathText>{session.exercise_title}</MathText>
      </h1>
        <p className="mt-4">
          {ranked
            ? "Défi abandonné. Ta tentative est consommée, sans autre pénalité."
            : "Session abandonnée. Rien n'a été envoyé."}
        </p>
        <p className="mt-6">
          <Link href={ranked ? "/defi" : `/exercices/${session.exercise_id}`} className="underline underline-offset-4">
            {ranked ? "Revenir aux défis" : "Revenir à l'exercice"}
          </Link>
        </p>
      </div>
    );
  }

  const median = session.median_elapsed_s;
  const pages = session.photo_count;

  return (
    <div>
      <p className="text-sm text-mute">{ranked ? "Défi du jour rendu" : "Entraînement rendu"}</p>
      <h1>
        <MathText>{session.exercise_title}</MathText>
      </h1>

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
        <li>
          {session.solution_status
            ? `Ta copie (${pages} page${pages > 1 ? "s" : ""}) est envoyée : ${SOLUTION_STATUS_LABELS[session.solution_status].toLowerCase()}. Trois membres la liront.`
            : "Aucune photo de ta copie n'est arrivée à temps : rien n'est parti en relecture."}
        </li>
        {ranked && <ChallengePoints session={session} />}
        <li className="text-mute">
          Sorties d&apos;onglet : {session.focus_losses}. Elles ne sont jamais pénalisées.
        </li>
      </ul>

      <section aria-labelledby="auto-evaluation" className="mt-12">
        <h2 id="auto-evaluation">
          Quelle difficulté, pour toi ?
        </h2>
        {rated ? (
          <p className="mt-3">Merci : tu as noté {rated} sur 5. Cela affine la difficulté de l&apos;exercice.</p>
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
        <Link href={`/exercices/${session.exercise_id}#ta-solution`} className="underline underline-offset-4">
          Suivre la correction de ma copie
        </Link>
        <Link href={ranked ? "/defi" : "/"} className="underline underline-offset-4">
          {ranked ? "Les autres défis" : "Un autre exercice"}
        </Link>
      </p>
    </div>
  );
}

const bonusFormat = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 });

/** Barème du défi : tous les points quand la copie est validée par les pairs. */
function ChallengePoints({ session }: { session: TrainingSession }) {
  const bonus = session.bonus === null ? "" : `, bonus de rapidité ×${bonusFormat.format(session.bonus)} compris`;
  return (
    <>
      {session.solution_status && (
        <li>
          +{session.justification_points} points si tes trois relecteurs la jugent juste{bonus}.
        </li>
      )}

    </>
  );
}
