import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { BadgeMedal } from "@/components/BadgeMedal";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { WeekSquares } from "@/components/HomeHero";
import { Icon } from "@/components/Icon";
import { MathText } from "@/components/MathText";
import { ProgressBar } from "@/components/ProgressBar";
import { DeleteGoalButton, GoalForm, VacationForm, WeeklyGoalForm } from "@/components/ProgressForms";
import {
  type BadgeProgress,
  type MyCopy,
  type Progress,
  type Skill,
  type WeekStatus,
  fetchProgress,
  fetchTopics,
} from "@/lib/api";
import { dateFormat, oneDecimal, plural, weekRange } from "@/lib/labels";
import { chaptersOf } from "@/lib/seo-pages";

export const metadata: Metadata = { title: "Ma progression" };

const shortDate = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short", timeZone: "UTC" });

const card = "rounded-2xl border border-hairline bg-surface-soft p-5";
const cardTitle = "font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-ink";
const sectionIntro = "mt-1 text-sm text-mute";

function day(iso: string) {
  return dateFormat.format(new Date(iso));
}

function short(iso: string) {
  return shortDate.format(new Date(iso));
}

function plus(iso: string, days: number) {
  const date = new Date(`${iso}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

/* ---------- Bilan ---------- */

function Summary({ progress }: { progress: Progress }) {
  const { summary } = progress;
  const tiles = [
    {
      value: summary.validated_exercises,
      label: summary.validated_exercises > 1 ? "exercices réussis" : "exercice réussi",
    },
    { value: summary.in_review, label: summary.in_review > 1 ? "copies en relecture" : "copie en relecture" },
    { value: summary.needs_work, label: "à reprendre", alert: summary.needs_work > 0 },
    { value: summary.points_week, label: summary.points_week > 1 ? "points cette semaine" : "point cette semaine" },
  ];
  return (
    <dl className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
      {tiles.map((tile) => (
        <div
          key={tile.label}
          className={`flex flex-col-reverse rounded-2xl px-4 py-3 ${tile.alert ? "bg-accent-soft" : "bg-surface-soft"}`}
        >
          <dt className={`text-sm ${tile.alert ? "text-accent-text" : "text-mute"}`}>{tile.label}</dt>
          <dd className="font-serif text-[2rem] leading-tight text-ink-deep tabular-nums">{tile.value}</dd>
        </div>
      ))}
    </dl>
  );
}

/* ---------- Mes copies ---------- */

const COPY_STATUS: Partial<Record<MyCopy["status"], { label: string; className: string }>> = {
  needs_work: { label: "À reprendre", className: "bg-accent-soft text-accent-text" },
  under_review: { label: "En relecture", className: "bg-surface-card text-body" },
  validated: { label: "Validée", className: "text-success" },
};

function copyDetail(copy: MyCopy) {
  const sent = copy.published_at ? `envoyée le ${short(copy.published_at)}` : "";
  switch (copy.status) {
    case "needs_work":
      return "Lis les commentaires des relecteurs, puis renvoie ta copie.";
    case "under_review":
      return `${copy.reviews_done} relecture${copy.reviews_done > 1 ? "s" : ""} sur ${copy.reviews_expected} · ${sent}`;
    case "validated":
      return copy.validated_at ? `validée le ${short(copy.validated_at)}` : "validée";
    default:
      return sent;
  }
}

function Copies({ progress, firstExercise }: { progress: Progress; firstExercise: Skill["next"] }) {
  const { copies, summary } = progress;
  return (
    <section aria-labelledby="copies">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="copies">Mes copies</h2>
        {summary.copies_sent > 0 && (
          <span className="text-sm text-mute">{plural(summary.copies_sent, "copie envoyée", "copies envoyées")}</span>
        )}
      </div>
      {copies.length === 0 ? (
        <p className="mt-3 text-body">
          Tu n&apos;as pas encore envoyé de copie.{" "}
          {firstExercise && (
            <>
              Pour commencer :{" "}
              <Link href={`/exercices/${firstExercise.id}`} className="text-ink underline underline-offset-4">
                <MathText>{firstExercise.title}</MathText>
              </Link>
              .
            </>
          )}
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-hairline">
          {copies.map((copy) => {
            const status = COPY_STATUS[copy.status];
            return (
              <li key={copy.id}>
                <Link
                  href={`/exercices/${copy.exercise_id}#ta-solution`}
                  className="-mx-3 flex items-center gap-4 rounded-xl px-3 py-3 hover:bg-hover"
                >
                  {/* Sur téléphone, l'état passe au-dessus du titre, qui garde toute la largeur. */}
                  <span className="flex min-w-0 flex-1 flex-col items-start gap-1.5 sm:flex-row sm:items-center sm:gap-4">
                    <span
                      className={`inline-flex shrink-0 items-center justify-center gap-1 rounded-full py-1 text-xs font-medium sm:w-[7.5rem] ${
                        copy.status === "validated" ? "" : "px-2.5"
                      } ${status?.className ?? ""}`}
                    >
                      {copy.status === "validated" && <Icon name="check" size={14} />}
                      {status?.label ?? copy.status}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-ink sm:truncate">
                        <MathText>{copy.exercise_title}</MathText>
                      </span>
                      <span className="block text-[13px] text-mute">{copyDetail(copy)}</span>
                    </span>
                  </span>
                  <Icon name="chevron" size={16} className="shrink-0 -rotate-90 text-stone" />
                </Link>
              </li>
            );
          })}
        </ul>
      )}
      <p className="mt-3 text-xs text-mute">Tes copies restent privées : seuls tes relecteurs, tirés au sort, les lisent, sauf celle que tu acceptes de voir servir de copie modèle.</p>
    </section>
  );
}

/* ---------- Par chapitre ---------- */

/** Ce que veut dire une maîtrise de 0 à 5, en mots. */
function masteryLabel(mastery: number) {
  if (mastery === 0) return "pas commencé";
  if (mastery < 1) return "premiers pas";
  if (mastery < 2) return "les bases";
  if (mastery < 3) return "solide";
  if (mastery < 4) return "avancé";
  return "expert";
}

/** Cinq crans, remplis jusqu'à la maîtrise (qui peut s'arrêter au milieu d'un cran). */
function Pips({ mastery }: { mastery: number }) {
  return (
    <span aria-hidden="true" className="flex gap-1">
      {[0, 1, 2, 3, 4].map((index) => (
        <span key={index} className="h-2 w-6 overflow-hidden rounded-full bg-surface-card">
          <span
            className="block h-full rounded-full bg-accent"
            style={{ width: `${Math.max(0, Math.min(1, mastery - index)) * 100}%` }}
          />
        </span>
      ))}
    </span>
  );
}

function NextExercise({ next, prefix }: { next: Skill["next"]; prefix: string }) {
  if (!next) return <span className="text-mute">Rien de nouveau à te proposer ici pour l&apos;instant.</span>;
  return (
    <>
      <span className="text-mute">{prefix} </span>
      <Link href={`/exercices/${next.id}`} className="text-ink underline decoration-stone underline-offset-4 hover:decoration-ink">
        <MathText>{next.title}</MathText>
      </Link>
      <span className="text-mute"> · difficulté {next.difficulty}</span>
    </>
  );
}

function Chapters({ skills }: { skills: Skill[] }) {
  const started = skills.filter((skill) => skill.solved > 0).sort((a, b) => b.mastery - a.mastery);
  const fresh = skills.filter((skill) => skill.solved === 0);
  return (
    <section aria-labelledby="chapitres">
      <h2 id="chapitres">Par chapitre</h2>
      <p className={sectionIntro}>
        {started.length > 0
          ? "Ta maîtrise de chaque chapitre, de 0 à 5, et l'exercice qui te fera passer un cran."
          : "Tu n'as encore réussi aucun exercice : voici par où commencer dans chaque chapitre."}
      </p>

      {started.length > 0 && (
        <ul className="mt-3 divide-y divide-hairline">
          {started.map((skill) => (
            <li key={skill.slug} className="py-4">
              <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                <span className="min-w-36 font-medium text-ink">{skill.topic}</span>
                <Pips mastery={skill.mastery} />
                <span className="text-sm text-mute">
                  <span className="sr-only">Maîtrise {oneDecimal.format(skill.mastery)} sur 5 : </span>
                  {masteryLabel(skill.mastery)} · {plural(skill.solved, "exercice réussi", "exercices réussis")}
                </span>
              </div>
              <p className="mt-2 text-sm">
                <NextExercise next={skill.next} prefix="Pour progresser :" />
              </p>
            </li>
          ))}
        </ul>
      )}

      {fresh.length > 0 && (
        <>
          {started.length > 0 && <h3 className="mt-6 font-medium">À découvrir</h3>}
          <ul className="mt-3 grid gap-3 sm:grid-cols-2">
            {fresh.map((skill) => (
              <li key={skill.slug} className="rounded-xl border border-hairline px-4 py-3 text-sm">
                <span className="block font-medium text-ink">{skill.topic}</span>
                <span className="mt-1 block">
                  <NextExercise next={skill.next} prefix="Commencer par" />
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

/* ---------- Objectifs ---------- */

function Goals({ progress, topics }: { progress: Progress; topics: Parameters<typeof GoalForm>[0]["topics"] }) {
  return (
    <section aria-labelledby="objectifs">
      <h2 id="objectifs">Mes objectifs</h2>
      {progress.goals.length === 0 ? (
        <p className={sectionIntro}>
          Un partiel, des oraux ? Fixe-toi un cap : «&nbsp;Partiel d&apos;algèbre linéaire : 10 exercices d&apos;ici
          le 10&nbsp;janvier&nbsp;», ou «&nbsp;Oraux : 3 exercices chronométrés par semaine&nbsp;».
        </p>
      ) : (
        <ul className="mt-2 divide-y divide-hairline">
          {progress.goals.map((goal) => {
            const reached = goal.done >= goal.target;
            return (
              <li key={goal.id} className="py-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-medium text-ink">{goal.title}</span>
                  <DeleteGoalButton goalId={goal.id} />
                </div>
                <p className="mt-2 flex flex-wrap items-center gap-x-3 tabular-nums">
                  <ProgressBar done={goal.done} target={goal.target} className="w-48" /> {goal.done} / {goal.target}
                  {goal.per_week && <span className="text-mute"> cette semaine</span>}
                  {reached && <span className="text-success">· atteint</span>}
                </p>
                <p className="text-sm text-mute">
                  {goal.per_week ? "jusqu'au" : "d'ici le"} {day(goal.deadline)}
                  {goal.topic && ` · ${goal.topic}`}
                </p>
              </li>
            );
          })}
        </ul>
      )}
      <details className="plain mt-4">
        <summary className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg bg-surface-card px-3 py-1.5 text-sm font-medium text-ink hover:bg-hover">
          <Icon name="plus" size={14} /> Nouvel objectif
        </summary>
        <div className="mt-4 rounded-2xl border border-hairline p-5">
          <GoalForm topics={topics} />
        </div>
      </details>
    </section>
  );
}

/* ---------- Régularité ---------- */

// Couleur de chaque semaine passée selon son état ; l'état est aussi dit en toutes lettres.
const WEEK_FILL: Record<WeekStatus, string> = {
  atteint: "bg-accent",
  joker: "bg-stone",
  vacances: "bg-hairline-strong",
  manque: "bg-mute/50",
};
const WEEK_LEGEND: Record<WeekStatus, string> = {
  atteint: "objectif atteint",
  joker: "sauvée par un joker",
  vacances: "examens ou vacances",
  manque: "manquée",
};

/** Les semaines passées, de la plus ancienne à la dernière : une barre par semaine, haute
 * de ses jours actifs, un trait à hauteur de l'objectif. */
function WeeksChart({ history }: { history: Progress["history"] }) {
  const weeks = [...history].reverse();
  const statuses = (Object.keys(WEEK_LEGEND) as WeekStatus[]).filter((status) =>
    weeks.some((week) => week.status === status),
  );
  return (
    <figure className="mt-5">
      <figcaption className="text-[13px] text-mute">
        {weeks.length > 1 ? `Tes ${weeks.length} dernières semaines` : "Ta dernière semaine"}
      </figcaption>
      <ol className="mt-2 flex h-16 items-end gap-0.5 border-b border-hairline-strong">
        {weeks.map((week) => {
          const range = weekRange(week.week_start, plus(week.week_start, 6));
          const text = `${range} : ${plural(week.active_days, "jour actif", "jours actifs")} sur ${week.goal}, ${WEEK_LEGEND[week.status]}.`;
          return (
            <li key={week.week} title={text} className="relative flex h-full max-w-6 flex-1 items-end">
              <span className="sr-only">{text}</span>
              <span
                aria-hidden="true"
                className={`block w-full rounded-t-[4px] ${WEEK_FILL[week.status]}`}
                style={{ height: `max(2px, ${(week.active_days / 7) * 100}%)` }}
              />
              {/* L'objectif de la semaine. */}
              <span
                aria-hidden="true"
                className="absolute inset-x-0 h-px bg-ink/60"
                style={{ bottom: `${(week.goal / 7) * 100}%` }}
              />
            </li>
          );
        })}
      </ol>
      <div aria-hidden="true" className="mt-1 flex justify-between text-[11px] text-mute">
        <span>{short(weeks[0].week_start)}</span>
        <span>{short(weeks[weeks.length - 1].week_start)}</span>
      </div>
      <ul className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[12px] text-mute">
        {statuses.map((status) => (
          <li key={status} className="inline-flex items-center gap-1.5">
            <span aria-hidden="true" className={`size-2 rounded-sm ${WEEK_FILL[status]}`} />
            {WEEK_LEGEND[status]}
          </li>
        ))}
        <li className="inline-flex items-center gap-1.5">
          <span aria-hidden="true" className="h-px w-3 bg-ink/60" />
          objectif
        </li>
      </ul>
    </figure>
  );
}

function Regularity({ progress }: { progress: Progress }) {
  const missing = Math.max(0, progress.goal_days - progress.active_days);
  return (
    <section aria-labelledby="regularite" className={card}>
      <h2 id="regularite" className={cardTitle}>
        Régularité
      </h2>
      <p className="mt-1 text-[13px] text-mute">{weekRange(progress.days[0].date, progress.days[6].date)}</p>
      <WeekSquares days={progress.days} />
      <p className="mt-3 text-sm text-ink">
        {progress.achieved
          ? `Objectif de la semaine atteint : ${progress.active_days} jours actifs.`
          : `${progress.active_days} jour${progress.active_days > 1 ? "s" : ""} actif${progress.active_days > 1 ? "s" : ""} sur ${progress.goal_days} · encore ${missing}.`}
      </p>
      <p className="mt-1 text-sm text-mute">
        Série : {plural(progress.streak, "semaine")} · {plural(progress.jokers_left, "joker")} ce mois-ci
        {progress.vacation && ` · en pause jusqu'au ${day(progress.vacation.end)}`}
      </p>

      {progress.history.length > 0 ? (
        <WeeksChart history={progress.history} />
      ) : (
        <p className="mt-4 text-[13px] text-mute">Tes semaines passées s&apos;afficheront ici, semaine après semaine.</p>
      )}

      <details className="mt-4 border-t border-hairline pt-3">
        <summary className="cursor-pointer text-sm text-mute hover:text-ink">Régler mon rythme</summary>
        <div className="mt-3 space-y-5">
          <WeeklyGoalForm days={progress.goal_days} />
          <div>
            <p className="text-sm font-medium text-ink">Examens ou vacances</p>
            <p className="mt-0.5 text-[13px] text-mute">La série se met en pause jusqu&apos;à 4 semaines, sans rien perdre.</p>
            <div className="mt-2">
              <VacationForm until={progress.vacation?.end ?? null} />
            </div>
          </div>
        </div>
      </details>
    </section>
  );
}

/* ---------- Prochains badges ---------- */

function NextBadges({ badges }: { badges: BadgeProgress[] }) {
  return (
    <section aria-labelledby="prochains-badges" className={card}>
      <h2 id="prochains-badges" className={cardTitle}>
        Prochains badges
      </h2>
      {badges.length === 0 ? (
        <p className="mt-2 text-sm text-mute">Tu as tous les badges qui se mesurent. Bravo.</p>
      ) : (
        <ul className="mt-3 space-y-4">
          {badges.map((badge) => (
            <li key={badge.slug} className="flex gap-3">
              <BadgeMedal slug={badge.slug} size={40} locked />
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-medium text-ink">{badge.name}</span>
                <span className="block text-[13px] leading-snug text-mute">{badge.criterion}</span>
                <span className="mt-1.5 flex items-center gap-2 text-[13px] tabular-nums text-body">
                  <ProgressBar done={badge.done} target={badge.target} className="w-auto flex-1" />
                  {badge.done} / {badge.target}
                </span>
              </span>
            </li>
          ))}
        </ul>
      )}
      <Link href="/badges" className="mt-3 inline-block text-[13px] text-mute underline underline-offset-4 hover:text-ink">
        Tous les badges
      </Link>
    </section>
  );
}

/* ---------- Page ---------- */

export default async function ProgressPage() {
  let data;
  try {
    data = await Promise.all([fetchProgress(), fetchTopics()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [progress, topics] = data;
  if (!progress) redirect("/connexion?suivant=/progression");
  const { contributor } = progress;
  // Premier exercice proposé, pour qui n'a encore rien envoyé.
  const firstExercise = progress.skills.find((skill) => skill.next)?.next ?? null;

  return (
    <div className="page-wide">
      <h1>Ma progression</h1>
      <p className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-body">
        <span>
          Niveau <span className="font-semibold text-ink">{contributor.level}</span> de contributeur
        </span>
        {contributor.next !== null ? (
          <>
            <ProgressBar done={contributor.points - contributor.floor} target={contributor.next - contributor.floor} />
            <span className="text-sm text-mute tabular-nums">
              {contributor.points} / {contributor.next} points pour le niveau {contributor.level + 1}
            </span>
          </>
        ) : (
          <span className="text-sm text-mute">niveau maximal</span>
        )}
      </p>

      <Summary progress={progress} />

      <div className="mt-12 flex flex-col gap-12 xl:grid xl:grid-cols-[minmax(0,1fr)_20rem] xl:items-start xl:gap-10">
        <div className="min-w-0 space-y-12">
          <Copies progress={progress} firstExercise={firstExercise} />
          <Chapters skills={progress.skills} />
          <Goals progress={progress} topics={chaptersOf(topics)} />
        </div>
        <div className="space-y-4">
          <Regularity progress={progress} />
          <NextBadges badges={progress.next_badges} />
        </div>
      </div>

      <details className="mt-14 border-t border-hairline pt-4 text-sm text-mute">
        <summary className="cursor-pointer hover:text-ink">Comment sont calculés ces chiffres ?</summary>
        <div className="mt-3 max-w-[70ch] space-y-2">
          <p>
            <span className="text-ink">Jour actif.</span> Une tentative de solution, une relecture ou 15 minutes de
            chronomètre ; une simple connexion ne compte pas. La série est hebdomadaire : tu choisis combien de jours
            par semaine. Deux jokers par mois protègent ta série quand une semaine est manquée. La régularité rapporte
            des badges, jamais de points.
          </p>
          <p>
            <span className="text-ink">Maîtrise d&apos;un chapitre.</span> La moyenne des difficultés de tes 5
            exercices réussis les plus difficiles, une case vide comptant 0 : cinq exercices de difficulté 3 donnent
            3. L&apos;exercice proposé vise un cran au-dessus. Cette carte n&apos;est visible que par toi.
          </p>
          <p>
            <span className="text-ink">Niveau de contributeur.</span> Il suit tes points sur une courbe quadratique :
            20 points pour le niveau 2, 1 620 pour le 10, 16 820 pour le 30.
          </p>
        </div>
      </details>
    </div>
  );
}
