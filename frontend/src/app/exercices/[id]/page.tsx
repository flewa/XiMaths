import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import {
  ReviseSolution,
  SolutionForm,
  VoteButton,
} from "@/components/ContributionForms";
import { Avatar } from "@/components/Avatar";
import { BadgeMedal } from "@/components/BadgeMedal";
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
  nullOnError,
  type AuthorReview,
  type ExerciseDetail,
  type ExerciseSummary,
  type Me,
  type MemberRef,
  type MySolution,
  type Topic,
} from "@/lib/api";
import { SOLUTION_STATUS_LABELS, dateFormat } from "@/lib/labels";
import { excerpt } from "@/lib/seo";
import { chapterPath, levelPath, ofChapter } from "@/lib/seo-pages";
import { SHARE_IMAGE, SITE_URL } from "@/lib/site";
import { MathText } from "@/components/MathText";

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
  const title = `${exercise.title_text} : ${kindOf(exercise)} (${exercise.primary_level})`;
  return {
    title,
    description,
    alternates: { canonical },
    openGraph: { title: exercise.title_text, description, type: "article", url: canonical, images: [SHARE_IMAGE] },
  };
}

/** Ressource pédagogique schema.org : niveaux, chapitres, licence, auteur. Google n'en tire
 * plus de résultat enrichi pour les exercices depuis 2026, mais d'autres moteurs la lisent. */
function exerciseData(exercise: ExerciseDetail, topics: Topic[]) {
  const url = `${SITE_URL}/exercices/${exercise.id}`;
  return {
    "@context": "https://schema.org",
    "@type": "LearningResource",
    name: exercise.title_text,
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
  return [["Accueil", "/"], ...middle, [exercise.title_text, `/exercices/${exercise.id}`]];
}

export default async function ExercisePage({ params }: Props) {
  const { id } = await params;
  let exercise: ExerciseDetail | null;
  let me: Me | null;
  let topics: Topic[];
  let related: ExerciseSummary[];
  let mySolutions: MySolution[] = [];
  try {
    [exercise, me, topics, related] = await Promise.all([
      fetchExercise(id),
      fetchMe(),
      fetchTopics(),
      fetchRelated(Number(id)),
    ]);
    if (exercise && me) mySolutions = await fetchMySolutions(exercise.id);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!exercise) notFound();
  // Doublon fusionné : son adresse redirige vers l'exercice canonique, qui a repris ses solutions.
  if (exercise.merged_into) permanentRedirect(`/exercices/${exercise.merged_into}`);

  const count = exercise.submitted_solutions;
  const pending = mySolutions.some((s) => s.status === "under_review");

  return (
    <article>
      <Link href="/exercices" className="text-sm text-mute hover:text-ink">
        ← Tous les exercices
      </Link>
      <h1 className="mt-3">
        <MathText>{exercise.title}</MathText>
      </h1>
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
          <Link
            href={`/membres/${encodeURIComponent(exercise.author)}`}
            className="inline-flex items-center gap-1.5 hover:underline"
          >
            {exercise.author_profile && <Avatar avatar={exercise.author_profile.avatar} size={18} />}
            par {exercise.author}
          </Link>
        )}
        {/* Les solutions restent privées : seul leur nombre est public. */}
        <span>{count === 0 ? "aucune solution envoyée" : `${count} solution${count > 1 ? "s" : ""} envoyée${count > 1 ? "s" : ""}`}</span>
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
            pour envoyer ta copie en photos : trois membres la reliront.
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
                  <span className="text-mute">ou à ton rythme, en photographiant ta copie ci-dessous</span>
                </p>
                <SolutionForm exerciseId={exercise.id} />
              </>
            )}
          </>
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
                  <MathText>{variant.title}</MathText>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {exercise.author_profile && <AuthorCard author={exercise.author_profile} />}

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

/** L'auteur, quand c'est un membre : une carte vers son profil, avec sa vitrine. */
function AuthorCard({ author }: { author: MemberRef }) {
  return (
    <section aria-label="Auteur de l'exercice" className={section}>
      <Link
        href={`/membres/${encodeURIComponent(author.username)}`}
        className="group flex items-center gap-4 rounded-2xl border border-hairline bg-surface-soft px-4 py-3.5 hover:border-hairline-strong"
      >
        <Avatar avatar={author.avatar} size={48} />
        <span className="min-w-0 flex-1">
          <span className="block text-sm text-mute">Proposé par</span>
          <span className="block truncate font-medium text-ink group-hover:underline">{author.username}</span>
        </span>
        {author.featured_badges.length > 0 && (
          <span className="flex gap-1.5 max-sm:hidden">
            {author.featured_badges.map((badge) => (
              <BadgeMedal key={badge.slug} slug={badge.slug} size={32} />
            ))}
          </span>
        )}
        <span className="flex items-center gap-1 text-sm text-mute group-hover:text-ink">
          <span className="max-sm:sr-only">Voir son profil</span>
          <Icon name="chevron" size={16} className="-rotate-90" />
        </span>
      </Link>
    </section>
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
      <ReviewsReceived solution={solution} />
      {(solution.status === "needs_work" || solution.status === "validated") && (
        <ReviseSolution
          solutionId={solution.id}
          exerciseId={exerciseId}
          validated={solution.status === "validated"}
        />
      )}
    </article>
  );
}

const VERDICT_STYLES: Record<AuthorReview["verdict"], string> = {
  correcte: "text-success",
  lacunes: "text-warning",
  incorrecte: "text-danger-text",
};

/** Les corrections reçues : verdict et commentaire de chaque relecteur, anonymes, lus dès
 * qu'ils arrivent. C'est la seule correction de l'exercice : aucune solution n'est publique. */
function ReviewsReceived({ solution }: { solution: MySolution }) {
  if (solution.reviews_expected === 0) return null;
  const done = solution.reviews.length;
  return (
    <div className="mt-3 text-sm">
      <p className="font-medium">
        Corrections reçues{" "}
        {/* Une fois la copie décidée, seul compte ce qui a été rendu. */}
        <span className="font-normal text-mute">
          {solution.status === "under_review"
            ? `· ${done} sur ${solution.reviews_expected} — les points viennent si tous tes relecteurs la jugent juste`
            : `· ${done}`}
        </span>
      </p>
      {solution.status === "under_review" && (
        <p className="mt-1 text-mute">
          {done === 0 && "Tes relecteurs ont 72 heures, et une notification t'annonce chaque correction. "}
          Si la relecture n&apos;est pas terminée sous 3 jours, l&apos;équipe du site est prévenue et prend le
          relais.
        </p>
      )}
      {done > 0 && (
        <ol className="mt-2 space-y-2">
          {solution.reviews.map((review, index) => (
            <li key={review.submitted_at} className="rounded-lg bg-surface-soft px-3 py-2">
              <p className="text-mute">
                Relecteur {index + 1} · <span className={VERDICT_STYLES[review.verdict]}>{review.verdict_label}</span>
              </p>
              <p className="mt-1 whitespace-pre-line text-body">{review.comment}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
