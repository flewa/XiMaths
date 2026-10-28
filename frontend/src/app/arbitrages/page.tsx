import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ArbitrationButtons } from "@/components/ContributionForms";
import { EvaluateQuestion } from "@/components/Questions";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { Tag } from "@/components/Tag";
import { fetchArbitrations, fetchMe, fetchQuestionsToEvaluate } from "@/lib/api";
import { AI_USAGE_BADGES } from "@/lib/labels";

export const metadata: Metadata = { title: "Arbitrages", robots: { index: false } };

const VERDICTS: Record<string, string> = {
  correcte: "Correcte",
  lacunes: "Correcte avec lacunes",
  incorrecte: "Incorrecte",
};

export default async function ArbitrationsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchArbitrations(), fetchQuestionsToEvaluate()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, contested, questions] = data;
  if (!me) redirect("/connexion?suivant=/arbitrages");

  return (
    <>
      <h1>Arbitrages</h1>
      <p className="mt-2 text-body">
        Les relecteurs de ces solutions ne sont pas d&apos;accord. Lis l&apos;énoncé, la solution et
        leurs avis, puis tranche. Auteur et relecteurs restent anonymes.
      </p>
      {contested === null ? (
        <p className="mt-8 text-mute">Les arbitrages sont ouverts aux experts et aux modérateurs.</p>
      ) : contested.length === 0 ? (
        <p className="mt-8 text-mute">Aucune solution contestée pour l&apos;instant.</p>
      ) : (
        contested.map((item) => {
          const aiBadge = AI_USAGE_BADGES[item.ai_usage];
          return (
            <article key={item.solution_id} className="mt-10 border border-hairline p-4">
              <p className="text-sm text-mute">
                <Link href={`/exercices/${item.exercise_id}`} className="font-medium text-ink hover:underline">
                  {item.exercise_title}
                </Link>
              </p>
              <MathMarkdown>{item.exercise_statement}</MathMarkdown>
              <div className="mt-4 border-l-2 border-hairline-strong bg-surface-soft px-4 py-1">
                <p className="mt-2 flex items-center gap-3 font-bold">
                  Solution {aiBadge && <Tag>{aiBadge}</Tag>}
                </p>
                <MathMarkdown>{item.solution_body}</MathMarkdown>
              </div>
              <ul className="mt-4 space-y-2">
                {item.reviews.map((review, index) => (
                  <li key={index}>
                    <Tag strong={review.verdict === "incorrecte"}>{VERDICTS[review.verdict] ?? review.verdict}</Tag>{" "}
                    <span className="text-sm text-mute">poids {review.weight}</span>
                    {review.feedback && <span className="block text-body">{review.feedback}</span>}
                  </li>
                ))}
              </ul>
              <div className="mt-4">
                <ArbitrationButtons solutionId={item.solution_id} />
              </div>
            </article>
          );
        })
      )}
      {questions && questions.length > 0 && (
        <section aria-labelledby="questions" className="mt-16">
          <h2 id="questions" className="border-b border-hairline pb-2 font-bold">
            Questions de compréhension à évaluer
          </h2>
          <p className="mt-2 text-body">
            L&apos;auteur a eu 5 minutes pour répondre à une question sur sa propre solution. Juge
            s&apos;il comprend le point soulevé, sans exiger une rédaction parfaite. Anonyme.
          </p>
          {questions.map((item) => (
            <article key={item.id} className="mt-8 border border-hairline p-4">
              <p className="text-sm font-medium">{item.exercise_title}</p>
              <MathMarkdown>{item.statement}</MathMarkdown>
              <div className="mt-4 border-l-2 border-hairline-strong bg-surface-soft px-4 py-1">
                <MathMarkdown>{item.solution_body}</MathMarkdown>
              </div>
              <p className="mt-4 font-medium">Question : {item.question}</p>
              {item.expected_points.length > 0 && (
                <ul className="mt-1 text-sm text-mute">
                  {item.expected_points.map((point) => (
                    <li key={point}>[·] {point}</li>
                  ))}
                </ul>
              )}
              <p className="mt-3 whitespace-pre-line border-l-2 border-ink pl-3">{item.answer}</p>
              {item.llm_assessment_label && (
                <p className="mt-3 text-sm text-mute">
                  Préévaluation automatique : {item.llm_assessment_label.toLowerCase()}. {item.llm_rationale}
                </p>
              )}
              <div className="mt-4">
                <EvaluateQuestion questionId={item.id} />
              </div>
            </article>
          ))}
        </section>
      )}
    </>
  );
}
