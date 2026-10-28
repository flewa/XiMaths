import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import { SolutionForm, VoteButton } from "@/components/ContributionForms";
import { ApiUnavailable, Difficulty, LevelTags } from "@/components/ExerciseMeta";
import { MathMarkdown } from "@/components/MathMarkdown";
import { ReportButton } from "@/components/ReportButton";
import { Tag } from "@/components/Tag";
import {
  fetchExercise,
  fetchMe,
  fetchMySolutions,
  type ExerciseDetail,
  type Me,
  type MySolution,
  type Solution,
} from "@/lib/api";
import { AI_USAGE_BADGES, SOLUTION_STATUS_LABELS, dateFormat } from "@/lib/labels";

type Props = { params: Promise<{ id: string }> };

// Sections espacées, titrées par un libellé gras au-dessus d'un filet.
const section = "mt-12 sm:mt-20";
const sectionTitle = "border-b border-hairline pb-2 font-bold";

/** Pourquoi le visiteur ne peut pas voter pour ce contenu, ou null s'il le peut. */
function voteBlocker(me: Me | null, author: string | null) {
  if (!me) return "Connecte-toi pour voter.";
  if (!me.email_verified) return "Confirme ton adresse email pour voter.";
  if (me.username === author) return "On ne vote pas pour sa propre contribution.";
  return null;
}

// Signaler un doublon est un droit du niveau Relecteur.
const REVIEWER_TRUST_LEVEL = 2;

/** Bouton « Signaler », pour un membre vérifié et sur le contenu des autres seulement. */
function Report({ me, author, ...target }: { me: Me | null; author: string | null } & Omit<
  React.ComponentProps<typeof ReportButton>,
  "canReportDuplicates"
>) {
  if (!me?.email_verified || me.username === author) return null;
  return <ReportButton {...target} canReportDuplicates={me.trust_level >= REVIEWER_TRUST_LEVEL} />;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const exercise = await fetchExercise(id).catch(() => null);
  return { title: exercise?.title ?? "Exercice" };
}

export default async function ExercisePage({ params }: Props) {
  const { id } = await params;
  let exercise: ExerciseDetail | null;
  let me: Me | null;
  let mySolutions: MySolution[] = [];
  try {
    [exercise, me] = await Promise.all([fetchExercise(id), fetchMe()]);
    if (exercise && me) mySolutions = await fetchMySolutions(exercise.id);
  } catch (error) {
    console.error(error);
    return <ApiUnavailable />;
  }
  if (!exercise) notFound();
  // Doublon fusionné : son adresse redirige vers l'exercice canonique, qui a repris ses solutions.
  if (exercise.merged_into) permanentRedirect(`/exercices/${exercise.merged_into}`);

  const count = exercise.solutions.length;
  const pending = mySolutions.some((s) => s.status === "under_review" || s.status === "contested");

  return (
    <article>
      <Link href="/exercices" className="text-sm text-mute hover:text-ink">
        ← Tous les exercices
      </Link>
      <h1 className="mt-3">{exercise.title}</h1>
      <p className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-body">
        <LevelTags levels={exercise.levels} />
        <Difficulty value={exercise.difficulty} />
        {exercise.topics.length > 0 && <span>{exercise.topics.join(", ")}</span>}
        {exercise.author && (
          <Link href={`/membres/${encodeURIComponent(exercise.author)}`} className="hover:underline">
            par {exercise.author}
          </Link>
        )}
        <VoteButton
          path={`/exercises/${exercise.id}/vote`}
          count={exercise.votes}
          disabledReason={voteBlocker(me, exercise.author)}
        />
      </p>

      <section aria-labelledby="enonce" className="mt-10">
        <h2 id="enonce" className={sectionTitle}>
          Énoncé
        </h2>
        <MathMarkdown>{exercise.statement}</MathMarkdown>
      </section>

      {exercise.hints.length > 0 && (
        <section aria-labelledby="indications" className={section}>
          <h2 id="indications" className={sectionTitle}>
            Indications
          </h2>
          {exercise.hints.map((hint, index) => (
            <details key={index} className="border-b border-hairline py-3">
              <summary className="font-medium">Indication {index + 1}</summary>
              <MathMarkdown>{hint}</MathMarkdown>
            </details>
          ))}
        </section>
      )}

      <section aria-labelledby="ta-solution" className={section}>
        <h2 id="ta-solution" className={sectionTitle}>
          Ta solution
        </h2>
        {!me ? (
          <p className="mt-3 text-body">
            <Link
              href={`/connexion?suivant=/exercices/${exercise.id}`}
              className="underline underline-offset-4"
            >
              Connecte-toi
            </Link>{" "}
            pour proposer une solution : trois membres la reliront.
          </p>
        ) : !me.email_verified ? (
          <p className="mt-3 text-body">Confirme ton adresse email pour proposer une solution.</p>
        ) : (
          <>
            {mySolutions.map((solution) => (
              <MySolutionCard key={solution.id} solution={solution} />
            ))}
            {!pending && (
              <>
                <p className="mt-3">
                  <Link href={`/exercices/${exercise.id}/chrono`} className="underline underline-offset-4">
                    [⏱] S&apos;entraîner en temps limité
                  </Link>
                  <span className="text-mute"> · ou rédige librement ci-dessous</span>
                </p>
                <SolutionForm exerciseId={exercise.id} />
              </>
            )}
          </>
        )}
      </section>

      <section aria-labelledby="solutions" className={section}>
        <h2 id="solutions" className={sectionTitle}>
          {count === 0
            ? "Solutions validées"
            : `${count} solution${count > 1 ? "s" : ""} validée${count > 1 ? "s" : ""}`}
        </h2>
        {count === 0 ? (
          <p className="mt-3 text-body">
            Aucune solution validée pour l&apos;instant : cet exercice attend sa première.
          </p>
        ) : (
          <details className="py-3">
            <summary className="font-medium">
              Afficher les solutions <span className="font-normal text-mute">· essaie d&apos;abord !</span>
            </summary>
            {exercise.solutions.map((solution) => (
              <SolutionCard key={solution.id} solution={solution} me={me} />
            ))}
          </details>
        )}
      </section>

      {exercise.variants.length > 0 && (
        <section aria-labelledby="variantes" className={section}>
          <h2 id="variantes" className={sectionTitle}>
            Variantes
          </h2>
          <ul className="mt-3 space-y-1">
            {exercise.variants.map((variant) => (
              <li key={variant.id}>
                <span className="text-mute">[~] </span>
                <Link href={`/exercices/${variant.id}`} className="underline underline-offset-4">
                  {variant.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="mt-12 flex flex-wrap items-start justify-between gap-x-4 gap-y-2 border-t border-hairline pt-4 sm:mt-20">
        <p className="text-sm text-mute">
          {exercise.source_reference ? `Source : ${exercise.source_reference}. ` : ""}
          Licence {exercise.license}.
        </p>
        <Report me={me} author={exercise.author} target="exercise" targetId={exercise.id} />
      </div>
    </article>
  );
}

function SolutionCard({ solution, me }: { solution: Solution; me: Me | null }) {
  const aiBadge = AI_USAGE_BADGES[solution.ai_usage];
  return (
    <article className="mt-3 border border-hairline px-4 py-3">
      <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-mute">
        <span className="font-medium text-ink">{solution.author ?? "Compte supprimé"}</span>
        {solution.validated_at && (
          <span>validée le {dateFormat.format(new Date(solution.validated_at))}</span>
        )}
        {aiBadge && <Tag>{aiBadge}</Tag>}
        <VoteButton
          path={`/solutions/${solution.id}/vote`}
          count={solution.votes}
          disabledReason={voteBlocker(me, solution.author)}
        />
      </p>
      <MathMarkdown>{solution.body}</MathMarkdown>
      <div className="mb-1 flex justify-end">
        <Report me={me} author={solution.author} target="solution" targetId={solution.id} />
      </div>
    </article>
  );
}

function MySolutionCard({ solution }: { solution: MySolution }) {
  return (
    <article className="mt-3 border border-hairline px-4 py-3">
      <p className="flex flex-wrap items-center gap-x-4 text-sm">
        <Tag strong>{SOLUTION_STATUS_LABELS[solution.status]}</Tag>
        {solution.published_at && (
          <span className="text-mute">
            envoyée le {dateFormat.format(new Date(solution.published_at))}
          </span>
        )}
      </p>
      <details className="mt-2">
        <summary className="text-sm text-mute">Relire ma solution</summary>
        <MathMarkdown>{solution.body}</MathMarkdown>
      </details>
      {solution.feedback.length > 0 && (
        <div className="mt-3 text-sm">
          <p className="font-medium">Retours des relecteurs</p>
          <ul className="mt-1 space-y-1 text-body">
            {solution.feedback.map((feedback, index) => (
              <li key={index}>
                <span className="text-mute">[-] </span>
                {feedback}
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}
