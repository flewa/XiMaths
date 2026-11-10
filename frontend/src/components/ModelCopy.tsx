"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { ModelCandidate, ModelCopy, MySolution } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { dateFormat } from "@/lib/labels";

import { CopyPhotoList } from "./CopyPhotos";
import { Checkbox, FormMessage, primaryButtonClass, secondaryButtonClass } from "./Form";

/** Ce que dit la case d'accord, à l'envoi d'une copie comme après. */
export const MODEL_CONSENT_LABEL =
  "J'accepte que cette copie, si elle est validée, puisse servir de copie modèle : montrée sans mon pseudo aux membres qui ont envoyé la leur.";

/** La copie modèle d'un exercice, pour qui a envoyé la sienne. On l'ouvre exprès : une
 * copie envoyée ensuite sur cet exercice ne rapporte plus de points. */
export function ModelCopyPanel({ exerciseId, initial }: { exerciseId: number; initial: ModelCopy }) {
  const [state, setState] = useState(initial);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function open() {
    setPending(true);
    setError(null);
    const result = await apiPost<ModelCopy>(`/exercises/${exerciseId}/model-copy/open`);
    setPending(false);
    if (result.ok) setState(result.data);
    else setError(result.error);
  }

  if (state.opened) {
    return (
      <>
        <p className="mt-3 text-sm text-mute">
          Une copie validée, choisie par l&apos;équipe avec l&apos;accord de son auteur. Elle n&apos;est pas un corrigé
          officiel : d&apos;autres rédactions sont justes.
        </p>
        <CopyPhotoList photos={state.photos} />
      </>
    );
  }
  if (!state.can_open) {
    return (
      <p className="mt-3 text-body">
        Une copie modèle existe pour cet exercice. Elle se débloque une fois ta propre copie envoyée.
      </p>
    );
  }
  return (
    <div className="mt-3 space-y-3">
      <p className="text-body">
        L&apos;équipe a choisi une copie validée, avec l&apos;accord de son auteur. Tu peux la lire, sans son nom.
      </p>
      {state.costs_points && (
        <p className="rounded-xl bg-surface-soft px-4 py-3 text-sm text-body">
          Ta copie n&apos;est pas encore validée. Celle que tu as déjà envoyée garde ses points ; mais une fois la copie
          modèle ouverte, une nouvelle copie de ta part sur cet exercice n&apos;en rapportera plus.
        </p>
      )}
      <button type="button" onClick={open} disabled={pending} className={primaryButtonClass}>
        {pending ? "Ouverture…" : "Voir la copie modèle"}
      </button>
      <FormMessage error={error} />
    </div>
  );
}

/** L'accord de l'auteur, modifiable à tout moment sur chacune de ses copies. */
export function ModelConsent({ solution }: { solution: MySolution }) {
  const router = useRouter();
  const [consent, setConsent] = useState(solution.model_consent);
  const [error, setError] = useState<string | null>(null);

  async function onChange(next: boolean) {
    setConsent(next);
    setError(null);
    const result = await apiPost(`/solutions/${solution.id}/model-consent`, { consent: next });
    if (!result.ok) {
      setConsent(!next);
      setError(result.error);
      return;
    }
    router.refresh();
  }

  return (
    <div className="mt-3 text-sm text-body">
      <Checkbox checked={consent} onChange={onChange}>
        {MODEL_CONSENT_LABEL}
      </Checkbox>
      {solution.is_model && (
        <p className="mt-1.5 pl-[1.625rem] text-mute">
          C&apos;est la copie modèle de cet exercice. Décoche la case pour la retirer aussitôt.
        </p>
      )}
      <FormMessage error={error} />
    </div>
  );
}

/** Pour l'équipe : choisir la copie modèle parmi les copies validées dont l'auteur est d'accord. */
export function ModelCandidates({ initial }: { initial: ModelCandidate[] }) {
  const router = useRouter();
  const [candidates, setCandidates] = useState(initial);
  const [error, setError] = useState<string | null>(null);

  async function choose(id: number, chosen: boolean) {
    setError(null);
    const result = await apiPost<ModelCandidate[]>(`/solutions/${id}/model`, { chosen });
    if (!result.ok) return setError(result.error);
    setCandidates(result.data);
    router.refresh();
  }

  return (
    <details className="mt-5 rounded-2xl border border-hairline px-4 py-3">
      <summary className="font-medium">
        Équipe : choisir la copie modèle{" "}
        <span className="font-normal text-mute">
          · {candidates.length} {candidates.length > 1 ? "copies proposées" : "copie proposée"}
        </span>
      </summary>
      <p className="mt-2 text-sm text-mute">
        Copies validées dont l&apos;auteur accepte qu&apos;elles servent de modèle. Une seule par exercice ; vérifie
        qu&apos;aucun nom n&apos;y figure.
      </p>
      <ul className="mt-3 divide-y divide-hairline">
        {candidates.map((candidate) => (
          <li key={candidate.id} className="py-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span className="text-sm text-body">
                {candidate.is_model ? "Copie modèle actuelle" : "Copie validée"}
                {candidate.validated_at && (
                  <span className="text-mute"> · validée le {dateFormat.format(new Date(candidate.validated_at))}</span>
                )}
              </span>
              <button
                type="button"
                onClick={() => choose(candidate.id, !candidate.is_model)}
                className={candidate.is_model ? secondaryButtonClass : primaryButtonClass}
              >
                {candidate.is_model ? "Retirer" : "Choisir comme modèle"}
              </button>
            </div>
            <CopyPhotoList photos={candidate.photos} compact />
          </li>
        ))}
      </ul>
      <FormMessage error={error} />
    </details>
  );
}
