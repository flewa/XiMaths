import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ReviewForm, VolunteerButton } from "@/components/ContributionForms";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { ProseSection } from "@/components/Prose";
import { Tag } from "@/components/Tag";
import { fetchMe, fetchOpenSolutions, fetchReviewTasks } from "@/lib/api";
import { AI_USAGE_BADGES, dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Relectures", robots: { index: false } };

// Niveau de confiance à partir duquel on est tiré au sort pour relire.
const REVIEWER_TRUST_LEVEL = 2;
// Niveau Expert : il tranche les solutions contestées.
const EXPERT_TRUST_LEVEL = 3;

export default async function ReviewsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchReviewTasks(), fetchOpenSolutions()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, tasks, open] = data;
  if (!me) redirect("/connexion?suivant=/relectures");

  return (
    <>
      <h1>Relectures</h1>
      <p className="mt-2 text-body">
        L&apos;auteur reste anonyme et tu ne vois pas les autres verdicts avant d&apos;avoir rendu le
        tien. Une relecture tirée au sort est à rendre sous 72 heures ; au-delà, elle est confiée à
        quelqu&apos;un d&apos;autre, sans pénalité.
      </p>
      {me.trust_level >= EXPERT_TRUST_LEVEL && (
        <p className="mt-2">
          <Link href="/arbitrages" className="underline underline-offset-4">
            [⚖] Solutions contestées à trancher
          </Link>
        </p>
      )}

      {tasks.length === 0 ? (
        <p className="mt-8 text-mute">
          {me.trust_level < REVIEWER_TRUST_LEVEL
            ? "Les relectures sont confiées aux membres de niveau Relecteur : 300 points et 5 solutions validées. Continue à résoudre des exercices pour y accéder."
            : "Aucune relecture en attente pour l'instant."}
        </p>
      ) : (
        tasks.map((task) => {
          const aiBadge = AI_USAGE_BADGES[task.ai_usage];
          return (
            <article key={task.id} className="mt-10 border border-hairline p-4">
              <p className="text-sm text-mute">
                [{task.primary_level}]{" "}
                <Link href={`/exercices/${task.exercise_id}`} className="font-medium text-ink hover:underline">
                  {task.exercise_title}
                </Link>
              </p>
              <MathMarkdown>{task.exercise_statement}</MathMarkdown>
              <div className="mt-4 border-l-2 border-hairline-strong bg-surface-soft px-4 py-1">
                <p className="mt-2 flex items-center gap-3 font-bold">
                  Solution proposée
                  {aiBadge && <Tag>{aiBadge}</Tag>}
                </p>
                <MathMarkdown>{task.solution_body}</MathMarkdown>
              </div>
              <div className="mt-4">
                <ReviewForm reviewId={task.id} />
              </div>
            </article>
          );
        })
      )}

      {me.trust_level >= REVIEWER_TRUST_LEVEL && (
        <ProseSection title="Relire spontanément">
          <p>
            D&apos;autres solutions attendent leurs relecteurs. Une relecture spontanée compte pour moitié
            dans la décision.
          </p>
          {open.length === 0 ? (
            <p className="text-mute">Aucune pour l&apos;instant.</p>
          ) : (
            <ul className="divide-y divide-hairline border-y border-hairline">
              {open.map((item) => (
                <li key={item.solution_id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                  <span>
                    <span className="text-mute">[{item.primary_level}] </span>
                    {item.exercise_title}
                    {item.published_at && (
                      <span className="block text-sm text-mute">
                        envoyée le {dateFormat.format(new Date(item.published_at))}
                      </span>
                    )}
                  </span>
                  <VolunteerButton solutionId={item.solution_id} />
                </li>
              ))}
            </ul>
          )}
        </ProseSection>
      )}
    </>
  );
}
