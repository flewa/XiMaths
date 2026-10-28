import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable } from "@/components/ExerciseMeta";
import { fetchMember } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

type Props = { params: Promise<{ pseudo: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { pseudo } = await params;
  return { title: decodeURIComponent(pseudo) };
}

export default async function MemberPage({ params }: Props) {
  const { pseudo } = await params;
  let member;
  try {
    member = await fetchMember(decodeURIComponent(pseudo));
  } catch (error) {
    console.error(error);
    return <ApiUnavailable />;
  }
  if (!member) notFound();

  const stats: { label: string; value: number }[] = [];
  // Points absents : le membre a masqué sa présence dans les classements.
  if (member.points !== null) stats.push({ label: "points", value: member.points });
  stats.push(
    {
      label: member.exercises_published > 1 ? "exercices publiés" : "exercice publié",
      value: member.exercises_published,
    },
    {
      label: member.solutions_validated > 1 ? "solutions validées" : "solution validée",
      value: member.solutions_validated,
    },
  );

  return (
    <>
      <h1>{member.username}</h1>
      <p className="mt-2 text-body">
        {member.trust_level}
        {member.declared_level && ` · ${member.declared_level}`} · membre depuis le{" "}
        {dateFormat.format(new Date(member.joined))}
      </p>

      <dl className="mt-10 grid grid-cols-3 border-y border-hairline">
        {stats.map((stat) => (
          <div key={stat.label} className="flex flex-col-reverse border-l border-hairline px-4 py-4 first:border-l-0 first:pl-0">
            <dt className="text-sm text-mute">{stat.label}</dt>
            <dd className="text-[28px] font-bold leading-normal tabular-nums">{stat.value}</dd>
          </div>
        ))}
      </dl>

      <section aria-labelledby="badges" className="mt-12 sm:mt-20">
        <h2 id="badges" className="border-b border-hairline pb-2 font-bold">
          Badges
        </h2>
        {member.badges.length === 0 ? (
          <p className="mt-3 text-body">Pas encore de badge.</p>
        ) : (
          <ul>
            {member.badges.map((badge) => (
              <li key={badge.slug} className="border-b border-hairline py-3">
                <p>
                  <span className="font-bold">[x] {badge.name}</span>
                  <span className="text-sm text-mute"> · le {dateFormat.format(new Date(badge.awarded_at))}</span>
                </p>
                <p className="text-body">{badge.criterion}</p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-4">
          <Link href="/badges" className="underline underline-offset-4">
            Tous les badges et leurs critères
          </Link>
        </p>
      </section>
    </>
  );
}
