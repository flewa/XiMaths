import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { LeaderboardVisibility } from "@/components/AccountControls";
import { Avatar } from "@/components/Avatar";
import { BadgeMedal } from "@/components/BadgeMedal";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Icon } from "@/components/Icon";
import { LevelPicker } from "@/components/LevelPicker";
import {
  fetchLeaderboard,
  fetchLevels,
  fetchMe,
  type Leaderboard,
  type LeaderboardEntry,
  type Me,
} from "@/lib/api";
import { ordinal, plural, weekRange } from "@/lib/labels";
import { PODIUM_TINTS } from "@/lib/profile-art";

export const metadata: Metadata = { title: "Classements" };

type Search = { classement?: string; semaine?: string; pairs?: string };

function rankingsHref({
  board,
  week,
  peers,
}: {
  board: string;
  week?: string | null;
  peers?: boolean;
}) {
  const query = new URLSearchParams();
  if (board !== "global") query.set("classement", board);
  if (week && board !== "pantheon") query.set("semaine", week);
  if (peers) query.set("pairs", "1");
  const search = query.toString();
  return search ? `/classements?${search}` : "/classements";
}

export default async function RankingsPage({ searchParams }: { searchParams: Promise<Search> }) {
  const { classement = "global", semaine, pairs } = await searchParams;
  const peers = pairs === "1";
  let data;
  try {
    data = await Promise.all([
      fetchLevels(),
      fetchMe(),
      fetchLeaderboard({ board: classement, week: semaine, peers }),
    ]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [levels, me, board] = data;
  if (!board) notFound();
  const pantheon = board.board === "pantheon";
  const neighbours = board.me?.neighbours ?? [];
  // Seule la semaine en cours n'a pas de semaine suivante.
  const pastWeek = board.next_week !== null;
  const leader = board.top[0]?.points ?? 0;
  const segment = (active: boolean) =>
    `inline-flex h-8 items-center rounded-lg px-3 text-sm font-medium ${
      active ? "bg-selected text-ink-deep" : "text-mute hover:text-ink"
    }`;

  return (
    <>
      <h1>Classements</h1>
      <p className="mt-2 max-w-[62ch] text-body">
        {pantheon
          ? "Tous les points cumulés depuis l'inscription."
          : "Les points de la semaine, du lundi au dimanche, comptés au niveau de l'exercice résolu : un exercice de M2 fait marquer en M2."}
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-2">
        <nav aria-label="Période" className="inline-flex rounded-xl bg-surface-soft p-1">
          <Link
            href={rankingsHref({ board: pantheon ? "global" : board.board, peers })}
            aria-current={!pantheon ? "page" : undefined}
            className={segment(!pantheon)}
          >
            Semaine
          </Link>
          <Link
            href={rankingsHref({ board: "pantheon", peers })}
            aria-current={pantheon ? "page" : undefined}
            className={segment(pantheon)}
          >
            Panthéon
          </Link>
        </nav>
        {!pantheon && (
          <LevelPicker
            levels={levels}
            current={board.board === "global" ? undefined : board.board}
            hrefFor={(code) => rankingsHref({ board: code ?? "global", week: semaine, peers })}
          />
        )}
        {me?.declared_level && (
          <Link
            href={rankingsHref({ board: board.board, week: semaine, peers: !board.peers_level })}
            aria-pressed={Boolean(board.peers_level)}
            title={`Seulement ceux qui ont déclaré le niveau ${me.declared_level}, comme toi`}
            className={`inline-flex h-8 items-center gap-1.5 rounded-lg px-3 text-sm font-medium ${
              board.peers_level ? "bg-ink text-canvas" : "bg-surface-soft text-mute hover:text-ink"
            }`}
          >
            {board.peers_level && <Icon name="check" size={14} />}
            Mes pairs ({me.declared_level})
          </Link>
        )}
        {!pantheon && board.week_start && board.week_end && (
          <nav aria-label="Changer de semaine" className="inline-flex items-center rounded-xl bg-surface-soft p-1 text-sm sm:ml-auto">
            {board.previous_week ? (
              <Link
                href={rankingsHref({ board: board.board, week: board.previous_week, peers })}
                aria-label="Semaine précédente"
                className="grid size-8 place-items-center rounded-lg text-mute hover:bg-hover hover:text-ink"
              >
                ‹
              </Link>
            ) : (
              <span className="size-8" />
            )}
            <span className="px-2">
              {weekRange(board.week_start, board.week_end)}
              <span className="text-mute"> · {board.final ? "définitif" : "provisoire"}</span>
            </span>
            {board.next_week ? (
              <Link
                href={rankingsHref({ board: board.board, week: board.next_week, peers })}
                aria-label="Semaine suivante"
                className="grid size-8 place-items-center rounded-lg text-mute hover:bg-hover hover:text-ink"
              >
                ›
              </Link>
            ) : (
              <span className="size-8" />
            )}
          </nav>
        )}
      </div>

      <h2 className="mt-8">
        {/* « Global » répétait le sélecteur « Tous niveaux » juste au-dessus. */}
        {pantheon ? "Panthéon" : board.board === "global" ? "La semaine, tous niveaux" : `La semaine en ${board.board_label}`}
        {board.peers_level && <span className="font-sans text-base text-mute"> · parmi les {board.peers_level}</span>}
        {board.total > 0 && <span className="font-sans text-base text-mute"> · {plural(board.total, "participant")}</span>}
      </h2>

      <MyPosition board={board} me={me} />

      {board.total === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-hairline-strong px-6 py-10 text-center">
          <p className="font-serif text-xl text-ink-deep">Le podium est libre.</p>
          <p className="mt-2 text-body">
            {pastWeek
              ? "Personne n'a marqué de points ici cette semaine-là."
              : `Personne n'a encore marqué de points ici${pantheon ? "" : " cette semaine"}.`}
          </p>
          <Link href="/" className="mt-4 inline-block underline underline-offset-4">
            Trouver un exercice à résoudre
          </Link>
        </div>
      ) : (
        <>
          <Podium entries={board.top.slice(0, 3)} />
          {board.top.length > 3 && (
            <ol className="mt-6 divide-y divide-hairline" aria-label="Suite du classement">
              {board.top.slice(3).map((entry) => (
                <Row key={entry.username} entry={entry} leader={leader} />
              ))}
            </ol>
          )}
          {neighbours.length > 0 && (
            <>
              <p className="py-2 text-center text-mute" aria-label="Classement abrégé">
                ⋯
              </p>
              <ol className="divide-y divide-hairline" aria-label="Autour de toi">
                {neighbours.map((entry) => (
                  <Row key={entry.username} entry={entry} leader={leader} />
                ))}
              </ol>
            </>
          )}
        </>
      )}

      <div className="mt-12 space-y-3 border-t border-hairline pt-6">
        {me && <LeaderboardVisibility visible={me.leaderboard_visible} />}
        <p className="text-sm text-mute">
          {pantheon
            ? "Le Panthéon cumule tous les points depuis l'inscription. Il reste au second plan : ce sont les classements de la semaine qui comptent."
            : "Le classement repart de zéro chaque lundi ; le Panthéon garde le total depuis l'inscription. Il devient définitif le mardi à 0 h : ces 24 heures servent à annuler d'éventuels points frauduleux."}{" "}
          <Link href="/badges" className="underline underline-offset-4">
            Les badges et leurs critères
          </Link>
        </p>
      </div>
    </>
  );
}

/** Ta position : rang, points, et l'écart avec la place du dessus. */
function MyPosition({ board, me }: { board: Leaderboard; me: Me | null }) {
  if (!board.me || !me) {
    return (
      <p className="mt-4 text-body">
        <Link href="/connexion?suivant=/classements" className="underline underline-offset-4">
          Connecte-toi
        </Link>{" "}
        pour voir ta position.
      </p>
    );
  }
  const { rank, points, message } = board.me;
  if (rank === null || points === null) {
    // Classement vide : l'encadré « Le podium est libre » dit déjà la même chose.
    if (board.total === 0) return null;
    return <p className="mt-4 rounded-2xl bg-surface-soft px-5 py-4 text-body">{message}</p>;
  }
  const shown = [...board.top, ...(board.me.neighbours ?? [])];
  const above = shown.filter((entry) => entry.rank < rank).sort((a, b) => b.rank - a.rank)[0];
  const second = shown.find((entry) => entry.rank === 2);
  const gap = above
    ? `À ${plural(above.points - points, "point")} de la ${above.rank === 1 ? "1re" : ordinal(above.rank)} place.`
    : second
      ? `En tête, avec ${plural(points - second.points, "point")} d'avance.`
      : "En tête.";
  return (
    <section
      aria-label="Ta position"
      className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3 rounded-2xl border border-hairline bg-surface-soft px-5 py-4"
    >
      <Avatar avatar={me.avatar} size={48} />
      <p className="min-w-0 flex-1">
        <span className="font-serif text-[2rem] leading-none text-ink-deep">{ordinal(rank)}</span>
        <span className="text-mute"> sur {board.total}</span>
        <span className="mt-1 block text-sm text-body">{gap}</span>
      </p>
      <p className="text-right">
        <span className="block font-serif text-[1.75rem] leading-none text-ink-deep tabular-nums">{points}</span>
        <span className="text-sm text-mute">{points > 1 ? "points" : "point"}</span>
      </p>
    </section>
  );
}

function Showcase({ badges, size }: { badges: LeaderboardEntry["featured_badges"]; size: number }) {
  if (badges.length === 0) return null;
  return (
    <span className="inline-flex gap-1">
      {badges.map((badge) => (
        <span key={badge.slug} title={badge.name}>
          <BadgeMedal slug={badge.slug} size={size} />
          <span className="sr-only">{badge.name}</span>
        </span>
      ))}
    </span>
  );
}

/** Les trois premiers, en podium : deuxième, premier, troisième. L'ordre du document reste 1, 2, 3. */
function Podium({ entries }: { entries: LeaderboardEntry[] }) {
  const order = ["order-2", "order-1", "order-3"];
  return (
    <ol className="mt-8 grid grid-cols-3 items-end gap-2 sm:gap-3" aria-label="Podium">
      {entries.map((entry, index) => (
        <li
          key={entry.username}
          className={`${order[index]} relative flex min-w-0 flex-col items-center rounded-2xl border bg-surface-soft px-2 pb-4 text-center sm:px-4 sm:pb-5 ${
            index === 0 ? "pt-7 sm:pt-8 sm:pb-8" : "pt-5 sm:pt-6"
          } ${entry.is_me ? "border-accent" : "border-hairline"}`}
        >
          <span
            className="absolute -top-3 grid size-7 place-items-center rounded-full text-sm font-semibold text-[#1c1c1c]"
            style={{ background: PODIUM_TINTS[entry.rank - 1] ?? PODIUM_TINTS[2] }}
            aria-hidden="true"
          >
            {entry.rank}
          </span>
          <Avatar
            avatar={entry.avatar}
            size={index === 0 ? 72 : 60}
            className={index === 0 ? "max-sm:[--avatar:52px]" : "max-sm:[--avatar:44px]"}
          />
          <Link
            href={`/membres/${encodeURIComponent(entry.username)}`}
            className="mt-2 max-w-full truncate text-sm font-medium text-ink hover:underline sm:mt-3 sm:text-base"
          >
            <span className="sr-only">{ordinal(entry.rank)} : </span>
            {entry.username}
            {entry.is_me && <span className="text-mute"> (toi)</span>}
          </Link>
          <span className="mt-0.5 max-w-full truncate text-xs text-mute">{entry.declared_level ?? "sans niveau"}</span>
          <span className="mt-2 font-serif text-2xl leading-none text-ink-deep tabular-nums sm:mt-3 sm:text-[1.75rem]">
            {entry.points}
          </span>
          <span className="text-xs text-mute">points</span>
          <span className="mt-2 min-h-5 sm:mt-3">
            <Showcase badges={entry.featured_badges} size={18} />
          </span>
        </li>
      ))}
    </ol>
  );
}

function Row({ entry, leader }: { entry: LeaderboardEntry; leader: number }) {
  const share = leader > 0 ? Math.max(4, Math.round((entry.points / leader) * 100)) : 0;
  return (
    <li className={`-mx-3 flex items-center gap-3 rounded-xl px-3 py-2.5 ${entry.is_me ? "bg-accent-soft" : ""}`}>
      <span className="w-8 shrink-0 text-right text-sm text-mute tabular-nums">{entry.rank}</span>
      <Avatar avatar={entry.avatar} size={36} />
      <span className="min-w-0 flex-1">
        <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <Link href={`/membres/${encodeURIComponent(entry.username)}`} className="truncate font-medium text-ink hover:underline">
            {entry.username}
          </Link>
          {entry.is_me && <span className="text-sm text-mute">(toi)</span>}
          {entry.declared_level && (
            <span className="rounded-full bg-surface-card px-2 py-px text-xs font-medium text-body">{entry.declared_level}</span>
          )}
          <Showcase badges={entry.featured_badges} size={18} />
        </span>
      </span>
      <span className="w-24 shrink-0 text-right">
        <span className="block font-serif text-lg leading-tight text-ink-deep tabular-nums">{entry.points}</span>
        <span aria-hidden="true" className="mt-1 block h-1 rounded-full bg-surface-card">
          <span className="block h-1 rounded-full bg-mute" style={{ width: `${share}%` }} />
        </span>
      </span>
    </li>
  );
}
