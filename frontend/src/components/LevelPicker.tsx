import Link from "next/link";

import type { Level } from "@/lib/api";
import { LEVEL_TRACKS } from "@/lib/labels";

import { Icon } from "./Icon";

/** Choix du niveau du fil : un menu déroulant, sans script. Il se referme en changeant de page. */
export function LevelPicker({
  levels,
  current,
  hrefFor,
}: {
  levels: Level[];
  current: string | undefined;
  hrefFor: (code: string | undefined) => string;
}) {
  const option = (active: boolean) =>
    `block rounded-md px-3 py-1.5 ${active ? "bg-selected text-ink-deep" : "text-mute hover:bg-hover hover:text-ink"}`;
  return (
    <details key={current ?? "tous"} className="plain relative">
      <summary className="flex items-center gap-1 rounded-md px-2 py-1 text-sm text-mute hover:bg-hover hover:text-ink">
        {current ? (levels.find((level) => level.code === current)?.name ?? current) : "Tous niveaux"}
        <Icon name="chevron" size={16} />
      </summary>
      <div className="absolute right-0 top-full z-10 mt-1 max-h-96 w-56 overflow-y-auto rounded-lg border border-hairline bg-surface-card p-1.5 text-sm shadow-2xl">
        <Link href={hrefFor(undefined)} className={option(!current)}>
          Tous les niveaux
        </Link>
        {LEVEL_TRACKS.map(({ track, label }) => (
          <div key={track} className="mt-1.5">
            <p className="px-3 py-1 text-xs text-stone">{label}</p>
            {levels
              .filter((level) => level.track === track)
              .map((level) => (
                <Link key={level.code} href={hrefFor(level.code)} className={option(current === level.code)}>
                  {level.name}
                </Link>
              ))}
          </div>
        ))}
      </div>
    </details>
  );
}
