import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import {
  IntegrityAnswer,
  RecommendButton,
  ReviseSolution,
  SolutionForm,
  VoteButton,
} from "@/components/ContributionForms";
import { CopyPhotoList } from "@/components/CopyPhotos";
import { ApiUnavailable, Difficulty, License, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import { secondaryButtonClass } from "@/components/Form";
import { Icon } from "@/components/Icon";
import { JsonLd, breadcrumb } from "@/components/JsonLd";
import { MathMarkdown } from "@/components/MathMarkdown";
import { ReportButton } from "@/components/ReportButton";
import { Tag } from "@/components/Tag";
import {
  fetchExercise,
  fetchMe,
  fetchMySolutions,
  fetchRelated,
  fetchTopics,
  fetchTranscriptionAvailable,
  nullOnError,
  type ExerciseDetail,
  type ExerciseSummary,
  type Me,
  type MySolution,
  type Solution,
  type Topic,
} from "@/lib/api";
import { AI_USAGE_BADGES, SOLUTION_STATUS_LABELS, dateFormat } from "@/lib/labels";
import { excerpt } from "@/lib/seo";
import { chapterPath, levelPath, ofChapter } from "@/lib/seo-pages";
import { SHARE_IMAGE, SITE_URL } from "@/lib/site";

type Props = { params: Promise<{ id: string }> };

// Sections espacées, titrées par un libellé gras au-dessus d'un filet.
const section = "mt-12 sm:mt-16";
const sectionTitle = "mb-3";

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

// Longueur qu'un moteur affiche pour une description.
const DESCRIPTION_MAX = 158;

/** « exercice de séries entières » : la notion d'abord, plus précise que le chapitre. */
function kindOf(exercise: ExerciseSummary) {
  const subject = exercise.notions[0] ?? exercise.topics[0];
  return subject ? `exercice ${ofChapter(subject)}` : "exercice de maths";
}

/** « Exercice de séries entières, niveau L2, MP, PSI. Déterminer le rayon… 2 indications. » */
function describe(exercise: ExerciseDetail) {
  const kind = kindOf(exercise);
  const head = `${kind.charAt(0).toUpperCase()}${kind.slice(1)}, niveau ${exercise.levels.join(", ")}. `;
  const hints = exercise.hints.length;
  const tail = hints > 0 ? ` ${hints} indication${hints > 1 ? "s" : ""} pour avancer.` : "";
  return `${head}${excerpt(exercise.statement, Math.max(60, DESCRIPTION_MAX - head.length - tail.length))}${tail}`;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const exercise = await fetchExercise(id).catch(nullOnError);
  if (!exercise) return { title: "Exercice" };
  const description = describe(exercise);
  // Un doublon fusionné reste lisible, mais l'adresse de référence est celle du canonique.
  const canonical = `/exercices/${exercise.merged_into ?? exercise.id}`;
  // « Intégrales de Wallis : exercice de calcul intégral (MPSI) » : ce que l'élève tape.
  const title = `${exercise.title} : ${kindOf(exercise)} (${exercise.primary_level})`;
  return {
    title,
    description,
    alternates: { canonical },
    openGraph: { title: exercise.title, description, type: "article", url: canonical, images: [SHARE_IMAGE] },
  };
}

/** Ressource pédagogique schema.org : niveaux, chapitres, licence, auteur. Google n'en tire
 * plus de résultat enrichi pour les exercices depuis 2026, mais d'autres moteurs la lisent. */
function exerciseData(exercise: ExerciseDetail, topics: Topic[]) {
  const url = `${SITE_URL}/exercices/${exercise.id}`;
  return {
    "@context": "https://schema.org",
    "@type": "LearningResource",
    name: exercise.title,
    description: excerpt(exercise.statement),
    url,
    inLanguage: "fr",
    learningResourceType: "Exercice",
    educationalLevel: exercise.levels,
    about: [...exercise.topics, ...exercise.notions].map((name) => {
      const topic = topics.find((item) => item.name === name);
      return { "@type": "Thing", name, ...(topic ? { url: `${SITE_URL}${chapterPath(topic.slug)}` } : {}) };
    }),
    isAccessibleForFree: true,
    license: "https://creativecommons.org/licenses/by-sa/4.0/",
    datePublished: exercise.published_at,
    ...(exercise.author ? { author: { "@type": "Person", name: exercise.author } } : {}),
    publisher: { "@type": "Organization", name: "XiMaths", url: SITE_URL },
  };
}

/** Fil d'Ariane pour les moteurs : chapitre puis notion quand l'exercice en a une,
 * sinon son niveau. */
function trail(exercise: ExerciseDetail, topics: Topic[]): [string, string][] {
  const notion = topics.find((topic) => topic.name === exercise.notions[0] && topic.parent);
  const chapter = notion ? topics.find((topic) => topic.slug === notion.parent) : undefined;
  const middle: [string, string][] =
    notion && chapter
      ? [
          [chapter.name, chapterPath(chapter.slug)],
          [notion.name, chapterPath(notion.slug)],
        ]
      : [[exercise.primary_level, levelPath(exercise.primary_level)]];
  return [["Accueil", "/"], ...middle, [exercise.title, `/exercices/${exercise.id}`]];
}

export default async function ExercisePage({ params }: Props) {
  const { id } = await params;
  let exercise: ExerciseDetail | null;
  let me: Me | null;
  let topics: Topic[];
  let related: ExerciseSummary[];
  let mySolutions: MySolution[] = [];
  let transcription = false;
  try {
    [exercise, me, topics, related] = await Promise.all([
      fetchExercise(id),
      fetchMe(),
      fetchTopics(),
      fetchRelated(Number(id)),
    ]);
    if (exercise && me) {
      [mySolutions, transcription] = await Promise.all([
        fetchMySolutions(exercise.id),
        fetchTranscriptionAvailable(),
      ]);
    }
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!exercise) notFound();
  // Doublon fusionné : son adresse redirige vers l'exercice canonique, qui a repris ses solutions.
  if (exercise.merged_into) permanentRedirect(`/exercices/${exercise.merged_into}`);

  const count = exercise.solutions.length;
  const pending = mySolutions.some((s) => ["held", "under_review", "contested"].includes(s.status));
  // L'auteur de l'exercice peut recommander une solution validée, une seule fois.
  const canRecommend =
    me !== null && me.username === exercise.author && !exercise.solutions.some((s) => s.recommended);

  return (
    <article>
      <Link href="/exercices" className="text-sm text-mute hover:text-ink">
        ← Tous les exercices
      </Link>
      <h1 className="mt-3">{exercise.title}</h1>
      <JsonLd data={exerciseData(exercise, topics)} />
      <JsonLd data={breadcrumb(trail(exercise, topics))} />
      <p className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-body">
        <span className="flex gap-1.5 font-medium">
          {exercise.levels.map((code) => (
            <Link key={code} href={levelPath(code)} className="text-ink hover:underline hover:underline-offset-4">
              {code}
            </Link>
          ))}
        </span>
        <Difficulty value={exercise.difficulty} withLabel />
        {exercise.topics.length + exercise.notions.length > 0 && (
          <span className="flex flex-wrap gap-x-1.5">
            {[...exercise.topics, ...exercise.notions].map((name, index) => {
              const topic = topics.find((item) => item.name === name);
              const separator = index > 0 ? " · " : "";
              return topic ? (
                <span key={name}>
                  {separator}
                  <Link href={chapterPath(topic.slug)} className="hover:text-ink hover:underline hover:underline-offset-4">
                    {name}
                  </Link>
                </span>
              ) : (
                <span key={name}>
                  {separator}
                  {name}
                </span>
              );
            })}
          </span>
        )}
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
        {/* L'énoncé, comme dans un manuel : filet corail à gauche. */}
        <div className="rounded-r-xl border-l-2 border-accent bg-surface-soft px-5 py-1 sm:px-6">
          <MathMarkdown>{exercise.statement}</MathMarkdown>
        </div>
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
              <MySolutionCard key={solution.id} solution={solution} exerciseId={exercise.id} />
            ))}
            {!pending && (
              <>
                <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2">
                  <Link href={`/exercices/${exercise.id}/chrono`} className={secondaryButtonClass}>
                    <Icon name="timer" size={16} />
                    S&apos;entraîner en temps limité
                  </Link>
                  <span className="text-mute">ou rédige librement ci-dessous</span>
                </p>
                <SolutionForm exerciseId={exercise.id} transcription={transcription} />
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
              <SolutionCard key={solution.id} solution={solution} me={me} canRecommend={canRecommend} />
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
                
                <Link href={`/exercices/${variant.id}`} className="underline underline-offset-4">
                  {variant.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {related.length > 0 && (
        <section aria-labelledby="proches" className={section}>
          <h2 id="proches" className={sectionTitle}>
            Exercices proches
          </h2>
          <ExerciseList exercises={related} />
        </section>
      )}

      <div className="mt-12 flex flex-wrap items-start justify-between gap-x-4 gap-y-2 border-t border-hairline pt-4 sm:mt-20">
        <p className="text-sm text-mute">
          {exercise.source_reference ? `Source : ${exercise.source_reference}. ` : ""}
          Licence <License code={exercise.license} />.
        </p>
        <Report me={me} author={exercise.author} target="exercise" targetId={exercise.id} />
      </div>
    </article>
  );
}

function SolutionCard({ solution, me, canRecommend }: { solution: Solution; me: Me | null; canRecommend: boolean }) {
  const aiBadge = AI_USAGE_BADGES[solution.ai_usage];
  return (
    <article className="mt-3 border border-hairline px-4 py-3">
      <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-mute">
        <span className="font-medium text-ink">{solution.author ?? "Compte supprimé"}</span>
        {solution.validated_at && (
          <span>validée le {dateFormat.format(new Date(solution.validated_at))}</span>
        )}
        {solution.recommended && <Tag strong>recommandée par l&apos;auteur</Tag>}
        {aiBadge && <Tag>{aiBadge}</Tag>}
        <VoteButton
          path={`/solutions/${solution.id}/vote`}
          count={solution.votes}
          disabledReason={voteBlocker(me, solution.author)}
        />
      </p>
      {solution.variant_statement && (
        <div className="mt-3 border-l-2 border-hairline-strong bg-surface-soft px-4 text-sm">
          <p className="pt-2 text-mute">Défi du jour · énoncé tiré pour cette solution</p>
          <MathMarkdown>{solution.variant_statement}</MathMarkdown>
        </div>
      )}
      <CopyPhotoList photos={solution.photos} />
      {solution.body && <MathMarkdown>{solution.body}</MathMarkdown>}
      <div className="mb-1 flex flex-wrap justify-end gap-x-6">
        {canRecommend && solution.author !== me?.username && <RecommendButton solutionId={solution.id} />}
        <Report me={me} author={solution.author} target="solution" targetId={solution.id} />
      </div>
    </article>
  );
}

function MySolutionCard({ solution, exerciseId }: { solution: MySolution; exerciseId: number }) {
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
        <CopyPhotoList photos={solution.photos} compact />
        {solution.body && <MathMarkdown>{solution.body}</MathMarkdown>}
      </details>
      {solution.integrity_question && solution.integrity_signal_id && (
        <div className="mt-3 border-l-2 border-hairline-strong pl-3">
          <p className="text-body">{solution.integrity_question}</p>
          <IntegrityAnswer signalId={solution.integrity_signal_id} initial={solution.integrity_answer} />
        </div>
      )}
      {solution.feedback.length > 0 && (
        <div className="mt-3 text-sm">
          <p className="font-medium">Retours des relecteurs</p>
          <ul className="mt-1 space-y-1 text-body">
            {solution.feedback.map((feedback, index) => (
              <li key={index}>
                
                {feedback}
              </li>
            ))}
          </ul>
        </div>
      )}
      {(solution.status === "needs_work" || solution.status === "validated") && (
        <ReviseSolution
          solutionId={solution.id}
          exerciseId={exerciseId}
          body={solution.body}
          hasPhotos={solution.photos.length > 0}
          validated={solution.status === "validated"}
        />
      )}
    </article>
  );
}
