import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { LeaderboardVisibility } from "@/components/AccountControls";
import { ApiUnavailable } from "@/components/ExerciseMeta";
import { FilterChip, Tabs } from "@/components/FilterChip";
import {
  fetchLeaderboard,
  fetchLevels,
  fetchMe,
  type Leaderboard,
  type LeaderboardEntry,
} from "@/lib/api";
import { ordinal, weekRange } from "@/lib/labels";

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
    console.error(error);
    return <ApiUnavailable />;
  }
  const [levels, me, board] = data;
  if (!board) notFound();
  const pantheon = board.board === "pantheon";
  const neighbours = board.me?.neighbours ?? [];
  // Seule la semaine en cours n'a pas de semaine suivante.
  const pastWeek = board.next_week !== null;

  return (
    <>
      <h1>Classements</h1>
      <p className="mt-2 text-body">
        Les points de la semaine, du lundi au dimanche. Ils comptent pour le niveau de l&apos;exercice
        résolu : un exercice de M2 fait marquer en M2.
      </p>

      <Tabs label="Choisir un classement" className="mt-10">
        <FilterChip
          href={rankingsHref({ board: "global", week: semaine, peers })}
          label="Global"
          active={board.board === "global"}
        />
        {levels.map((level) => (
          <FilterChip
            key={level.code}
            href={rankingsHref({ board: level.code, week: semaine, peers })}
            label={level.code}
            title={level.name}
            active={board.board === level.code}
          />
        ))}
        {/* Le Panthéon reste au second plan, après les classements de la semaine. */}
        <FilterChip
          href={rankingsHref({ board: "pantheon", peers })}
          label="Panthéon"
          active={pantheon}
        />
      </Tabs>

      <div className="mt-8 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-2">
        <h2 className="font-bold">
          {pantheon ? "Panthéon des points cumulés" : board.board_label}
          {board.week_start && board.week_end && (
            <span className="ml-2 font-normal text-mute">
              · semaine {weekRange(board.week_start, board.week_end)} [
              {board.final ? "définitif" : "provisoire"}]
            </span>
          )}
        </h2>
        {!pantheon && (
          <nav aria-label="Changer de semaine" className="flex gap-4 text-sm">
            {board.previous_week && (
              <Link
                href={rankingsHref({ board: board.board, week: board.previous_week, peers })}
                className="underline underline-offset-4"
              >
                ← semaine précédente
              </Link>
            )}
            {board.next_week && (
              <Link
                href={rankingsHref({ board: board.board, week: board.next_week, peers })}
                className="underline underline-offset-4"
              >
                semaine suivante →
              </Link>
            )}
          </nav>
        )}
      </div>

      {me?.declared_level && (
        <Tabs label="Filtrer les participants" className="mt-3">
          <FilterChip
            href={rankingsHref({ board: board.board, week: semaine })}
            label="Tout le monde"
            active={!board.peers_level}
          />
          <FilterChip
            href={rankingsHref({ board: board.board, week: semaine, peers: true })}
            label={`Mes pairs (${me.declared_level})`}
            title={`Ceux qui ont déclaré le niveau ${me.declared_level}, comme toi`}
            active={Boolean(board.peers_level)}
          />
        </Tabs>
      )}

      <MyPosition board={board} />

      {board.total === 0 ? (
        <p className="mt-6 border-t border-hairline pt-4 text-body">
          {pastWeek
            ? "Personne n'a marqué de points ici cette semaine-là."
            : `Personne n'a encore marqué de points ici${pantheon ? "" : " cette semaine"}.`}{" "}
          <Link href="/" className="underline underline-offset-4">
            Trouver un exercice à résoudre
          </Link>
        </p>
      ) : (
        <table className="mt-6 w-full">
          <thead className="border-b border-hairline-strong text-left text-sm text-mute">
            <tr>
              <th scope="col" className="w-16 py-2 font-bold">
                Rang
              </th>
              <th scope="col" className="py-2 font-bold">
                Pseudo
              </th>
              <th scope="col" className="py-2 font-bold">
                Niveau
              </th>
              <th scope="col" className="py-2 text-right font-bold">
                Points
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline border-b border-hairline">
            {board.top.map((entry) => (
              <Row key={entry.username} entry={entry} />
            ))}
            {neighbours.length > 0 && (
              <>
                <tr>
                  <td colSpan={4} className="py-1 text-center text-mute" aria-label="Classement abrégé">
                    …
                  </td>
                </tr>
                {neighbours.map((entry) => (
                  <Row key={entry.username} entry={entry} />
                ))}
              </>
            )}
          </tbody>
        </table>
      )}

      <div className="mt-12 space-y-3">
        {me && <LeaderboardVisibility visible={me.leaderboard_visible} />}
        <p className="text-sm text-mute">
          {pantheon
            ? "Le Panthéon cumule tous les points depuis l'inscription. Il reste au second plan : ce sont les classements de la semaine qui comptent."
            : "Un classement devient définitif le mardi à 0 h : les 24 heures qui suivent la fin de la semaine servent à annuler d'éventuels points frauduleux."}{" "}
          <Link href="/badges" className="underline underline-offset-4">
            Les badges et leurs critères
          </Link>
        </p>
      </div>
    </>
  );
}

function MyPosition({ board }: { board: Leaderboard }) {
  if (!board.me) {
    return (
      <p className="mt-6 text-body">
        <Link href="/connexion?suivant=/classements" className="underline underline-offset-4">
          Connecte-toi
        </Link>{" "}
        pour voir ta position.
      </p>
    );
  }
  const { rank, points, message } = board.me;
  if (rank === null || points === null) {
    return <p className="mt-6 text-body">[-] {message}</p>;
  }
  const week = board.next_week ? "cette semaine-là" : "cette semaine";
  const scope =
    board.board === "pantheon"
      ? "au Panthéon"
      : board.board === "global"
        ? week
        : `en ${board.board} ${week}`;
  return (
    <p className="mt-6">
      [+] Tu es <strong>{ordinal(rank)}</strong> sur {board.total} {scope}
      {board.peers_level && `, parmi les ${board.peers_level}`}, avec{" "}
      {points > 1 ? `${points} points` : `${points} point`}.
    </p>
  );
}

function Row({ entry }: { entry: LeaderboardEntry }) {
  return (
    <tr className={entry.is_me ? "bg-surface-card font-bold" : undefined}>
      <td className="py-2 pl-2 tabular-nums">{entry.rank}</td>
      <td className="py-2">
        <Link href={`/membres/${encodeURIComponent(entry.username)}`} className="hover:underline">
          {entry.username}
        </Link>
        {entry.is_me && <span className="font-normal text-mute"> ← toi</span>}
      </td>
      <td className="py-2 text-mute">{entry.declared_level ?? "—"}</td>
      <td className="py-2 pr-2 text-right tabular-nums">{entry.points}</td>
    </tr>
  );
}
