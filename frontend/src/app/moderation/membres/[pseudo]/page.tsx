import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { MathText } from "@/components/MathText";
import { MemberAdmin } from "@/components/AdminActions";
import { LiftSanction, ModeratorToggle, SanctionForm } from "@/components/Moderation";
import { LogList } from "@/components/ModerationLog";
import { Tag } from "@/components/Tag";
import { fetchMe, fetchMemberFile } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Fiche de modération", robots: { index: false } };

type Props = { params: Promise<{ pseudo: string }> };

function day(iso: string | null) {
  return iso ? dateFormat.format(new Date(iso)) : "";
}

const section = "mt-10";

export default async function MemberFilePage({ params }: Props) {
  const username = decodeURIComponent((await params).pseudo);
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchMemberFile(username)]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, file] = data;
  if (!me) redirect(`/connexion?suivant=/moderation/membres/${encodeURIComponent(username)}`);
  // Réservé à l'équipe, et membre inconnu : la page n'existe pas.
  if (!file) notFound();

  const tiles = [
    { value: file.points, label: "points" },
    { value: file.exercises, label: file.exercises > 1 ? "exercices" : "exercice" },
    { value: file.solutions, label: file.solutions > 1 ? "copies" : "copie" },
    { value: file.reviews, label: file.reviews > 1 ? "relectures" : "relecture" },
    { value: file.messages, label: file.messages > 1 ? "messages" : "message" },
  ];

  return (
    <div className="max-w-[760px]">
      <Link href="/moderation" className="text-sm text-mute hover:text-ink">
        ← Modération
      </Link>
      <h1 className="mt-3 break-words">{file.username}</h1>
      <p className="mt-2 flex flex-wrap items-center gap-2 text-sm">
        <Tag strong={file.status !== "active"}>{file.status_label}</Tag>
        <Tag>{file.is_staff ? "Administrateur" : file.trust_label}</Tag>
        {!file.email_verified && <Tag>Adresse non vérifiée</Tag>}
        <span className="text-mute">inscrit le {day(file.joined_at)}</span>
        <Link href={`/membres/${encodeURIComponent(file.username)}`} className="text-mute underline underline-offset-4 hover:text-ink">
          Profil public
        </Link>
      </p>

      <dl className="mt-6 grid grid-cols-3 gap-2 sm:grid-cols-5">
        {tiles.map((tile) => (
          <div key={tile.label} className="flex flex-col-reverse rounded-xl bg-surface-soft px-3 py-2">
            <dt className="text-[13px] text-mute">{tile.label}</dt>
            <dd className="font-serif text-xl leading-tight text-ink-deep tabular-nums">{tile.value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-3 text-sm text-mute">
        Signalements déposés : {file.reports_made}
        {file.reports_made > 0 && ` (${file.reports_confirmed} confirmés, ${file.reports_rejected} non retenus)`}.
      </p>

      <section aria-labelledby="sanctions" className={section}>
        <h2 id="sanctions">Sanctions</h2>
        {file.sanctions.length === 0 ? (
          <p className="mt-2 text-body">Aucune sanction.</p>
        ) : (
          <ul className="mt-3 divide-y divide-hairline border-y border-hairline">
            {file.sanctions.map((sanction) => (
              <li key={sanction.id} className="py-3 text-sm">
                <p className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-ink">{sanction.label}</span>
                  {sanction.active && <Tag strong>En cours{sanction.ends_at ? ` jusqu'au ${day(sanction.ends_at)}` : ""}</Tag>}
                  {sanction.appeal && <Tag>{sanction.appeal}</Tag>}
                  <span className="text-mute">
                    le {day(sanction.created_at)}
                    {sanction.decided_by ? `, par ${sanction.decided_by}` : ""}
                  </span>
                </p>
                <p className="mt-1 whitespace-pre-line text-body">{sanction.reason}</p>
                {sanction.lifted_reason && <p className="mt-1 text-mute">Levée : {sanction.lifted_reason}</p>}
                {sanction.active && file.can_sanction && (
                  <div className="mt-2">
                    <LiftSanction id={sanction.id} />
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
        {file.can_sanction ? (
          <details className="mt-4 rounded-2xl border border-hairline px-4 py-3">
            <summary className="font-medium">Prononcer une sanction</summary>
            <p className="mt-2 text-sm text-mute">
              Le membre reçoit le motif et peut faire appel sous 14 jours ; un autre membre de l&apos;équipe tranche
              l&apos;appel. Une suspension ou un bannissement l&apos;empêche d&apos;écrire sur le site.
            </p>
            <div className="mt-3">
              <SanctionForm username={file.username} />
            </div>
          </details>
        ) : (
          <p className="mt-4 text-sm text-mute">
            {file.username === me.username
              ? "C'est ta fiche : tu ne te sanctionnes pas toi-même."
              : "Ce compte fait partie de l'équipe : seul un administrateur peut le sanctionner."}
          </p>
        )}
      </section>

      <section aria-labelledby="retraits" className={section}>
        <h2 id="retraits">Contenus retirés</h2>
        {file.removals.length === 0 ? (
          <p className="mt-2 text-body">Aucun contenu retiré.</p>
        ) : (
          <ul className="mt-3 divide-y divide-hairline border-y border-hairline">
            {file.removals.map((removal) => (
              <li key={`${removal.what}-${removal.decided_at}`} className="py-3 text-sm">
                <p className="flex flex-wrap items-center gap-2">
                  {removal.url ? (
                    <Link href={removal.url} className="font-medium text-ink hover:underline">
                      <MathText>{removal.what}</MathText>
                    </Link>
                  ) : (
                    <span className="font-medium text-ink">{removal.what}</span>
                  )}
                  {removal.appeal && <Tag>{removal.appeal}</Tag>}
                  <span className="text-mute">
                    le {day(removal.decided_at)}
                    {removal.decided_by ? `, par ${removal.decided_by}` : ""}
                  </span>
                </p>
                {removal.reason && <p className="mt-1 whitespace-pre-line text-body">{removal.reason}</p>}
              </li>
            ))}
          </ul>
        )}
      </section>

      {file.recent_messages.length > 0 && (
        <section aria-labelledby="messages" className={section}>
          <h2 id="messages">Derniers messages</h2>
          <ul className="mt-3 divide-y divide-hairline border-y border-hairline">
            {file.recent_messages.map((message) => (
              <li key={message.id} className="py-3 text-sm">
                <p className="text-mute">
                  Sous{" "}
                  <Link href={`/exercices/${message.exercise_id}#discussion`} className="text-ink hover:underline">
                    <MathText>{message.exercise_title}</MathText>
                  </Link>{" "}
                  · {day(message.created_at)}
                  {message.removed && " · retiré"}
                </p>
                <div className={`[overflow-wrap:anywhere] ${message.removed ? "text-mute" : "text-body"}`}>
                  <MathMarkdown>{message.body}</MathMarkdown>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {file.can_administer && (
        <section aria-labelledby="administration" className={section}>
          <h2 id="administration">Administration du compte</h2>
          <p className="mt-2 text-sm text-mute">Chaque action demande un motif, prévient le membre et s&apos;inscrit au journal.</p>
          <div className="mt-3">
            <MemberAdmin
              username={file.username}
              trustLevel={file.trust_level}
              emailVerified={file.email_verified}
              isStaff={file.is_staff}
              canMakeAdmin={file.can_make_admin}
            />
          </div>
        </section>
      )}

      {file.can_appoint && (
        <section aria-labelledby="equipe" className={section}>
          <h2 id="equipe">Équipe de modération</h2>
          <p className="mt-2 text-sm text-mute">
            {file.is_moderator
              ? "Ce membre modère : il traite les signalements, les messages signalés et les appels."
              : "Un modérateur traite les signalements, les messages signalés et les appels. Choisis quelqu'un de fiable, dont les relectures et les signalements sont justes."}
          </p>
          <div className="mt-3">
            <ModeratorToggle username={file.username} moderator={file.is_moderator} />
          </div>
        </section>
      )}

      <section aria-labelledby="journal" className={section}>
        <h2 id="journal">Journal</h2>
        {file.log.length === 0 ? (
          <p className="mt-2 text-body">Aucune décision de l&apos;équipe sur ce membre.</p>
        ) : (
          <div className="mt-3">
            <LogList entries={file.log} />
          </div>
        )}
      </section>
    </div>
  );
}
