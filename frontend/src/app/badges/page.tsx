import type { Metadata } from "next";

import { BadgeMedal } from "@/components/BadgeMedal";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Tag } from "@/components/Tag";
import { fetchBadges, fetchMe } from "@/lib/api";
import { dateFormat } from "@/lib/labels";
import { BADGE_ART } from "@/lib/profile-art";

export const metadata: Metadata = { title: "Badges" };

export default async function BadgesPage() {
  let data;
  try {
    data = await Promise.all([fetchBadges(), fetchMe()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [badges, me] = data;
  const earned = badges.filter((badge) => badge.awarded_at).length;

  return (
    <>
      <h1>Badges</h1>
      <p className="mt-2 max-w-[62ch] text-body">
        Chaque badge porte un symbole mathématique. Aucun n&apos;est secret, et un badge obtenu reste acquis
        {me ? ` : tu en as ${earned} sur ${badges.length}. Mets tes préférés en vitrine sur ton profil.` : "."}
      </p>

      <ul className="mt-10 grid gap-3 sm:grid-cols-2">
        {badges.map((badge) => {
          const meaning = BADGE_ART[badge.slug]?.meaning;
          return (
            <li
              key={badge.slug}
              className={`flex gap-4 rounded-2xl border p-4 ${
                badge.awarded_at ? "border-hairline-strong bg-surface-soft" : "border-hairline"
              }`}
            >
              <BadgeMedal slug={badge.slug} size={64} locked={!badge.awarded_at} />
              <div className="min-w-0">
                <p className="flex flex-wrap items-center gap-2">
                  <span className="font-serif text-lg text-ink-deep">{badge.name}</span>
                  {!badge.available && <Tag>bientôt</Tag>}
                </p>
                {meaning && <p className="text-xs italic text-mute">{meaning}</p>}
                <p className="mt-1.5 text-sm text-body">{badge.criterion}</p>
                <p className="mt-1.5 text-xs text-mute">
                  {badge.awarded_at
                    ? `Obtenu le ${dateFormat.format(new Date(badge.awarded_at))}`
                    : badge.holders === 0
                      ? "Personne ne l'a encore obtenu."
                      : `${badge.holders} membre${badge.holders > 1 ? "s l'ont" : " l'a"} obtenu.`}
                </p>
              </div>
            </li>
          );
        })}
      </ul>
    </>
  );
}
