import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { CopyPhotoList } from "@/components/CopyPhotos";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { MathText } from "@/components/MathText";
import { AppealDecision, ClaimControl, MessageDecision, ReportDecision } from "@/components/Moderation";
import { LogList } from "@/components/ModerationLog";
import { Tag } from "@/components/Tag";
import { TeamHeader, type TeamTab } from "@/components/TeamNav";
import {
  type AppealItem,
  type Claim,
  type FlaggedMessage,
  type LogEntry,
  type MemberBrief,
  type ReportGroup,
  fetchAppealQueue,
  fetchFlaggedMessages,
  fetchMe,
  fetchModerationLog,
  fetchModerationSummary,
  fetchReportQueue,
} from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Modération", robots: { index: false } };

/** « depuis 25 min » : calculé au rendu de la page, qui se recharge à chaque décision. */
function claimSince(claim: Claim | null, now: Date) {
  if (!claim) return "";
  const minutes = Math.max(0, Math.round((now.getTime() - new Date(claim.since).getTime()) / 60_000));
  if (minutes < 1) return "à l'instant";
  return minutes < 60 ? `depuis ${minutes} min` : `depuis ${Math.floor(minutes / 60)} h`;
}

const FILES = [
  { value: "signalements", label: "Signalements" },
  { value: "messages", label: "Messages" },
  { value: "appels", label: "Appels" },
  { value: "journal", label: "Journal" },
] as const;
type File = (typeof FILES)[number]["value"];

const card = "rounded-2xl border border-hairline p-4 sm:p-5";

function day(iso: string | null) {
  return iso ? dateFormat.format(new Date(iso)) : "";
}

/** Le membre concerné, avec ce qui aide à juger : statut, sanction en cours, antécédents. */
function MemberLine({ member, label }: { member: MemberBrief | null; label: string }) {
  if (!member) return <p className="text-sm text-mute">{label} : compte supprimé</p>;
  return (
    <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
      <span className="text-mute">{label} :</span>
      <Link href={`/moderation/membres/${encodeURIComponent(member.username)}`} className="font-medium text-ink hover:underline">
        {member.username}
      </Link>
      {member.status !== "active" && <Tag strong>{member.status_label}</Tag>}
      {member.active_sanction && <Tag strong>{member.active_sanction}</Tag>}
      <span className="text-mute">
        {member.past_decisions === 0
          ? "aucune décision passée"
          : `${member.past_decisions} décision${member.past_decisions > 1 ? "s" : ""} passée${member.past_decisions > 1 ? "s" : ""}`}
      </span>
    </p>
  );
}

function NotYours({ children }: { children: React.ReactNode }) {
  return <p className="mt-4 border-t border-hairline pt-4 text-sm text-mute">{children}</p>;
}

type Elsewhere = { href: string; label: string; count: number };

/** File vide : ce qui attend ailleurs, pour que la page ne soit pas un cul-de-sac. */
function Empty({ children, elsewhere = [] }: { children: React.ReactNode; elsewhere?: Elsewhere[] }) {
  const waiting = elsewhere.filter((item) => item.count > 0);
  return (
    <div className="mt-6 rounded-2xl bg-surface-soft px-5 py-4 text-body">
      <p>{children}</p>
      {waiting.length > 0 ? (
        <ul className="mt-3 space-y-1.5">
          {waiting.map((item) => (
            <li key={item.href}>
              <Link href={item.href} className="inline-flex min-h-8 items-center gap-1 text-accent-text hover:underline">
                {item.label} : {item.count} →
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-mute">
          Rien n&apos;attend ailleurs non plus.{" "}
          <Link href="/relectures" className="underline underline-offset-4 hover:text-ink">
            Les copies en attente de correction
          </Link>{" "}
          sont dans Relectures.
        </p>
      )}
    </div>
  );
}

function ReportCard({ group, now }: { group: ReportGroup; now: Date }) {
  return (
    <li className={card}>
      <p className="flex flex-wrap items-center gap-2 text-sm">
        <Tag strong>{group.reason_label}</Tag>
        <span className="text-mute">
          {group.target === "exercise" ? "sur un exercice" : "sur une copie"} · signalé le {day(group.created_at)}
        </span>
      </p>
      <p className="mt-2 font-medium">
        <Link href={`/exercices/${group.exercise_id}`} className="text-ink hover:underline">
          <MathText>{group.exercise_title}</MathText>
        </Link>
      </p>
      <details className="mt-2">
        <summary className="text-sm text-mute">{group.target === "exercise" ? "Voir l'énoncé" : "Voir l'énoncé et la copie"}</summary>
        <div className="mt-2 rounded-xl bg-surface-soft px-4 py-1">
          <MathMarkdown>{group.statement}</MathMarkdown>
        </div>
        {group.photos.length > 0 && <CopyPhotoList photos={group.photos} compact />}
        {group.solution_status && <p className="text-sm text-mute">Statut de la copie : {group.solution_status}</p>}
      </details>
      <div className="mt-3 space-y-1.5">
        <MemberLine member={group.author} label="Auteur" />
        <ul className="space-y-1 text-sm">
          {group.reports.map((report) => (
            <li key={`${report.username}-${report.created_at}`} className="text-body">
              <span className="text-mute">Signalé par </span>
              <Link href={`/moderation/membres/${encodeURIComponent(report.username)}`} className="text-ink hover:underline">
                {report.username}
              </Link>
              {report.details && <span className="whitespace-pre-line"> : « {report.details} »</span>}
            </li>
          ))}
        </ul>
        {group.effect && <p className="text-sm text-mute">{group.effect}</p>}
      </div>
      {group.can_decide && <ClaimControl claimKey={`report:${group.id}`} claim={group.claim} since={claimSince(group.claim, now)} />}
      {group.can_decide ? (
        <ReportDecision id={group.id} hasAuthor={Boolean(group.author)} />
      ) : (
        <NotYours>Ce contenu est le tien : un autre membre de l&apos;équipe tranche.</NotYours>
      )}
    </li>
  );
}

function MessageCard({ message, now }: { message: FlaggedMessage; now: Date }) {
  return (
    <li className={card}>
      <p className="text-sm text-mute">
        Sous{" "}
        <Link href={`/exercices/${message.exercise_id}#discussion`} className="text-ink hover:underline">
          <MathText>{message.exercise_title}</MathText>
        </Link>{" "}
        · écrit le {day(message.created_at)}
      </p>
      {message.in_reply_to && (
        <p className="mt-2 border-l-2 border-hairline pl-3 text-sm text-mute">En réponse à : {message.in_reply_to}</p>
      )}
      <div className="mt-2 rounded-xl bg-surface-soft px-4 py-1 [overflow-wrap:anywhere]">
        <MathMarkdown>{message.body}</MathMarkdown>
      </div>
      <div className="mt-3 space-y-1.5">
        <MemberLine member={message.author} label="Auteur" />
        <p className="text-sm text-body">
          <span className="text-mute">Signalé par </span>
          {message.flags.map((flag, index) => (
            <span key={flag.username}>
              {index > 0 && ", "}
              <Link href={`/moderation/membres/${encodeURIComponent(flag.username)}`} className="text-ink hover:underline">
                {flag.username}
              </Link>
            </span>
          ))}
        </p>
        {message.kept_before && <p className="text-sm text-mute">Déjà examiné et gardé une fois, puis signalé à nouveau.</p>}
      </div>
      {message.can_decide && (
        <ClaimControl claimKey={`message:${message.id}`} claim={message.claim} since={claimSince(message.claim, now)} />
      )}
      {message.can_decide ? (
        <MessageDecision id={message.id} />
      ) : (
        <NotYours>C&apos;est ton message : un autre membre de l&apos;équipe l&apos;examine.</NotYours>
      )}
    </li>
  );
}

function AppealCard({ appeal, now }: { appeal: AppealItem; now: Date }) {
  return (
    <li className={card}>
      <p className="flex flex-wrap items-center gap-2 text-sm">
        {appeal.overdue ? <Tag strong>En retard</Tag> : <Tag>À répondre</Tag>}
        <span className="text-mute">
          appel du {day(appeal.created_at)} · réponse due le {day(appeal.due_at)}
        </span>
      </p>
      <p className="mt-2 font-medium text-ink">
        {appeal.url ? (
          <Link href={appeal.url} className="hover:underline">
            <MathText>{appeal.decision_title}</MathText>
          </Link>
        ) : (
          <MathText>{appeal.decision_title}</MathText>
        )}
      </p>
      <div className="mt-2 space-y-1.5 text-sm">
        <MemberLine member={appeal.member} label="Membre" />
        <p className="text-body">
          <span className="text-mute">
            Décision du {day(appeal.decided_at)}
            {appeal.decided_by ? `, par ${appeal.decided_by}` : ""} :{" "}
          </span>
          <span className="whitespace-pre-line">{appeal.decision_reason || "sans motif écrit"}</span>
        </p>
      </div>
      <blockquote className="mt-3 whitespace-pre-line rounded-xl bg-surface-soft px-4 py-3 text-body">
        {appeal.statement}
      </blockquote>
      {appeal.can_decide && <ClaimControl claimKey={`appeal:${appeal.id}`} claim={appeal.claim} since={claimSince(appeal.claim, now)} />}
      {appeal.can_decide ? (
        <AppealDecision id={appeal.id} />
      ) : (
        <NotYours>Tu as pris la décision contestée : un autre membre de l&apos;équipe tranche l&apos;appel.</NotYours>
      )}
    </li>
  );
}

export default async function ModerationPage({ searchParams }: { searchParams: Promise<{ file?: string }> }) {
  const requested = (await searchParams).file;
  const file: File = FILES.some((item) => item.value === requested) ? (requested as File) : "signalements";
  const loaders = {
    signalements: fetchReportQueue,
    messages: fetchFlaggedMessages,
    appels: fetchAppealQueue,
    journal: fetchModerationLog,
  };
  let data;
  try {
    const [me, summary, items] = await Promise.all([fetchMe(), fetchModerationSummary(), loaders[file]()]);
    data = { me, summary, items: items ?? [] };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { me, summary, items } = data;
  if (!me) redirect("/connexion?suivant=/moderation");
  // Réservé à l'équipe : pour les autres, la page n'existe pas.
  if (!summary) notFound();
  const now = new Date();
  const queues: Record<"signalements" | "messages" | "appels", Elsewhere> = {
    signalements: { href: "/moderation?file=signalements", label: "Signalements à trancher", count: summary.reports },
    messages: { href: "/moderation?file=messages", label: "Messages signalés", count: summary.messages },
    appels: { href: "/moderation?file=appels", label: "Appels à trancher", count: summary.appeals },
  };
  const others = (current: keyof typeof queues) =>
    (Object.keys(queues) as (keyof typeof queues)[]).filter((key) => key !== current).map((key) => queues[key]);

  return (
    // Large comme l'administration, pour que les onglets communs tiennent sur une ligne ; les
    // dossiers gardent une largeur de lecture.
    <div className="page-wide">
      <TeamHeader
        staff={me.is_staff}
        counts={{ reports: summary.reports, messages: summary.messages, appeals: summary.appeals }}
        active={file as TeamTab}
      />
      <div className="max-w-[760px]">
      {summary.appeals_overdue > 0 && (
        <p className="mt-4 rounded-xl bg-accent-soft px-4 py-3 text-accent-text">
          {summary.appeals_overdue > 1
            ? `${summary.appeals_overdue} appels attendent depuis plus de 7 jours`
            : "Un appel attend depuis plus de 7 jours"}
          , le délai promis aux membres.
        </p>
      )}

      {file === "signalements" && (
        <>
          {summary.duplicates > 0 && (
            <p className="mt-4 text-sm text-mute">
              {summary.duplicates > 1 ? `${summary.duplicates} signalements de doublon attendent` : "Un signalement de doublon attend"}{" "}
              dans la file des doublons
              {me.is_staff ? (
                <>
                  , dans{" "}
                  <a href="/admin/duplicates/duplicatepair/" className="underline underline-offset-4 hover:text-ink">
                    l&apos;administration
                  </a>
                  .
                </>
              ) : (
                ", que traitent les administrateurs."
              )}
            </p>
          )}
          {items.length === 0 ? (
            <Empty elsewhere={others("signalements")}>Aucun signalement à trancher.</Empty>
          ) : (
            <ul className="mt-6 space-y-4">
              {(items as ReportGroup[]).map((group) => (
                <ReportCard key={group.id} group={group} now={now} />
              ))}
            </ul>
          )}
        </>
      )}
      {file === "messages" &&
        (items.length === 0 ? (
          <Empty elsewhere={others("messages")}>Aucun message signalé.</Empty>
        ) : (
          <ul className="mt-6 space-y-4">
            {(items as FlaggedMessage[]).map((message) => (
              <MessageCard key={message.id} message={message} now={now} />
            ))}
          </ul>
        ))}
      {file === "appels" &&
        (items.length === 0 ? (
          <Empty elsewhere={others("appels")}>Aucun appel en attente.</Empty>
        ) : (
          <ul className="mt-6 space-y-4">
            {(items as AppealItem[]).map((appeal) => (
              <AppealCard key={appeal.id} appeal={appeal} now={now} />
            ))}
          </ul>
        ))}
      {file === "journal" &&
        (items.length === 0 ? (
          <Empty elsewhere={Object.values(queues)}>Aucune décision pour l&apos;instant.</Empty>
        ) : (
          <div className="mt-6">
            <p className="mb-3 text-sm text-mute">Les 100 dernières décisions de l&apos;équipe, visibles de toute l&apos;équipe.</p>
            <LogList entries={items as LogEntry[]} />
          </div>
        ))}
      </div>
    </div>
  );
}
