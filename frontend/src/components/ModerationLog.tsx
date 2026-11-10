import Link from "next/link";

import type { LogEntry } from "@/lib/api";

import { MathText } from "./MathText";
import { Tag } from "./Tag";

const dateTime = new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium", timeStyle: "short" });

/** Lignes du journal de modération : qui a décidé quoi, quand, et pourquoi. */
export function LogList({ entries }: { entries: LogEntry[] }) {
  return (
    <ul className="divide-y divide-hairline border-y border-hairline">
      {entries.map((entry) => (
        <li key={entry.id} className="py-3 text-sm">
          <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
            <Tag>{entry.action_label}</Tag>
            <span className="text-mute">
              {dateTime.format(new Date(entry.created_at))} · par {entry.actor ?? "compte supprimé"}
            </span>
            {entry.member && (
              <Link href={`/moderation/membres/${encodeURIComponent(entry.member)}`} className="text-ink hover:underline">
                {entry.member}
              </Link>
            )}
          </p>
          <p className="mt-1 whitespace-pre-line text-body">
            {entry.url ? (
              <Link href={entry.url} className="hover:underline">
                <MathText>{entry.summary}</MathText>
              </Link>
            ) : (
              <MathText>{entry.summary}</MathText>
            )}
          </p>
        </li>
      ))}
    </ul>
  );
}

