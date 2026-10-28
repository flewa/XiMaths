import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { DeleteGoalButton, GoalForm, VacationForm, WeeklyGoalForm } from "@/components/ProgressForms";
import { Tag } from "@/components/Tag";
import { type ContributorLevel, type Skill, type WeekStatus, fetchProgress, fetchTopics } from "@/lib/api";
import { dateFormat, oneDecimal, progressBar, weekRange } from "@/lib/labels";

export const metadata: Metadata = { title: "Ma progression" };

const weekday = new Intl.DateTimeFormat("fr-FR", { weekday: "short", timeZone: "UTC" });

function day(iso: string) {
  return dateFormat.format(new Date(iso));
}

function plus(iso: string, days: number) {
  const date = new Date(`${iso}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

const STATUS_MARK: Record<WeekStatus, string> = { atteint: "[+]", joker: "[j]", vacances: "[~]", manque: "[-]" };

function LevelLine({ contributor }: { contributor: ContributorLevel }) {
  if (contributor.next === null) {
    return (
      <p className="font-mono tabular-nums">
        <span aria-hidden="true">{progressBar(1, 1)}</span> {contributor.points} points · niveau maximal
      </p>
    );
  }
  return (
    <p className="font-mono tabular-nums">
      <span aria-hidden="true">{progressBar(contributor.points - contributor.floor, contributor.next - contributor.floor)}</span>{" "}
      {contributor.points} /{" "}
      {contributor.next} points <span className="text-mute">pour le niveau {contributor.level + 1}</span>
    </p>
  );
}

function SkillRow({ skill }: { skill: Skill }) {
  return (
    <li className="py-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="font-medium">{skill.topic}</span>
        <span className="text-sm text-mute">
          {skill.solved === 0
            ? "aucun exercice résolu"
            : `${skill.solved} exercice${skill.solved > 1 ? "s" : ""} résolu${skill.solved > 1 ? "s" : ""}`}
        </span>
      </div>
      <p className="mt-1 font-mono tabular-nums">
        <span aria-hidden="true">{progressBar(skill.mastery, 5)}</span> {oneDecimal.format(skill.mastery)} / 5
      </p>
      <p className="text-sm text-mute">
        {skill.next ? (
          <>
            Prochain :{" "}
            <Link href={`/exercices/${skill.next.id}`} className="text-ink underline underline-offset-4">
              {skill.next.title}
            </Link>{" "}
            · difficulté {skill.next.difficulty}
          </>
        ) : (
          "Rien à te proposer dans ce chapitre pour l'instant."
        )}
      </p>
    </li>
  );
}

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
  const missing = Math.max(0, progress.goal_days - progress.active_days);

  return (
    <div className="max-w-[720px]">
      <h1>Ma progression</h1>
      <p className="mt-2 text-body">
        Une série hebdomadaire plutôt que quotidienne : tu choisis ton rythme. Un jour actif, c&apos;est
        une tentative de solution, une relecture ou 15 minutes de chronomètre ; une simple connexion ne
        compte pas. La régularité rapporte des badges, jamais de points.
      </p>

      <section aria-labelledby="this-week" className="mt-10">
        <h2 id="this-week" className="border-b border-hairline pb-2 font-bold">
          Cette semaine <span className="font-normal text-mute">· {weekRange(progress.days[0].date, progress.days[6].date)}</span>
        </h2>
        <ol className="mt-4 grid grid-cols-7 gap-1 text-center">
          {progress.days.map((item) => (
            <li key={item.date} className={item.future ? "text-stone" : ""}>
              <span className="block text-sm text-mute">{weekday.format(new Date(`${item.date}T00:00:00Z`))}</span>
              <span aria-label={item.active ? "actif" : item.future ? "à venir" : "inactif"}>
                {item.active ? "[x]" : item.future ? " · " : "[ ]"}
              </span>
            </li>
          ))}
        </ol>
        <p className="mt-4">
          {progress.achieved
            ? `[+] Objectif atteint : ${progress.active_days} jours actifs sur ${progress.goal_days}.`
            : `${progress.active_days} jour${progress.active_days > 1 ? "s" : ""} actif${progress.active_days > 1 ? "s" : ""} sur ${progress.goal_days} · encore ${missing} cette semaine.`}
        </p>

        <dl className="mt-6 grid grid-cols-2 border-y border-hairline sm:grid-cols-3">
          <div className="flex flex-col-reverse py-4">
            <dt className="text-sm text-mute">semaines tenues d&apos;affilée</dt>
            <dd className="text-[28px] font-bold leading-normal tabular-nums">{progress.streak}</dd>
          </div>
          <div className="flex flex-col-reverse border-l border-hairline px-4 py-4">
            <dt className="text-sm text-mute">jokers ce mois-ci</dt>
            <dd className="text-[28px] font-bold leading-normal tabular-nums">{progress.jokers_left} / 2</dd>
          </div>
          <div className="col-span-2 flex flex-col-reverse border-t border-hairline py-4 sm:col-span-1 sm:border-l sm:border-t-0 sm:px-4">
            <dt className="text-sm text-mute">mode examens ou vacances</dt>
            <dd className="font-bold leading-normal">
              {progress.vacation ? `jusqu'au ${day(progress.vacation.end)}` : "inactif"}
            </dd>
          </div>
        </dl>
        <p className="mt-3 text-sm text-mute">
          Deux jokers par mois protègent ta série d&apos;eux-mêmes quand une semaine est manquée.
        </p>
      </section>

      <section aria-labelledby="skills" className="mt-12">
        <h2 id="skills" className="border-b border-hairline pb-2 font-bold">
          Niveau de contributeur
        </h2>
        <p className="mt-4 text-[28px] font-bold leading-normal tabular-nums">
          {progress.contributor.level} <span className="text-base font-normal text-mute">sur 30</span>
        </p>
        <LevelLine contributor={progress.contributor} />
        <p className="mt-2 text-sm text-mute">
          Le niveau de contributeur suit tes points, sur une courbe quadratique : 20 points pour le niveau 2,
          1 620 pour le 10, 16 820 pour le 30.
        </p>

        <h3 className="mt-8 font-medium">Carte de compétences</h3>
        <p className="mt-1 text-sm text-mute">
          Dans chaque chapitre, ta maîtrise est la moyenne des difficultés de tes 5 exercices résolus les plus
          difficiles ; une case vide compte 0. L&apos;exercice proposé vise un cran au-dessus. Cette carte
          n&apos;est visible que par toi.
        </p>
        <ul className="mt-2 divide-y divide-hairline">
          {progress.skills.map((skill) => (
            <SkillRow key={skill.slug} skill={skill} />
          ))}
        </ul>
      </section>

      <section aria-labelledby="settings" className="mt-12 space-y-8">
        <h2 id="settings" className="border-b border-hairline pb-2 font-bold">
          Mon rythme
        </h2>
        <WeeklyGoalForm days={progress.goal_days} />
        <div>
          <h3 className="font-medium">Examens ou vacances</h3>
          <p className="mt-1 text-sm text-mute">
            Partiels, concours, vacances : la série se met en pause jusqu&apos;à 4 semaines, sans rien perdre.
          </p>
          <div className="mt-3">
            <VacationForm until={progress.vacation?.end ?? null} />
          </div>
        </div>
      </section>

      <section aria-labelledby="goals" className="mt-12">
        <h2 id="goals" className="border-b border-hairline pb-2 font-bold">
          Mes objectifs
        </h2>
        {progress.goals.length === 0 ? (
          <p className="mt-3 text-mute">
            Aucun objectif en cours. Par exemple : « Partiel d&apos;algèbre linéaire : 10 exercices d&apos;ici le
            10 janvier », ou « Oraux : 3 exercices chronométrés par semaine ».
          </p>
        ) : (
          <ul className="mt-2 divide-y divide-hairline">
            {progress.goals.map((goal) => (
              <li key={goal.id} className="py-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-medium">{goal.title}</span>
                  <DeleteGoalButton goalId={goal.id} />
                </div>
                <p className="mt-2 font-mono tabular-nums">
                  {progressBar(goal.done, goal.target)} {goal.done} / {goal.target}
                  {goal.per_week && <span className="text-mute"> cette semaine</span>}
                </p>
                <p className="text-sm text-mute">
                  {goal.per_week ? "jusqu'au" : "d'ici le"} {day(goal.deadline)}
                  {goal.topic && ` · ${goal.topic}`}
                  {goal.done >= goal.target && " · atteint"}
                </p>
              </li>
            ))}
          </ul>
        )}
        <div className="mt-6 border-t border-hairline pt-6">
          <GoalForm topics={topics} />
        </div>
      </section>

      {progress.history.length > 0 && (
        <section aria-labelledby="history" className="mt-12">
          <h2 id="history" className="border-b border-hairline pb-2 font-bold">
            Semaines passées
          </h2>
          <ul className="mt-2 divide-y divide-hairline">
            {progress.history.map((week) => (
              <li key={week.week} className="flex flex-wrap items-center justify-between gap-2 py-2">
                <span>
                  <span className="text-mute">{STATUS_MARK[week.status]}</span>{" "}
                  {weekRange(week.week_start, plus(week.week_start, 6))}
                </span>
                <span className="text-sm text-mute">
                  {week.active_days} / {week.goal} · <Tag>{week.status_label}</Tag>
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
