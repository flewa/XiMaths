"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { Claim, DiscussionMessage, SanctionKind } from "@/lib/api";
import { apiDelete, apiPost } from "@/lib/client-api";

import { FormMessage, inputClass, primaryButtonClass, secondaryButtonClass } from "./Form";

/** Motifs fréquents d'un retrait de message : un clic les écrit, on peut les compléter. */
const MESSAGE_REASONS = [
  "Le message donne la solution : elle s'envoie en copie, pas dans le fil.",
  "Hors sujet : le fil sert aux questions et remarques sur cet exercice.",
  "Propos irrespectueux envers un autre membre.",
  "Publicité ou lien sans rapport avec l'exercice.",
  "Le message contient des données personnelles.",
];

export const SANCTIONS: { value: SanctionKind; label: string }[] = [
  { value: "avertissement", label: "Avertissement" },
  { value: "exclusion_classements", label: "Exclusion des classements (30 jours)" },
  { value: "suspension", label: "Suspension (7 jours)" },
  { value: "bannissement", label: "Bannissement" },
];

const presetClass =
  "rounded-full bg-surface-card px-3 py-1 text-left text-sm text-body hover:bg-surface-dark-elevated hover:text-ink";

function useAction() {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function run<T>(path: string, body: unknown, onDone?: (data: T) => void) {
    setPending(true);
    setError(null);
    const result = await apiPost<T>(path, body);
    setPending(false);
    if (!result.ok) return setError(result.error);
    if (onDone) onDone(result.data);
    else router.refresh();
  }
  return { pending, error, run };
}

function ReasonField({
  id,
  label,
  value,
  onChange,
  presets,
  rows = 3,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  presets?: string[];
  rows?: number;
}) {
  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-sm font-medium text-ink">
        {label}
      </label>
      {presets && (
        <div className="flex flex-wrap gap-1.5">
          {presets.map((preset) => (
            <button key={preset} type="button" onClick={() => onChange(preset)} className={presetClass}>
              {preset}
            </button>
          ))}
        </div>
      )}
      <textarea id={id} value={value} onChange={(event) => onChange(event.target.value)} rows={rows} className={inputClass} />
    </div>
  );
}

/** « Je m'en occupe » : montre aux collègues qu'un dossier est ouvert, pour ne pas le traiter
 * à deux. Simple indication, deux heures au plus : tout le monde peut encore trancher. */
export function ClaimControl({ claimKey, claim, since }: { claimKey: string; claim: Claim | null; since: string }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function act(call: () => Promise<{ ok: boolean; error?: string }>) {
    setPending(true);
    setError(null);
    const result = await call();
    setPending(false);
    if (!result.ok) return setError(result.error ?? "Action impossible.");
    router.refresh();
  }
  const take = (takeOver: boolean) => act(() => apiPost("/moderation/claims", { key: claimKey, take_over: takeOver }));
  const small = "inline-flex min-h-8 items-center rounded-lg px-3 text-sm font-medium";
  return (
    <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
      {!claim ? (
        <button type="button" disabled={pending} onClick={() => take(false)} className={`${small} bg-surface-card text-ink hover:bg-surface-dark-elevated`}>
          Je m&apos;en occupe
        </button>
      ) : claim.mine ? (
        <>
          <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-accent-text">Tu t&apos;en occupes</span>
          <button
            type="button"
            disabled={pending}
            onClick={() => act(() => apiDelete(`/moderation/claims/${encodeURIComponent(claimKey)}`))}
            className={`${small} text-mute hover:bg-hover hover:text-ink`}
          >
            Rendre le dossier
          </button>
        </>
      ) : (
        <>
          <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-accent-text">
            {claim.username} s&apos;en occupe {since}
          </span>
          <button type="button" disabled={pending} onClick={() => take(true)} className={`${small} text-mute hover:bg-hover hover:text-ink`}>
            Prendre le relais
          </button>
        </>
      )}
      <FormMessage error={error} />
    </div>
  );
}

/** Trancher un signalement : confirmer (motif obligatoire, sanction possible) ou ne pas retenir. */
export function ReportDecision({ id, hasAuthor }: { id: number; hasAuthor: boolean }) {
  const { pending, error, run } = useAction();
  const [note, setNote] = useState("");
  const [sanction, setSanction] = useState<SanctionKind | "">("");
  const path = `/moderation/reports/${id}/decide`;
  return (
    <div className="mt-4 space-y-3 border-t border-hairline pt-4">
      <ReasonField
        id={`motif-${id}`}
        label="Motif, envoyé à l'auteur du contenu s'il est confirmé"
        value={note}
        onChange={setNote}
      />
      {hasAuthor && (
        <div>
          <label htmlFor={`sanction-${id}`} className="block text-sm font-medium text-ink">
            Sanctionner aussi l&apos;auteur ?
          </label>
          <select
            id={`sanction-${id}`}
            value={sanction}
            onChange={(event) => setSanction(event.target.value as SanctionKind | "")}
            className={`${inputClass} mt-1.5 sm:max-w-sm`}
          >
            <option value="">Non, retirer le contenu suffit</option>
            {SANCTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={pending || !note.trim()}
          onClick={() => run(path, { confirmed: true, note, sanction: sanction || null })}
          className={primaryButtonClass}
        >
          Confirmer
        </button>
        <button
          type="button"
          disabled={pending}
          onClick={() => run(path, { confirmed: false, note })}
          className={secondaryButtonClass}
        >
          Ne pas retenir
        </button>
      </div>
      <FormMessage error={error} />
    </div>
  );
}

/** Message signalé : le garder, ou le retirer avec un motif que son auteur recevra. */
export function MessageDecision({ id }: { id: number }) {
  const { pending, error, run } = useAction();
  const [removing, setRemoving] = useState(false);
  const [reason, setReason] = useState("");
  const path = `/moderation/messages/${id}/decide`;
  return (
    <div className="mt-4 space-y-3 border-t border-hairline pt-4">
      {removing && (
        <ReasonField
          id={`retrait-${id}`}
          label="Motif du retrait, envoyé à l'auteur du message"
          value={reason}
          onChange={setReason}
          presets={MESSAGE_REASONS}
          rows={2}
        />
      )}
      <div className="flex flex-wrap gap-2">
        {removing ? (
          <>
            <button
              type="button"
              disabled={pending || !reason.trim()}
              onClick={() => run(path, { remove: true, reason })}
              className={primaryButtonClass}
            >
              Retirer le message
            </button>
            <button type="button" onClick={() => setRemoving(false)} className={secondaryButtonClass}>
              Annuler
            </button>
          </>
        ) : (
          <>
            <button type="button" disabled={pending} onClick={() => run(path, { remove: false })} className={secondaryButtonClass}>
              Garder le message
            </button>
            <button type="button" onClick={() => setRemoving(true)} className={secondaryButtonClass}>
              Retirer…
            </button>
          </>
        )}
      </div>
      <FormMessage error={error} />
    </div>
  );
}

/** Trancher un appel, avec un motif que le membre recevra. */
export function AppealDecision({ id }: { id: number }) {
  const { pending, error, run } = useAction();
  const [note, setNote] = useState("");
  const path = `/moderation/appeals/${id}/decide`;
  return (
    <div className="mt-4 space-y-3 border-t border-hairline pt-4">
      <ReasonField id={`appel-${id}`} label="Réponse, envoyée au membre" value={note} onChange={setNote} />
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={pending || !note.trim()}
          onClick={() => run(path, { overturn: true, note })}
          className={primaryButtonClass}
        >
          Annuler la décision
        </button>
        <button
          type="button"
          disabled={pending || !note.trim()}
          onClick={() => run(path, { overturn: false, note })}
          className={secondaryButtonClass}
        >
          Maintenir la décision
        </button>
      </div>
      <FormMessage error={error} />
    </div>
  );
}

/** Sanctionner un membre depuis sa fiche. */
export function SanctionForm({ username }: { username: string }) {
  const { pending, error, run } = useAction();
  const [kind, setKind] = useState<SanctionKind>("avertissement");
  const [reason, setReason] = useState("");
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        run(`/moderation/members/${encodeURIComponent(username)}/sanctions`, { kind, reason });
        setReason("");
      }}
      className="space-y-3"
    >
      <div>
        <label htmlFor="sanction-kind" className="block text-sm font-medium text-ink">
          Sanction
        </label>
        <select
          id="sanction-kind"
          value={kind}
          onChange={(event) => setKind(event.target.value as SanctionKind)}
          className={`${inputClass} mt-1.5 sm:max-w-sm`}
        >
          {SANCTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      <ReasonField
        id="sanction-motif"
        label="Motif, envoyé au membre : ce qui s'est passé, et les contenus concernés"
        value={reason}
        onChange={setReason}
      />
      <button type="submit" disabled={pending || !reason.trim()} className={primaryButtonClass}>
        Sanctionner
      </button>
      <FormMessage error={error} />
    </form>
  );
}

/** Lever une sanction en cours, avec une raison que le membre recevra. */
export function LiftSanction({ id }: { id: number }) {
  const { pending, error, run } = useAction();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)} className="text-sm text-mute underline-offset-4 hover:text-ink hover:underline">
        Lever la sanction
      </button>
    );
  }
  return (
    <div className="mt-2 space-y-2">
      <label htmlFor={`levee-${id}`} className="block text-sm font-medium text-ink">
        Raison de la levée, envoyée au membre
      </label>
      <input
        id={`levee-${id}`}
        value={reason}
        maxLength={200}
        onChange={(event) => setReason(event.target.value)}
        className={inputClass}
      />
      <div className="flex gap-2">
        <button
          type="button"
          disabled={pending || !reason.trim()}
          onClick={() => run(`/moderation/sanctions/${id}/lift`, { reason })}
          className={primaryButtonClass}
        >
          Lever
        </button>
        <button type="button" onClick={() => setOpen(false)} className={secondaryButtonClass}>
          Annuler
        </button>
      </div>
      <FormMessage error={error} />
    </div>
  );
}

/** Depuis le fil d'un exercice : l'équipe retire le message d'un autre, avec un motif. */
export function ModerateMessage({
  id,
  onThread,
  onCancel,
}: {
  id: number;
  onThread: (thread: DiscussionMessage[]) => void;
  onCancel: () => void;
}) {
  const { pending, error, run } = useAction();
  const [reason, setReason] = useState("");
  return (
    <div className="mt-2 space-y-2 rounded-xl border border-hairline p-3">
      <ReasonField
        id={`moderer-${id}`}
        label="Motif du retrait, envoyé à l'auteur, qui peut faire appel"
        value={reason}
        onChange={setReason}
        presets={MESSAGE_REASONS}
        rows={2}
      />
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={pending || !reason.trim()}
          onClick={() => run<DiscussionMessage[]>(`/messages/${id}/moderate`, { reason }, onThread)}
          className={primaryButtonClass}
        >
          Retirer le message
        </button>
        <button type="button" onClick={onCancel} className={secondaryButtonClass}>
          Annuler
        </button>
      </div>
      <FormMessage error={error} />
    </div>
  );
}
