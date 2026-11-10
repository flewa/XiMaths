import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { CopyPhotoList } from "@/components/CopyPhotos";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { FilterChip, Tabs } from "@/components/FilterChip";
import { MathMarkdown } from "@/components/MathMarkdown";
import { MathText } from "@/components/MathText";
import { AppealDecision, MessageDecision, ReportDecision } from "@/components/Moderation";
import { LogList } from "@/components/ModerationLog";
import { Tag } from "@/components/Tag";
import {
  type AppealItem,
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

function Empty({ children }: { children: React.ReactNode }) {
  return <p className="mt-6 rounded-2xl bg-surface-soft px-5 py-4 text-body">{children}</p>;
}

function ReportCard({ group }: { group: ReportGroup }) {
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
      {group.can_decide ? (
        <ReportDecision id={group.id} hasAuthor={Boolean(group.author)} />
      ) : (
        <NotYours>Ce contenu est le tien : un autre membre de l&apos;équipe tranche.</NotYours>
      )}
    </li>
  );
}

function MessageCard({ message }: { message: FlaggedMessage }) {
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
      {message.can_decide ? (
        <MessageDecision id={message.id} />
      ) : (
        <NotYours>C&apos;est ton message : un autre membre de l&apos;équipe l&apos;examine.</NotYours>
      )}
    </li>
  );
}

function AppealCard({ appeal }: { appeal: AppealItem }) {
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
  const counts: Record<File, number | null> = {
    signalements: summary.reports,
    messages: summary.messages,
    appels: summary.appeals,
    journal: null,
  };

  return (
    <div className="max-w-[760px]">
      <h1>Modération</h1>
      <p className="mt-2 text-body">
        Chaque décision est prise par un humain, motivée, envoyée à la personne concernée, contestable en appel et
        inscrite au journal. Tu ne tranches jamais ce qui te concerne : un autre membre de l&apos;équipe le fait.
      </p>
      {summary.appeals_overdue > 0 && (
        <p className="mt-4 rounded-xl bg-accent-soft px-4 py-3 text-accent-text">
          {summary.appeals_overdue > 1
            ? `${summary.appeals_overdue} appels attendent depuis plus de 7 jours`
            : "Un appel attend depuis plus de 7 jours"}
          , le délai promis aux membres.
        </p>
      )}

      <Tabs label="Files de modération" className="mt-8">
        {FILES.map((item) => (
          <FilterChip
            key={item.value}
            href={`/moderation?file=${item.value}`}
            label={counts[item.value] ? `${item.label} · ${counts[item.value]}` : item.label}
            active={file === item.value}
          />
        ))}
      </Tabs>

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
            <Empty>Aucun signalement à trancher.</Empty>
          ) : (
            <ul className="mt-6 space-y-4">
              {(items as ReportGroup[]).map((group) => (
                <ReportCard key={group.id} group={group} />
              ))}
            </ul>
          )}
        </>
      )}
      {file === "messages" &&
        (items.length === 0 ? (
          <Empty>Aucun message signalé.</Empty>
        ) : (
          <ul className="mt-6 space-y-4">
            {(items as FlaggedMessage[]).map((message) => (
              <MessageCard key={message.id} message={message} />
            ))}
          </ul>
        ))}
      {file === "appels" &&
        (items.length === 0 ? (
          <Empty>Aucun appel en attente.</Empty>
        ) : (
          <ul className="mt-6 space-y-4">
            {(items as AppealItem[]).map((appeal) => (
              <AppealCard key={appeal.id} appeal={appeal} />
            ))}
          </ul>
        ))}
      {file === "journal" &&
        (items.length === 0 ? (
          <Empty>Aucune décision pour l&apos;instant.</Empty>
        ) : (
          <div className="mt-6">
            <p className="mb-3 text-sm text-mute">Les 100 dernières décisions de l&apos;équipe, visibles de toute l&apos;équipe.</p>
            <LogList entries={items as LogEntry[]} />
          </div>
        ))}
    </div>
  );
}
