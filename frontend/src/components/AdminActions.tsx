"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { Level, PanelExerciseDetail, SolutionStatus, Topic } from "@/lib/api";
import { apiPost, apiPut } from "@/lib/client-api";
import { LEVEL_TRACKS } from "@/lib/labels";

import { Field, FormMessage, inputClass, primaryButtonClass, secondaryButtonClass } from "./Form";
import { LevelOptions } from "./LevelOptions";

const DIFFICULTIES = [1, 2, 3, 4, 5];

/** Envoi d'une action du panneau : état d'attente, erreur, succès, puis rafraîchissement. */
function useAction() {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  async function run(call: () => ReturnType<typeof apiPost>, done: string, after?: () => void) {
    setPending(true);
    setError(null);
    setSuccess(null);
    const result = await call();
    setPending(false);
    if (!result.ok) return setError(result.error);
    setSuccess(done);
    if (after) after();
    else router.refresh();
  }
  return { pending, error, success, run };
}

function Reason({ id, value, onChange, placeholder }: { id: string; value: string; onChange: (value: string) => void; placeholder?: string }) {
  return (
    <Field label="Motif, gardé au journal et envoyé à la personne concernée" htmlFor={id}>
      <textarea id={id} rows={2} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className={inputClass} />
    </Field>
  );
}

// ---------------------------------------------------------------- copies

const DECISIONS: { value: string; label: string; help: string; from: SolutionStatus[] }[] = [
  { value: "validate", label: "Valider", help: "Les points sont accordés à l'auteur.", from: ["under_review", "needs_work"] },
  { value: "needs_work", label: "Renvoyer à reprendre", help: "Sans points ; ceux d'une copie validée sont repris.", from: ["under_review", "validated"] },
  { value: "review_again", label: "Remettre en relecture", help: "Un nouveau tour, avec de nouveaux relecteurs.", from: ["needs_work", "validated"] },
  { value: "remove_plagiarism", label: "Retirer : plagiat", help: "Masquée, points annulés et 50 retirés ; l'auteur peut faire appel.", from: ["under_review", "validated", "needs_work"] },
  { value: "remove_inappropriate", label: "Retirer : contenu inapproprié", help: "Masquée, points annulés ; l'auteur peut faire appel.", from: ["under_review", "validated", "needs_work"] },
];

/** Décider d'une copie depuis le panneau. */
export function SolutionDecision({ id, status }: { id: number; status: SolutionStatus }) {
  const options = DECISIONS.filter((option) => option.from.includes(status));
  const [decision, setDecision] = useState(options[0]?.value ?? "");
  const [reason, setReason] = useState("");
  const { pending, error, success, run } = useAction();
  if (options.length === 0) return null;
  return (
    <details className="mt-2">
      <summary className="text-sm font-medium text-ink">Décider de cette copie</summary>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          run(() => apiPost(`/panel/solutions/${id}/decide`, { decision, reason }), "Décision enregistrée.");
        }}
        className="mt-3 space-y-3 rounded-xl border border-hairline p-3"
      >
        <fieldset className="space-y-1.5">
          <legend className="sr-only">Décision</legend>
          {options.map((option) => (
            <label key={option.value} className="flex cursor-pointer gap-2.5 text-sm">
              <input type="radio" name={`decision-${id}`} value={option.value} checked={decision === option.value} onChange={() => setDecision(option.value)} />
              <span>
                <span className="font-medium text-ink">{option.label}</span> <span className="text-mute">· {option.help}</span>
              </span>
            </label>
          ))}
        </fieldset>
        <Reason id={`motif-copie-${id}`} value={reason} onChange={setReason} />
        <button type="submit" disabled={pending || !reason.trim()} className={primaryButtonClass}>
          {pending ? "Enregistrement…" : "Appliquer"}
        </button>
        <FormMessage error={error} success={success} />
      </form>
    </details>
  );
}

// ---------------------------------------------------------------- exercices

/** Corriger un exercice : tout ce qu'un auteur peut écrire, plus son statut. */
export function ExerciseEditor({ initial, levels, topics }: { initial: PanelExerciseDetail; levels: Level[]; topics: Topic[] }) {
  const [form, setForm] = useState({ ...initial, hints: initial.hints.length ? initial.hints : [""] });
  const [reason, setReason] = useState("");
  const [statusReason, setStatusReason] = useState("");
  const save = useAction();
  const status = useAction();
  const set = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) => setForm((current) => ({ ...current, [key]: value }));
  const toggle = (key: "levels" | "topics", value: string) =>
    set(key, form[key].includes(value) ? form[key].filter((item) => item !== value) : [...form[key], value]);
  const chapters = topics.filter((topic) => topic.parent === null);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const payload = {
      title: form.title,
      statement: form.statement,
      hints: form.hints.map((hint) => hint.trim()).filter(Boolean),
      final_answer: form.final_answer,
      difficulty: form.difficulty,
      primary_level: form.primary_level,
      levels: form.levels,
      topics: form.topics,
      source_type: form.source_type,
      source_reference: form.source_reference,
      reason,
    };
    save.run(() => apiPut(`/panel/exercises/${initial.id}`, payload), "Exercice enregistré.");
  }

  return (
    <>
      <form onSubmit={submit} className="mt-6 space-y-5">
        <Field label="Titre" htmlFor="titre">
          <input id="titre" value={form.title} onChange={(event) => set("title", event.target.value)} maxLength={200} className={inputClass} />
        </Field>
        <Field label="Énoncé (Markdown et LaTeX)" htmlFor="enonce">
          <textarea id="enonce" rows={10} value={form.statement} onChange={(event) => set("statement", event.target.value)} className={`${inputClass} font-mono text-sm`} />
        </Field>
        <fieldset className="space-y-2">
          <legend className="font-medium text-ink">Indications</legend>
          {form.hints.map((hint, index) => (
            <div key={index} className="flex gap-2">
              <label htmlFor={`indication-${index}`} className="sr-only">
                Indication {index + 1}
              </label>
              <textarea
                id={`indication-${index}`}
                rows={2}
                value={hint}
                onChange={(event) => set("hints", form.hints.map((item, position) => (position === index ? event.target.value : item)))}
                className={`${inputClass} text-sm`}
              />
              <button type="button" onClick={() => set("hints", form.hints.filter((_, position) => position !== index))} className={secondaryButtonClass} aria-label={`Retirer l'indication ${index + 1}`}>
                Retirer
              </button>
            </div>
          ))}
          {form.hints.length < 5 && (
            <button type="button" onClick={() => set("hints", [...form.hints, ""])} className="text-sm text-mute underline underline-offset-4 hover:text-ink">
              Ajouter une indication
            </button>
          )}
        </fieldset>
        <div className="grid gap-5 sm:grid-cols-3">
          <Field label="Niveau principal" htmlFor="niveau">
            <select id="niveau" value={form.primary_level} onChange={(event) => set("primary_level", event.target.value)} className={inputClass}>
              <LevelOptions levels={levels} />
            </select>
          </Field>
          <Field label="Difficulté" htmlFor="difficulte">
            <select id="difficulte" value={form.difficulty} onChange={(event) => set("difficulty", Number(event.target.value))} className={inputClass}>
              {DIFFICULTIES.map((value) => (
                <option key={value} value={value}>
                  {value} sur 5
                </option>
              ))}
            </select>
          </Field>
          <Field label="Réponse finale (facultative)" htmlFor="reponse">
            <input id="reponse" value={form.final_answer} onChange={(event) => set("final_answer", event.target.value)} className={inputClass} />
          </Field>
        </div>
        <fieldset>
          <legend className="font-medium text-ink">Aussi pour les niveaux</legend>
          {LEVEL_TRACKS.map(({ track, label }) => (
            <div key={track} className="mt-2">
              <p className="text-xs text-mute">{label}</p>
              <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1">
                {levels
                  .filter((level) => level.track === track)
                  .map((level) => (
                    <label key={level.code} className="flex items-center gap-1.5 text-sm">
                      <input type="checkbox" checked={form.levels.includes(level.code)} onChange={() => toggle("levels", level.code)} />
                      {level.code}
                    </label>
                  ))}
              </div>
            </div>
          ))}
        </fieldset>
        <fieldset>
          <legend className="font-medium text-ink">Chapitres et notions</legend>
          <div className="mt-2 space-y-2">
            {chapters.map((chapter) => (
              <div key={chapter.slug}>
                <label className="flex items-center gap-1.5 text-sm font-medium text-ink">
                  <input type="checkbox" checked={form.topics.includes(chapter.slug)} onChange={() => toggle("topics", chapter.slug)} />
                  {chapter.name}
                </label>
                <div className="ml-6 mt-1 flex flex-wrap gap-x-4 gap-y-1">
                  {topics
                    .filter((topic) => topic.parent === chapter.slug)
                    .map((topic) => (
                      <label key={topic.slug} className="flex items-center gap-1.5 text-sm text-body">
                        <input type="checkbox" checked={form.topics.includes(topic.slug)} onChange={() => toggle("topics", topic.slug)} />
                        {topic.name}
                      </label>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </fieldset>
        <Reason id="motif-exercice" value={reason} onChange={setReason} placeholder="Par exemple : coquille dans la question 2." />
        <button type="submit" disabled={save.pending || !reason.trim()} className={primaryButtonClass}>
          {save.pending ? "Enregistrement…" : "Enregistrer les modifications"}
        </button>
        <FormMessage error={save.error} success={save.success} />
      </form>

      <section aria-labelledby="statut-exercice" className="mt-12 border-t border-hairline pt-6">
        <h2 id="statut-exercice">Statut : {initial.status_label}</h2>
        {initial.status === "published" || initial.status === "removed" ? (
          <div className="mt-3 space-y-3">
            <p className="text-sm text-mute">
              {initial.status === "published"
                ? "Retirer l'exercice annule ses points ; son auteur reçoit le motif et peut faire appel. Un autre membre de l'équipe tranche l'appel."
                : "Rétablir l'exercice le republie et rend ses points à son auteur."}
            </p>
            <Reason id="motif-statut" value={statusReason} onChange={setStatusReason} />
            <div className="flex flex-wrap gap-2">
              {initial.status === "published" ? (
                <>
                  <button type="button" disabled={status.pending || !statusReason.trim()} onClick={() => status.run(() => apiPost(`/panel/exercises/${initial.id}/status`, { action: "remove_plagiarism", reason: statusReason }), "Exercice retiré.")} className={secondaryButtonClass}>
                    Retirer : plagiat
                  </button>
                  <button type="button" disabled={status.pending || !statusReason.trim()} onClick={() => status.run(() => apiPost(`/panel/exercises/${initial.id}/status`, { action: "remove_inappropriate", reason: statusReason }), "Exercice retiré.")} className={secondaryButtonClass}>
                    Retirer : contenu inapproprié
                  </button>
                </>
              ) : (
                <button type="button" disabled={status.pending || !statusReason.trim()} onClick={() => status.run(() => apiPost(`/panel/exercises/${initial.id}/status`, { action: "restore", reason: statusReason }), "Exercice rétabli.")} className={primaryButtonClass}>
                  Rétablir l&apos;exercice
                </button>
              )}
            </div>
            <FormMessage error={status.error} success={status.success} />
          </div>
        ) : (
          <p className="mt-2 text-sm text-mute">Un brouillon ou un exercice fusionné ne change pas de statut ici.</p>
        )}
      </section>
    </>
  );
}

// ---------------------------------------------------------------- comptes

const TRUST_LEVELS = [
  { value: 0, label: "Nouveau" },
  { value: 1, label: "Membre" },
  { value: 2, label: "Relecteur" },
  { value: 3, label: "Expert" },
];

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <details className="rounded-2xl border border-hairline px-4 py-3">
      <summary className="font-medium text-ink">{title}</summary>
      <div className="mt-3 space-y-3">{children}</div>
    </details>
  );
}

/** Ce qu'un administrateur fait sur un compte, depuis sa fiche. */
export function MemberAdmin({
  username,
  trustLevel,
  emailVerified,
  isStaff,
  canMakeAdmin,
}: {
  username: string;
  trustLevel: number;
  emailVerified: boolean;
  isStaff: boolean;
  canMakeAdmin: boolean;
}) {
  const router = useRouter();
  const base = `/panel/members/${encodeURIComponent(username)}`;
  const [amount, setAmount] = useState("");
  const [pointsReason, setPointsReason] = useState("");
  const [level, setLevel] = useState(Math.min(trustLevel, 3));
  const [levelReason, setLevelReason] = useState("");
  const [newName, setNewName] = useState(username);
  const [renameReason, setRenameReason] = useState("");
  const [confirm, setConfirm] = useState("");
  const [deleteReason, setDeleteReason] = useState("");
  const points = useAction();
  const trust = useAction();
  const email = useAction();
  const renaming = useAction();
  const removal = useAction();
  const adminRole = useAction();

  return (
    <div className="space-y-3">
      <Block title="Ajouter ou retirer des points">
        <Field label="Nombre de points (négatif pour en retirer)" htmlFor="points-montant">
          <input id="points-montant" type="number" min={-1000} max={1000} value={amount} onChange={(event) => setAmount(event.target.value)} className={`${inputClass} sm:max-w-40`} />
        </Field>
        <Reason id="points-motif" value={pointsReason} onChange={setPointsReason} />
        <button
          type="button"
          disabled={points.pending || !pointsReason.trim() || !Number(amount)}
          onClick={() => points.run(() => apiPost(`${base}/points`, { amount: Number(amount), reason: pointsReason }), "Points enregistrés.", () => { setAmount(""); setPointsReason(""); router.refresh(); })}
          className={primaryButtonClass}
        >
          Enregistrer
        </button>
        <FormMessage error={points.error} success={points.success} />
      </Block>

      {trustLevel < 4 && (
        <Block title="Changer le niveau de confiance">
          <Field label="Niveau" htmlFor="niveau-confiance" hint="Un niveau baissé peut remonter seul si le membre en remplit de nouveau les conditions.">
            <select id="niveau-confiance" value={level} onChange={(event) => setLevel(Number(event.target.value))} className={`${inputClass} sm:max-w-60`}>
              {TRUST_LEVELS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </Field>
          <Reason id="niveau-motif" value={levelReason} onChange={setLevelReason} />
          <button type="button" disabled={trust.pending || !levelReason.trim() || level === trustLevel} onClick={() => trust.run(() => apiPost(`${base}/trust`, { level, reason: levelReason }), "Niveau changé.")} className={primaryButtonClass}>
            Changer le niveau
          </button>
          <FormMessage error={trust.error} success={trust.success} />
        </Block>
      )}

      {!emailVerified && (
        <Block title="Vérifier l'adresse à la main">
          <p className="text-sm text-mute">Pour un membre dont l&apos;email de confirmation n&apos;arrive pas. Il pourra contribuer aussitôt.</p>
          <button type="button" disabled={email.pending} onClick={() => email.run(() => apiPost(`${base}/verify-email`), "Adresse vérifiée.")} className={primaryButtonClass}>
            Marquer l&apos;adresse comme vérifiée
          </button>
          <FormMessage error={email.error} success={email.success} />
        </Block>
      )}

      <Block title="Changer le pseudo">
        <Field label="Nouveau pseudo" htmlFor="nouveau-pseudo" hint="Lettres, chiffres, points et tirets ; 3 à 30 caractères.">
          <input id="nouveau-pseudo" value={newName} maxLength={30} onChange={(event) => setNewName(event.target.value)} className={`${inputClass} sm:max-w-60`} />
        </Field>
        <Reason id="pseudo-motif" value={renameReason} onChange={setRenameReason} />
        <button
          type="button"
          disabled={renaming.pending || !renameReason.trim() || newName.trim() === username}
          onClick={() => renaming.run(() => apiPost(`${base}/rename`, { username: newName.trim(), reason: renameReason }), "Pseudo changé.", () => router.replace(`/moderation/membres/${encodeURIComponent(newName.trim())}`))}
          className={primaryButtonClass}
        >
          Changer le pseudo
        </button>
        <FormMessage error={renaming.error} success={renaming.success} />
      </Block>

      {canMakeAdmin && (
        <Block title={isStaff ? "Retirer les droits d'administration" : "Nommer administrateur du site"}>
          <p className="text-sm text-mute">
            {isStaff
              ? "Il perd le panneau d'administration et l'accès à l'admin technique."
              : "Il aura le panneau d'administration, la modération, et l'admin technique : choisis quelqu'un de confiance."}
          </p>
          <button type="button" disabled={adminRole.pending} onClick={() => adminRole.run(() => apiPost(`${base}/admin`, { admin: !isStaff }), isStaff ? "Droits retirés." : "Administrateur nommé.")} className={secondaryButtonClass}>
            {isStaff ? "Retirer les droits" : "Nommer administrateur"}
          </button>
          <FormMessage error={adminRole.error} success={adminRole.success} />
        </Block>
      )}

      <Block title="Supprimer le compte">
        <p className="text-sm text-mute">
          Irréversible. Ses données personnelles sont effacées ; ses exercices et messages restent publiés, sans pseudo, comme
          quand un membre supprime lui-même son compte. Pour écarter quelqu&apos;un, un bannissement suffit souvent.
        </p>
        <Field label={`Retape « ${username} » pour confirmer`} htmlFor="confirmer-suppression">
          <input id="confirmer-suppression" value={confirm} onChange={(event) => setConfirm(event.target.value)} className={`${inputClass} sm:max-w-60`} />
        </Field>
        <Reason id="suppression-motif" value={deleteReason} onChange={setDeleteReason} />
        <button
          type="button"
          disabled={removal.pending || confirm.trim() !== username || !deleteReason.trim()}
          onClick={() => removal.run(() => apiPost(`${base}/delete`, { confirm: confirm.trim(), reason: deleteReason }), "Compte supprimé.", () => router.push("/administration?vue=membres"))}
          className="inline-flex min-h-9 items-center justify-center rounded-lg bg-danger px-4 py-1.5 text-[15px] font-semibold text-white hover:brightness-110 disabled:bg-surface-card disabled:text-ash"
        >
          Supprimer définitivement
        </button>
        <FormMessage error={removal.error} success={removal.success} />
      </Block>
    </div>
  );
}
