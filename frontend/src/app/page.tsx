import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseList } from "@/components/ExerciseList";
import {
  ChallengeCard,
  CourseNotesCard,
  HowItWorks,
  LeadersCard,
  MemberHeader,
  TodoCard,
  VisitorHero,
  ExercisePreview,
  WeekCard,
} from "@/components/HomeHero";
import { secondaryButtonClass } from "@/components/Form";
import { JsonLd } from "@/components/JsonLd";
import { LevelPicker } from "@/components/LevelPicker";
import {
  type ExerciseSummary,
  type FeedItem,
  type Level,
  fetchCourseNotes,
  fetchDailyChallenges,
  fetchExercises,
  fetchFeed,
  fetchLeaderboard,
  fetchLevels,
  fetchMe,
  fetchProgress,
} from "@/lib/api";
import { ALL_LEVELS, HOME_VIEWS, dayLabel, homeHref, homeView, suggestedNotes, todayChallenge } from "@/lib/home";
import { SITE_URL, SOCIAL_PROFILES } from "@/lib/site";

export const metadata: Metadata = {
  title: { absolute: "XiMaths · Exercices de maths du supérieur, de la L1 au M2 et en prépa" },
  // Le fil filtré par niveau (?niveau=) ou par vue (?vue=) reste la même page pour un moteur de recherche.
  alternates: { canonical: "/" },
};

// Nom du site et logo dans les résultats de recherche.
const SITE_DATA = [
  { "@context": "https://schema.org", "@type": "WebSite", name: "XiMaths", url: `${SITE_URL}/`, inLanguage: "fr" },
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "XiMaths",
    url: `${SITE_URL}/`,
    logo: `${SITE_URL}/icons/icon-512.png`,
    sameAs: SOCIAL_PROFILES.map((profile) => profile.url),
  },
];

// Une poignée d'exercices : l'accueil oriente, le catalogue fait le reste. Au-delà, sur
// téléphone, le cours et le classement passaient à trois écrans de distance.
const VIEW_SIZE = 8;

type View = (typeof HOME_VIEWS)[number];

/** Les exercices de l'accueil : vues en onglets (le fil, sans solution, tendance, nouveaux),
 * choix du niveau, puis le lien vers tout le catalogue. */
function ExerciseFeed({
  levels,
  level,
  niveau,
  view,
  exercises,
}: {
  levels: Level[];
  level: string | undefined;
  /** ?niveau= tel que reçu, gardé d'un onglet à l'autre. */
  niveau: string | undefined;
  view: View;
  exercises: (ExerciseSummary | FeedItem)[];
}) {
  const browseHref = level ? `/exercices?niveau=${level}` : "/exercices";
  return (
    <section aria-labelledby="fil">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="fil">Exercices</h2>
        <LevelPicker levels={levels} current={level} hrefFor={(code) => homeHref(view.value, code ?? ALL_LEVELS)} />
      </div>
      <nav
        aria-label="Vue des exercices"
        className="mt-3.5 flex flex-wrap gap-1 border-b border-hairline pb-3"
      >
        {HOME_VIEWS.map((item) => (
          <Link
            key={item.value}
            href={homeHref(item.value, niveau)}
            aria-current={item.value === view.value ? "page" : undefined}
            className={`inline-flex h-8 shrink-0 items-center rounded-lg px-3 text-sm font-medium ${
              item.value === view.value ? "bg-selected text-ink-deep" : "text-mute hover:bg-hover hover:text-ink"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <p className="mb-1 mt-3 text-sm text-mute">{view.intro}</p>
      {exercises.length === 0 ? (
        <p className="py-6 text-mute">
          Aucun exercice ici pour l&apos;instant.{" "}
          <Link href="/exercices/nouveau" className="text-ink underline decoration-stone underline-offset-4">
            Publier un exercice
          </Link>
        </p>
      ) : (
        <ExerciseList exercises={exercises} />
      )}
      <p className="mt-5">
        <Link href={browseHref} className={secondaryButtonClass}>
          Voir tout le catalogue{level ? ` de ${level}` : ""} →
        </Link>
      </p>
    </section>
  );
}

/** Classement de la semaine pour l'accueil ; tant que personne n'a marqué (en début de
 * semaine), celui de la semaine passée. Secondaire : sans lui, l'accueil s'affiche quand même. */
async function weekLeaders() {
  try {
    const current = await fetchLeaderboard({ board: "global" });
    if (current && current.total === 0 && current.previous_week) {
      const previous = await fetchLeaderboard({ board: "global", week: current.previous_week });
      if (previous && previous.total > 0) return { board: previous, lastWeek: true };
    }
    return current && { board: current, lastWeek: false };
  } catch {
    return null;
  }
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ niveau?: string; vue?: string }>;
}) {
  const { niveau, vue } = await searchParams;
  const view = homeView(vue);
  let data;
  try {
    const [levels, me] = await Promise.all([fetchLevels(), fetchMe()]);
    // Par défaut, les exercices du niveau déclaré.
    const level = niveau === ALL_LEVELS ? undefined : (niveau ?? me?.declared_level ?? undefined);
    const [exercises, progress, challenges, notes, leaders] = await Promise.all([
      (view.sort ? fetchExercises(level, view.sort) : fetchFeed(level)).then((list) => list && list.slice(0, VIEW_SIZE)),
      me ? fetchProgress() : null,
      me ? fetchDailyChallenges() : [],
      me ? fetchCourseNotes().catch(() => []) : [],
      me ? weekLeaders() : null,
    ]);
    data = { levels, me, level, exercises, progress, challenges, notes, leaders };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { levels, me, level, exercises, progress, challenges, notes, leaders } = data;
  // Un niveau inconnu dans l'adresse : le fil n'existe pas.
  if (!exercises) notFound();

  const feed = (
    <ExerciseFeed levels={levels} level={level} niveau={niveau} view={view} exercises={exercises} />
  );

  if (!me) {
    return (
      <div className="page-wide">
        <JsonLd data={SITE_DATA} />
        <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_21rem] lg:items-start lg:gap-10">
          <VisitorHero />
          <div className="hidden lg:block">
            <ExercisePreview exercises={exercises.slice(0, 4)} />
          </div>
        </div>
        <HowItWorks />
        <div className="mt-14">{feed}</div>
      </div>
    );
  }

  const declared = levels.find((item) => item.code === me.declared_level) ?? null;
  const challenge = todayChallenge(challenges, me.declared_level);
  const topics = exercises.flatMap((exercise) => [...exercise.topics, ...exercise.notions]);
  const courseNotes = suggestedNotes(notes, { year: declared?.year ?? null, topics });

  // Deux colonnes sur grand écran : le défi et les exercices, puis le suivi à droite. Sur
  // téléphone, une seule : la semaine, le défi, l'à-faire, les exercices, le cours, le classement.
  return (
    <div className="page-wide">
      <JsonLd data={SITE_DATA} />
      <MemberHeader me={me} levelName={declared?.name ?? null} today={dayLabel(new Date())} />
      <div className="mt-7 flex flex-col gap-8 xl:grid xl:grid-cols-[minmax(0,1fr)_20rem] xl:items-start xl:gap-10">
        <div className="contents xl:flex xl:min-w-0 xl:flex-col xl:gap-9">
          {challenge && (
            <div className="order-2 xl:order-none">
              <ChallengeCard challenge={challenge.challenge} state={challenge.state} />
            </div>
          )}
          <div className="order-4 min-w-0 xl:order-none">{feed}</div>
        </div>
        <div className="contents xl:flex xl:flex-col xl:gap-4">
          {progress && (
            <div className="order-1 xl:order-none">
              <WeekCard progress={progress} />
            </div>
          )}
          <div className="order-3 xl:order-none">
            <TodoCard me={me} progress={progress} />
          </div>
          {courseNotes.length > 0 && (
            <div className="order-5 xl:order-none">
              <CourseNotesCard notes={courseNotes} />
            </div>
          )}
          {leaders && (
            <div className="order-6 xl:order-none">
              <LeadersCard board={leaders.board} lastWeek={leaders.lastWeek} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
