import Link from "next/link";

import type { DailyChallenge, Me, Progress } from "@/lib/api";
import { nextSkill, openChallenge } from "@/lib/home";
import { plural } from "@/lib/labels";

import { primaryButtonClass, secondaryButtonClass } from "./Form";
import { Icon, type IconName } from "./Icon";

const DAY_LETTERS = ["L", "M", "M", "J", "V", "S", "D"];
const DAY_NAMES = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"];

/** La semaine en sept cases : pleine si active, cerclée pour aujourd'hui, pâle pour les jours à venir. */
function WeekSquares({ days }: { days: Progress["days"] }) {
  const today = days.findLastIndex((day) => !day.future);
  const active = days.flatMap((day, index) => (day.active ? [DAY_NAMES[index]] : []));
  return (
    <span
      role="img"
      aria-label={active.length ? `Jours actifs : ${active.join(", ")}` : "Aucun jour actif cette semaine"}
      className="flex gap-1.5"
    >
      {days.map((day, index) => (
        <span
          key={day.date}
          className={`grid size-[22px] place-items-center rounded-md text-[10px] font-semibold ${
            day.active
              ? "bg-ink text-canvas"
              : index === today
                ? "text-ink ring-[1.5px] ring-mute ring-inset"
                : "bg-surface-card text-stone"
          }`}
        >
          {DAY_LETTERS[index]}
        </span>
      ))}
    </span>
  );
}

type Action = { icon: IconName; href: string; label: React.ReactNode; detail?: string; urgent?: boolean };

function actionsFor(me: Me, progress: Progress | null): Action[] {
  const actions: Action[] = [];
  if (me.pending_reviews > 0) {
    actions.push({
      icon: "review",
      href: "/relectures",
      label: `Rendre ${plural(me.pending_reviews, "relecture")}`,
      detail: "relance à 48 h",
      urgent: true,
    });
  }
  const skill = progress ? nextSkill(progress.skills) : null;
  if (skill?.next) {
    actions.push({
      icon: "chart",
      href: `/exercices/${skill.next.id}`,
      label: `Progresser en ${skill.topic.toLowerCase()} avec « ${skill.next.title} »`,
      detail: `difficulté ${skill.next.difficulty}`,
    });
  }
  if (me.unread_notifications > 0) {
    actions.push({
      icon: "bell",
      href: "/notifications",
      label: `Lire ${plural(me.unread_notifications, "notification")}`,
    });
  }
  return actions;
}

/** Le défi du jour, mis en page comme un énoncé de manuel : tête en gras, filet à gauche. */
function ChallengeBlock({ challenge }: { challenge: DailyChallenge }) {
  return (
    <section aria-labelledby="defi" className="mt-10 rounded-r-xl border-l-2 border-accent bg-surface-soft px-5 py-5 sm:px-6">
      <p id="defi" className="font-serif text-xl text-ink-deep">
        <b className="font-bold">Défi du jour.</b>{" "}
        <span className="ml-1 font-sans text-sm text-mute">
          {challenge.level}, {challenge.minutes} minutes
        </span>
      </p>
      <p className="mt-2 font-serif text-2xl text-ink-deep">{challenge.exercise_title}</p>
      <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-3">
        <Link href="/defi" className={primaryButtonClass}>
          <Icon name="timer" size={16} />
          Commencer le défi
        </Link>
        <span className="text-sm text-mute">
          Jusqu&apos;à {challenge.points_max} points, ouvert jusqu&apos;à minuit.
        </span>
      </div>
    </section>
  );
}

/** Accueil d'un membre : sa semaine, le défi du jour, puis ce qui l'attend. */
export function MemberHero({
  me,
  progress,
  challenges,
}: {
  me: Me;
  progress: Progress | null;
  challenges: DailyChallenge[];
}) {
  const actions = actionsFor(me, progress);
  const challenge = openChallenge(challenges, me.declared_level);
  return (
    <>
      <section aria-labelledby="accroche">
        <h1 id="accroche">Bonjour, {me.username}.</h1>
        {progress && (
          <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-3 text-mute">
            <WeekSquares days={progress.days} />
            <p>
              <strong className="font-medium text-ink">
                {progress.active_days} {progress.active_days > 1 ? "jours" : "jour"} sur {progress.goal_days}
              </strong>{" "}
              cette semaine
              {progress.streak > 0 && <>, série de {plural(progress.streak, "semaine")}</>}.{" "}
              <Link href="/progression" className="underline decoration-stone underline-offset-4 hover:text-ink">
                Ta progression
              </Link>
            </p>
          </div>
        )}
      </section>

      {challenge && <ChallengeBlock challenge={challenge} />}

      <section aria-labelledby="a-faire" className="mt-12">
        <h2 id="a-faire">À faire</h2>
        {actions.length > 0 ? (
          <ul className="mt-3">
            {actions.map((action) => (
              <li key={action.href}>
                <Link
                  href={action.href}
                  className="-mx-3 flex items-center gap-3.5 rounded-lg px-3 py-2.5 hover:bg-hover"
                >
                  <Icon name={action.icon} className={action.urgent ? "text-accent-text" : "text-mute"} />
                  <span className="min-w-0 flex-1">{action.label}</span>
                  {action.detail && (
                    <span className={`hidden whitespace-nowrap text-sm sm:inline ${action.urgent ? "text-accent-text" : "text-mute"}`}>
                      {action.detail}
                    </span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-mute">
            Rien ne t&apos;attend. Choisis un exercice ci-dessous, ou{" "}
            <Link href="/exercices/nouveau" className="text-ink underline decoration-stone underline-offset-4">
              publies-en un
            </Link>
            .
          </p>
        )}
      </section>
    </>
  );
}

/** Accueil d'un visiteur : la promesse, et une action claire. */
export function VisitorHero() {
  return (
    <section aria-labelledby="accroche">
      <h1 id="accroche" className="max-w-[20ch]">
        Des maths du supérieur, résolues et relues par la communauté.
      </h1>
      <p className="mt-5 max-w-[58ch] text-lg text-body">
        De la L1 au M2 et en prépa : publie des exercices, propose tes solutions, et fais-les relire par trois
        pairs tirés au sort.
      </p>
      <p className="mt-8 flex flex-wrap items-center gap-3">
        <Link href="/inscription" className={primaryButtonClass}>
          Créer un compte
        </Link>
        <Link href="/connexion" className={secondaryButtonClass}>
          J&apos;ai déjà un compte
        </Link>
      </p>
    </section>
  );
}

const STEPS = [
  {
    title: "Choisis un exercice.",
    text: "Un fil par niveau, de la L1 au M2 et en prépa, avec les exercices qui attendent leur première solution.",
  },
  {
    title: "Rédige ta solution.",
    text: "En Markdown et LaTeX, avec l'aperçu en direct, ou en photographiant ta copie manuscrite.",
  },
  {
    title: "Trois pairs la relisent.",
    text: "Validée, elle rapporte des points, des badges et une place au classement de la semaine.",
  },
];

export function HowItWorks() {
  return (
    <section aria-labelledby="comment" className="mt-14">
      <h2 id="comment">Comment ça marche</h2>
      <ol className="mt-5 grid gap-6 sm:grid-cols-3">
        {STEPS.map((step, index) => (
          <li key={step.title}>
            <p className="font-serif text-lg text-ink-deep">
              <span className="text-accent-text">{index + 1}.</span> <b className="font-bold">{step.title}</b>
            </p>
            <p className="mt-1.5 text-[15px] text-mute">{step.text}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
