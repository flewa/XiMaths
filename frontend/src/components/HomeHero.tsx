import Link from "next/link";

import type { DailyChallenge, FeedItem, Me, Progress } from "@/lib/api";
import { nextSkill, openChallenge, weekLine } from "@/lib/home";
import { plural } from "@/lib/labels";

const surface = "-mx-4 bg-surface-dark px-4 text-on-dark sm:mx-0 sm:px-8";
const prompt = "rounded-sm bg-surface-dark-elevated px-3 py-2";
const quickLinks = "flex flex-wrap gap-x-6 text-sm text-on-dark-mute [&>a]:inline-block [&>a]:py-1 [&>a:hover]:text-on-dark";

function composition(feed: FeedItem[]) {
  const count = (reason: FeedItem["reason"]) => feed.filter((item) => item.reason === reason).length;
  return `${plural(count("tendance"), "tendance")} · ${count("a_resoudre")} à résoudre · ${count("exploration")} à découvrir`;
}

type Action = { marker: string; href: string; label: React.ReactNode; detail?: string };

function actionsFor(me: Me, progress: Progress | null, challenges: DailyChallenge[]): Action[] {
  const actions: Action[] = [];
  if (me.pending_reviews > 0) {
    actions.push({
      marker: "[!]",
      href: "/relectures",
      label: plural(me.pending_reviews, "relecture à rendre", "relectures à rendre"),
      detail: "relance à 48 h",
    });
  }
  const challenge = openChallenge(challenges, me.declared_level);
  if (challenge) {
    actions.push({
      marker: "[⏱]",
      href: "/defi",
      label: `Défi du jour ${challenge.level} : ${challenge.exercise_title}`,
      detail: `${challenge.minutes} min, jusqu'à minuit`,
    });
  }
  const skill = progress ? nextSkill(progress.skills) : null;
  if (skill?.next) {
    actions.push({
      marker: "[>]",
      href: `/exercices/${skill.next.id}`,
      label: `Pour progresser en ${skill.topic.toLowerCase()} : ${skill.next.title}`,
      detail: `difficulté\u00a0${skill.next.difficulty}`,
    });
  }
  if (me.unread_notifications > 0) {
    actions.push({
      marker: "[•]",
      href: "/notifications",
      label: plural(me.unread_notifications, "notification non lue", "notifications non lues"),
    });
  }
  return actions;
}

/** Accueil d'un membre : sa semaine, puis ce qui l'attend, du plus pressé au moins pressé. */
export function MemberHero({
  me,
  progress,
  challenges,
  level,
  browseHref,
}: {
  me: Me;
  progress: Progress | null;
  challenges: DailyChallenge[];
  level: string | undefined;
  browseHref: string;
}) {
  const actions = actionsFor(me, progress, challenges);
  return (
    <section aria-labelledby="accroche" className={`${surface} py-8 sm:py-10`}>
      <p className="text-sm text-on-dark-mute">
        ximaths ~ {me.username} {level ? `--niveau ${level}` : "--tous-niveaux"}
      </p>
      <h1 id="accroche" className="mt-2">
        Bonjour {me.username}.
      </h1>
      {progress && (
        <Link href="/progression" className={`${prompt} group mt-6 flex flex-wrap items-baseline gap-x-3`}>
          <span className="text-on-dark-mute">│ semaine</span>
          <span aria-hidden="true" className="tracking-widest">
            {weekLine(progress.days)}
          </span>
          <span>
            {progress.active_days}/{progress.goal_days} jours actifs
            {progress.streak > 0 && (
              <span className="text-on-dark-mute"> · série de {plural(progress.streak, "semaine")}</span>
            )}
          </span>
          <span aria-hidden="true" className="text-on-dark-mute group-hover:text-on-dark">
            →
          </span>
        </Link>
      )}
      <h2 className="sr-only">À faire</h2>
      {actions.length > 0 ? (
        <ul className="mt-4">
          {actions.map((action) => (
            <li key={action.href}>
              <Link
                href={action.href}
                className="-mx-3 flex gap-3 rounded-sm px-3 py-1.5 hover:bg-surface-dark-elevated"
              >
                <span aria-hidden="true" className="shrink-0 text-on-dark-mute">
                  {action.marker}
                </span>
                <span>
                  {action.label}
                  {action.detail && <span className="whitespace-nowrap text-on-dark-mute"> · {action.detail}</span>}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-on-dark-mute">[+] Rien ne t&apos;attend : choisis un exercice ci-dessous, ou publies-en un.</p>
      )}
      <p className={`mt-6 ${quickLinks}`}>
        <Link href="/exercices/nouveau">[+] publier un exercice</Link>
        <Link href={browseHref}>[&gt;] parcourir le catalogue</Link>
        <Link href="/progression">[~] ma progression</Link>
      </p>
    </section>
  );
}

/** Accueil d'un visiteur : la promesse, une action claire, et ce que contient le fil. */
export function VisitorHero({
  feed,
  level,
  browseHref,
}: {
  feed: FeedItem[];
  level: string | undefined;
  browseHref: string;
}) {
  return (
    <section aria-labelledby="accroche" className={`${surface} py-10 sm:py-14`}>
      <p className="text-sm text-on-dark-mute">ximaths ~ fil {level ? `--niveau ${level}` : "--tous-niveaux"}</p>
      <h1 id="accroche" className="mt-3 max-w-[30ch]">
        Des maths du supérieur, résolues et relues par la communauté.
      </h1>
      <p className="mt-4 max-w-[60ch] text-on-dark-mute">
        De la L1 au M2 et en prépa : publie des exercices, propose tes solutions, et fais-les relire par trois
        pairs tirés au sort.
      </p>
      <p className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-3">
        <Link
          href="/inscription"
          className="inline-block min-h-9 rounded-sm bg-on-dark px-5 py-1 font-medium leading-7 text-surface-dark"
        >
          Créer un compte
        </Link>
        <Link href="/connexion" className="inline-block py-1 underline underline-offset-4">
          J&apos;ai déjà un compte
        </Link>
      </p>
      <p className={`mt-8 ${prompt}`}>
        <span className="text-on-dark-mute">│ </span>
        {feed.length === 0 ? "aucun exercice à ce niveau pour l'instant" : composition(feed)}
      </p>
      <p className={`mt-4 ${quickLinks}`}>
        <Link href={browseHref}>[&gt;] parcourir le catalogue</Link>
        <Link href="/defi">[⏱] défi du jour</Link>
        <Link href="/classements">[#] classements</Link>
      </p>
    </section>
  );
}

const STEPS = [
  {
    title: "Choisis un exercice",
    text: "Un fil par niveau, de la L1 au M2 et en prépa, avec les exercices qui attendent leur première solution.",
  },
  {
    title: "Rédige ta solution",
    text: "En Markdown et LaTeX, avec l'aperçu en direct, ou en photographiant ta copie manuscrite.",
  },
  {
    title: "Trois pairs la relisent",
    text: "Validée, elle rapporte des points, des badges et une place au classement de la semaine.",
  },
];

export function HowItWorks() {
  return (
    <section aria-labelledby="comment" className="mt-10">
      <h2 id="comment" className="sr-only">
        Comment ça marche
      </h2>
      <ol className="grid border-y border-hairline sm:grid-cols-3">
        {STEPS.map((step, index) => (
          <li
            key={step.title}
            className="border-t border-hairline py-4 first:border-t-0 sm:border-l sm:border-t-0 sm:px-4 sm:first:border-l-0 sm:first:pl-0"
          >
            <p className="font-bold">
              <span className="text-stone">[{index + 1}]</span> {step.title}
            </p>
            <p className="mt-1 text-sm text-body">{step.text}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
