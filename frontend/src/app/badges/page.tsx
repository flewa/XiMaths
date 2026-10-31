import type { Metadata } from "next";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { Tag } from "@/components/Tag";
import { fetchBadges, fetchMe } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

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
      <p className="mt-2 text-body">
        Tous les badges et leurs critères : aucun n&apos;est secret, et un badge obtenu reste acquis.
        {me && ` Tu en as ${earned} sur ${badges.length}.`}
      </p>

      <ul className="mt-10 grid border-t border-hairline sm:grid-cols-2">
        {badges.map((badge) => (
          <li
            key={badge.slug}
            className={`border-b border-hairline px-4 py-4 sm:odd:border-r ${
              badge.awarded_at ? "bg-surface-card" : ""
            }`}
          >
            <p className="flex items-center justify-between gap-2">
              <span className="font-bold">
                <span className={badge.awarded_at ? "" : "text-stone"}>{badge.awarded_at ? "[x]" : "[ ]"}</span>{" "}
                {badge.name}
              </span>
              {!badge.available && <Tag>bientôt</Tag>}
            </p>
            <p className="mt-1 text-body">{badge.criterion}</p>
            <p className="mt-2 text-sm text-mute">
              {badge.awarded_at
                ? `Obtenu le ${dateFormat.format(new Date(badge.awarded_at))}`
                : !badge.available
                  ? "Arrive avec les signalements."
                  : badge.holders === 0
                    ? "Personne ne l'a encore obtenu."
                    : `${badge.holders} membre${badge.holders > 1 ? "s l'ont" : " l'a"} obtenu.`}
            </p>
          </li>
        ))}
      </ul>
    </>
  );
}
