"use client";

import Link from "next/link";
import { useState } from "react";

import type { DiscussionMessage, DiscussionReply } from "@/lib/api";
import { apiDelete, apiPost } from "@/lib/client-api";
import { dateFormat } from "@/lib/labels";

import { Avatar } from "./Avatar";
import { FormMessage, inputClass, primaryButtonClass } from "./Form";
import { MathMarkdown } from "./MathMarkdown";

const MAX_LENGTH = 2000;
const action = "text-sm text-mute underline-offset-4 hover:text-ink hover:underline disabled:opacity-60";
const tag = "rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent-text";

/** Qui regarde : null pour un visiteur ; `verified` dit si le membre peut écrire. */
type Viewer = { verified: boolean } | null;

function Composer({
  exerciseId,
  parent,
  onPosted,
  onCancel,
}: {
  exerciseId: number;
  parent?: number;
  onPosted: (thread: DiscussionMessage[]) => void;
  onCancel?: () => void;
}) {
  const [body, setBody] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const field = parent ? `reponse-${parent}` : "nouveau-message";

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!body.trim()) return;
    setPending(true);
    setError(null);
    const result = await apiPost<DiscussionMessage[]>(`/exercises/${exerciseId}/messages`, { body, parent });
    setPending(false);
    if (!result.ok) {
      setError(result.status === 422 && typeof (result.body as { detail?: unknown })?.detail !== "string" ? "Ton message est vide, ou trop long." : result.error);
      return;
    }
    setBody("");
    onPosted(result.data);
  }

  return (
    <form onSubmit={onSubmit} className="space-y-2">
      <label htmlFor={field} className="sr-only">
        {parent ? "Ta réponse" : "Ta question ou ta remarque"}
      </label>
      <textarea
        id={field}
        value={body}
        onChange={(event) => setBody(event.target.value)}
        rows={parent ? 2 : 3}
        maxLength={MAX_LENGTH}
        placeholder={parent ? "Ta réponse…" : "Une précision sur l'énoncé, une coquille, une idée de méthode…"}
        className={inputClass}
      />
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <button type="submit" disabled={pending || !body.trim()} className={primaryButtonClass}>
          {pending ? "Envoi…" : parent ? "Répondre" : "Publier"}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className={action}>
            Annuler
          </button>
        )}
        <span className="text-sm text-mute">Les formules s&apos;écrivent en LaTeX, entre $…$.</span>
      </div>
      <FormMessage error={error} />
    </form>
  );
}

function Entry({
  message,
  viewer,
  onReply,
  onThread,
}: {
  message: DiscussionReply;
  viewer: Viewer;
  onReply?: () => void;
  onThread: (thread: DiscussionMessage[]) => void;
}) {
  const [confirming, setConfirming] = useState(false);
  const [flagged, setFlagged] = useState(message.flagged);
  const [error, setError] = useState<string | null>(null);

  async function remove() {
    const result = await apiDelete<DiscussionMessage[]>(`/messages/${message.id}`);
    if (result.ok) onThread(result.data);
    else setError(result.error);
  }

  async function flag() {
    const result = await apiPost(`/messages/${message.id}/flag`);
    if (result.ok) setFlagged(true);
    else setError(result.error);
  }

  if (message.removed) {
    return <p className="text-sm italic text-mute">Message retiré.</p>;
  }
  return (
    <div className="flex gap-3">
      <span className="mt-0.5 shrink-0">
        {message.author ? (
          <Avatar avatar={message.author.avatar} size={28} />
        ) : (
          <span className="block size-7 rounded-lg bg-surface-card" />
        )}
      </span>
      <div className="min-w-0 flex-1">
        <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
          {message.author ? (
            <Link href={`/membres/${encodeURIComponent(message.author.username)}`} className="font-medium text-ink hover:underline">
              {message.author.username}
            </Link>
          ) : (
            <span className="text-mute">Compte supprimé</span>
          )}
          {message.exercise_author && <span className={tag}>Auteur de l&apos;exercice</span>}
          {message.team && !message.exercise_author && <span className={tag}>Équipe</span>}
          <span className="text-mute">{dateFormat.format(new Date(message.created_at))}</span>
        </p>
        <div className="-my-2 text-body [overflow-wrap:anywhere]">
          <MathMarkdown>{message.body}</MathMarkdown>
        </div>
        {viewer && (
          <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1">
            {onReply && viewer.verified && (
              <button type="button" onClick={onReply} className={action}>
                Répondre
              </button>
            )}
            {!message.mine &&
              viewer.verified &&
              (flagged ? (
                <span className="text-sm text-mute">Signalé à l&apos;équipe</span>
              ) : (
                <button type="button" onClick={flag} className={action}>
                  Signaler
                </button>
              ))}
            {message.can_remove &&
              (confirming ? (
                <>
                  <button type="button" onClick={remove} className={`${action} text-ink`}>
                    Confirmer le retrait
                  </button>
                  <button type="button" onClick={() => setConfirming(false)} className={action}>
                    Annuler
                  </button>
                </>
              ) : (
                <button type="button" onClick={() => setConfirming(true)} className={action}>
                  Retirer
                </button>
              ))}
          </p>
        )}
        <FormMessage error={error} />
      </div>
    </div>
  );
}

/** Le fil de questions et de remarques d'un exercice. Lisible par tous ; on écrit connecté. */
export function Discussion({
  exerciseId,
  initial,
  viewer,
}: {
  exerciseId: number;
  initial: DiscussionMessage[];
  viewer: Viewer;
}) {
  const [messages, setMessages] = useState(initial);
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const count = messages.reduce((total, message) => total + (message.removed ? 0 : 1) + message.replies.length, 0);

  function onThread(thread: DiscussionMessage[]) {
    setMessages(thread);
    setReplyingTo(null);
  }

  return (
    <>
      <h2 id="discussion-titre" className="flex items-baseline gap-2">
        Questions et remarques
        {count > 0 && <span className="font-sans text-base text-mute tabular-nums">{count}</span>}
      </h2>
      <p className="mt-2 text-sm text-mute">
        Pour demander une précision, signaler une coquille ou discuter d&apos;une méthode. Pas de solution ici :
        elle s&apos;envoie en copie, plus haut.
      </p>

      {messages.length > 0 && (
        <ul className="mt-5 divide-y divide-hairline border-y border-hairline">
          {messages.map((message) => (
            <li key={message.id} className="py-4">
              <Entry
                message={message}
                viewer={viewer}
                onReply={() => setReplyingTo(replyingTo === message.id ? null : message.id)}
                onThread={onThread}
              />
              {(message.replies.length > 0 || replyingTo === message.id) && (
                <div className="ml-3.5 mt-3 space-y-4 border-l border-hairline pl-5 sm:ml-10">
                  {message.replies.map((reply) => (
                    <Entry key={reply.id} message={reply} viewer={viewer} onThread={onThread} />
                  ))}
                  {replyingTo === message.id && (
                    <Composer
                      exerciseId={exerciseId}
                      parent={message.id}
                      onPosted={onThread}
                      onCancel={() => setReplyingTo(null)}
                    />
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      <div className="mt-5">
        {!viewer ? (
          <p className="text-body">
            <Link href={`/connexion?suivant=/exercices/${exerciseId}%23discussion`} className="underline underline-offset-4">
              Connecte-toi
            </Link>{" "}
            pour poser une question ou répondre.
          </p>
        ) : !viewer.verified ? (
          <p className="text-body">Confirme ton adresse email pour écrire ici.</p>
        ) : (
          <Composer exerciseId={exerciseId} onPosted={onThread} />
        )}
      </div>
    </>
  );
}
