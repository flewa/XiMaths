import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { CopyPhotoList } from "@/components/CopyPhotos";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { MathText } from "@/components/MathText";
import { EvaluateQuestion } from "@/components/Questions";
import { PageIntro } from "@/components/PageIntro";
import { fetchMe, fetchQuestionsToEvaluate } from "@/lib/api";

export const metadata: Metadata = { title: "Réponses à évaluer", robots: { index: false } };

/** Réponses aux questions de compréhension, à évaluer par les experts et l'équipe. */
export default async function EvaluationsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchQuestionsToEvaluate()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, questions] = data;
  if (!me) redirect("/connexion?suivant=/evaluations");

  return (
    <>
      <h1>Réponses à évaluer</h1>
      <PageIntro id="evaluations">
        L&apos;auteur a eu 5 minutes pour répondre à une question sur sa propre solution. Juge s&apos;il comprend
        le point soulevé, sans exiger une rédaction parfaite. Tout est anonyme.
      </PageIntro>
      {questions === null ? (
        <p className="mt-8 text-mute">Ces évaluations sont ouvertes aux experts et à l&apos;équipe du site.</p>
      ) : questions.length === 0 ? (
        <p className="mt-8 text-mute">Aucune réponse à évaluer pour l&apos;instant.</p>
      ) : (
        questions.map((item) => (
          <article key={item.id} className="mt-8 border border-hairline p-4">
            <p className="text-sm font-medium">
              <MathText>{item.exercise_title}</MathText>
            </p>
            <MathMarkdown>{item.statement}</MathMarkdown>
            <div className="mt-4 border-l-2 border-hairline-strong bg-surface-soft px-4 py-1">
              <CopyPhotoList photos={item.solution_photos} />
              {item.solution_body && <MathMarkdown>{item.solution_body}</MathMarkdown>}
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
        ))
      )}
    </>
  );
}
