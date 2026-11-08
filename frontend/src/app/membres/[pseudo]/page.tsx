import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Avatar } from "@/components/Avatar";
import { BadgeMedal } from "@/components/BadgeMedal";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { secondaryButtonClass } from "@/components/Form";
import { ShareProfile } from "@/components/ShareProfile";
import { type Member, fetchBadges, fetchMember } from "@/lib/api";
import { dateFormat, plural } from "@/lib/labels";
import { chapterPath } from "@/lib/seo-pages";

type Props = { params: Promise<{ pseudo: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { pseudo } = await params;
  // Un profil est public, mais n'a rien à faire dans les résultats de recherche.
  return { title: decodeURIComponent(pseudo), robots: { index: false } };
}

const sectionTitle = "font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-ink";

function stats(member: Member) {
  return [
    // Points absents : le membre a masqué sa présence dans les classements.
    member.points !== null && { label: "points", value: member.points },
    member.contributor_level !== null && { label: "niveau de contributeur", value: member.contributor_level },
    { label: member.exercises_published > 1 ? "exercices publiés" : "exercice publié", value: member.exercises_published },
    { label: member.solutions_validated > 1 ? "solutions validées" : "solution validée", value: member.solutions_validated },
    { label: member.reviews_done > 1 ? "relectures rendues" : "relecture rendue", value: member.reviews_done },
    { label: member.streak_weeks > 1 ? "semaines de série" : "semaine de série", value: member.streak_weeks },
  ].filter((stat): stat is { label: string; value: number } => Boolean(stat));
}

export default async function MemberPage({ params }: Props) {
  const { pseudo } = await params;
  let data;
  try {
    const [member, catalog] = await Promise.all([fetchMember(decodeURIComponent(pseudo)), fetchBadges()]);
    data = { member, catalog };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { member, catalog } = data;
  if (!member) notFound();

  return (
    <>
      <header className="flex flex-wrap items-start gap-x-6 gap-y-4">
        <Avatar avatar={member.avatar} size={88} />
        <div className="min-w-0 flex-1 basis-64">
          <h1 className="break-words">{member.username}</h1>
          <p className="mt-1 text-sm text-mute">
            {[member.declared_level_name, member.trust_level, `membre depuis le ${dateFormat.format(new Date(member.joined))}`]
              .filter(Boolean)
              .join(" · ")}
          </p>
          {member.bio && <p className="mt-3 max-w-[60ch] text-body">{member.bio}</p>}
          {member.favorite_topics.length > 0 && (
            <p className="mt-3 flex flex-wrap items-center gap-2 text-sm">
              <span className="text-mute">Aime :</span>
              {member.favorite_topics.map((topic) => (
                <Link
                  key={topic.slug}
                  href={chapterPath(topic.slug)}
                  className="rounded-full bg-surface-card px-3 py-1 text-ink hover:bg-surface-dark-elevated"
                >
                  {topic.name}
                </Link>
              ))}
            </p>
          )}
          {member.is_me && (
            <div className="mt-4 flex flex-wrap gap-2">
              <Link href="/reglages#profil" className={secondaryButtonClass}>
                Personnaliser mon profil
              </Link>
              <ShareProfile username={member.username} />
            </div>
          )}
        </div>

      </header>

      {(member.featured_badges.length > 0 || member.is_me) && (
        <section aria-labelledby="vitrine" className="mt-10">
          <h2 id="vitrine" className={sectionTitle}>
            Vitrine
          </h2>
          {member.featured_badges.length > 0 ? (
            <ul className="mt-4 grid gap-3 sm:grid-cols-3">
              {member.featured_badges.map((badge) => (
                <li key={badge.slug} className="flex items-center gap-4 rounded-2xl border border-hairline bg-surface-soft p-4">
                  <BadgeMedal slug={badge.slug} size={64} />
                  <span className="min-w-0">
                    <span className="block font-serif text-lg text-ink-deep">{badge.name}</span>
                    <span className="block text-xs text-mute">le {dateFormat.format(new Date(badge.awarded_at))}</span>
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-mute">
              Mets jusqu&apos;à trois de tes badges en avant, depuis{" "}
              <Link href="/reglages#profil" className="text-ink underline underline-offset-4">
                tes réglages
              </Link>
              .
            </p>
          )}
        </section>
      )}

      <dl className="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-3">
        {stats(member).map((stat) => (
          <div key={stat.label} className="flex flex-col-reverse rounded-2xl bg-surface-soft px-4 py-3">
            <dt className="text-sm text-mute">{stat.label}</dt>
            <dd className="font-serif text-[2rem] leading-tight text-ink-deep tabular-nums">{stat.value}</dd>
          </div>
        ))}
      </dl>
      {member.points === null && (
        <p className="mt-2 text-sm text-mute">Ce membre ne montre pas ses points dans les classements.</p>
      )}

      <section aria-labelledby="badges" className="mt-12">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 id="badges" className={sectionTitle}>
            Badges · {member.badges.length} sur {catalog.length}
          </h2>
          <Link href="/badges" className="text-sm text-mute underline underline-offset-4 hover:text-ink">
            Tous les badges et leurs critères
          </Link>
        </div>
        <ul className="mt-4 grid grid-cols-3 gap-x-3 gap-y-5 sm:grid-cols-5">
          {catalog.map((badge) => {
            const earned = member.badges.find((item) => item.slug === badge.slug);
            return (
              <li key={badge.slug} className="flex flex-col items-center gap-2 text-center" title={badge.criterion}>
                <BadgeMedal slug={badge.slug} size={56} locked={!earned} />
                <span className={`text-xs leading-snug ${earned ? "text-ink" : "text-mute"}`}>
                  {badge.name}
                  <span className="sr-only">{earned ? ", obtenu" : ", pas encore obtenu"}</span>
                </span>
              </li>
            );
          })}
        </ul>
      </section>

      <section aria-labelledby="exercices" className="mt-12">
        <h2 id="exercices" className={sectionTitle}>
          {member.recent_exercises.length > 0
            ? `Derniers exercices publiés · ${plural(member.exercises_published, "exercice")}`
            : "Exercices publiés"}
        </h2>
        {member.recent_exercises.length > 0 ? (
          <div className="mt-2">
            <ExerciseList exercises={member.recent_exercises} showAuthor={false} />
          </div>
        ) : (
          <p className="mt-3 text-sm text-mute">
            {member.is_me ? (
              <>
                Pas encore d&apos;exercice publié.{" "}
                <Link href="/exercices/nouveau" className="text-ink underline underline-offset-4">
                  Publier un exercice
                </Link>
              </>
            ) : (
              "Pas encore d'exercice publié."
            )}
          </p>
        )}
        <p className="mt-4 text-xs text-mute">Les solutions restent privées : seuls leurs nombres apparaissent ici.</p>
      </section>
    </>
  );
}
