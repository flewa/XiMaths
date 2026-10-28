import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ReviewForm } from "@/components/ContributionForms";
import { ApiUnavailable } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { Tag } from "@/components/Tag";
import { fetchMe, fetchReviewTasks } from "@/lib/api";
import { AI_USAGE_BADGES } from "@/lib/labels";

export const metadata: Metadata = { title: "Relectures" };

// Niveau de confiance à partir duquel on est tiré au sort pour relire.
const REVIEWER_TRUST_LEVEL = 2;

export default async function ReviewsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchReviewTasks()]);
  } catch (error) {
    console.error(error);
    return <ApiUnavailable />;
  }
  const [me, tasks] = data;
  if (!me) redirect("/connexion?suivant=/relectures");

  return (
    <>
      <h1>Relectures</h1>
      <p className="mt-2 text-body">
        Tu as été tiré au sort pour relire ces solutions. L&apos;auteur reste anonyme et tu ne vois
        pas les autres verdicts avant d&apos;avoir rendu le tien.
      </p>

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
    </>
  );
}
