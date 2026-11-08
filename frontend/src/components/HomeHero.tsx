import Link from "next/link";

import type { CourseNoteSummary, DailyChallenge, Leaderboard, Me, Progress } from "@/lib/api";
import { courseNotePath } from "@/lib/course-notes";
import { nextSkill } from "@/lib/home";
import { ordinal, plural } from "@/lib/labels";
import { PODIUM_TINTS } from "@/lib/profile-art";

import { Avatar } from "./Avatar";
import { primaryButtonClass, secondaryButtonClass } from "./Form";
import { Icon, type IconName } from "./Icon";
import { SearchBox } from "./SearchBox";
import { MathText } from "./MathText";

const DAY_LETTERS = ["L", "M", "M", "J", "V", "S", "D"];
const DAY_NAMES = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"];

const card = "rounded-2xl border border-hairline bg-surface-soft p-5";
const cardTitle = "font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-ink";
const pill = "rounded-full bg-surface-card px-2 py-px text-xs font-medium text-body";

/** La semaine en sept cases : pleine si active, cerclée pour aujourd'hui, pâle pour les jours à venir. */
function WeekSquares({ days }: { days: Progress["days"] }) {
  const today = days.findLastIndex((day) => !day.future);
  const active = days.flatMap((day, index) => (day.active ? [DAY_NAMES[index]] : []));
  return (
    <span
      role="img"
      aria-label={active.length ? `Jours actifs : ${active.join(", ")}` : "Aucun jour actif cette semaine"}
      className="mt-4 flex justify-between gap-1"
    >
      {days.map((day, index) => (
        <span
          key={day.date}
          className={`grid size-8 place-items-center rounded-lg text-[11px] font-semibold ${
            day.active ? "bg-ink text-canvas" : "bg-surface-card text-mute"
          } ${index === today ? "ring-[1.5px] ring-accent ring-offset-2 ring-offset-surface-soft" : ""}`}
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
      label: (
        <>
          Progresser en {skill.topic.toLowerCase()} avec « <MathText>{skill.next.title}</MathText> »
        </>
      ),
      detail: `Difficulté ${skill.next.difficulty}/5`,
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

/** En-tête de l'accueil d'un membre : la date, son niveau, et la recherche. */
export function MemberHeader({ me, levelName, today }: { me: Me; levelName: string | null; today: string }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
      <div>
        <p className="text-sm text-mute">
          {today}
          {levelName && ` · ${levelName}`}
        </p>
        <h1 id="accroche" className="mt-1 text-[2rem] sm:text-[2.25rem]">
          Bonjour, {me.username}.
        </h1>
      </div>
      <SearchBox id="recherche-accueil" className="w-full sm:w-[22rem]" />
    </header>
  );
}

/** Le défi du jour du niveau déclaré, s'il reste à relever. */
export function ChallengeCard({ challenge }: { challenge: DailyChallenge }) {
  return (
    <section aria-labelledby="defi" className="rounded-2xl border border-hairline bg-surface-soft px-5 py-6 sm:px-7">
      <div className="flex flex-wrap items-center gap-2.5 text-[13px] text-mute">
        <span className="grid size-7 place-items-center rounded-lg bg-accent-soft text-accent-text">
          <Icon name="timer" size={16} />
        </span>
        <h2 id="defi" className={cardTitle}>
          Défi du jour
        </h2>
        <span className={pill}>{challenge.level}</span>
        <span className={pill}>{challenge.minutes} minutes</span>
        <span className="sm:ml-auto">Ferme à minuit</span>
      </div>
      <p className="mt-4 font-serif text-[1.5rem] leading-snug text-ink-deep sm:text-[1.625rem]">
        <MathText>{challenge.exercise_title}</MathText>
      </p>
      <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-3">
        <Link href="/defi" className={`${primaryButtonClass} min-h-11 px-5`}>
          Commencer le défi
        </Link>
        <span className="text-sm text-body">
          Jusqu&apos;à <strong className="font-semibold text-ink-deep">{challenge.points_max} points</strong>, comptés
          quand ta copie est validée.
        </span>
      </div>
    </section>
  );
}

/** Ta semaine : jours actifs face à l'objectif, et la série en cours. */
export function WeekCard({ progress }: { progress: Progress }) {
  return (
    <section aria-labelledby="semaine" className={card}>
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="semaine" className={cardTitle}>
          Ta semaine
        </h2>
        <Link href="/progression" className="text-[13px] text-mute hover:text-ink">
          Progression →
        </Link>
      </div>
      <p className="mt-3.5 flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <span className="font-serif text-[2.125rem] leading-none text-ink-deep">
          {progress.active_days}/{progress.goal_days}
        </span>
        <span className="text-sm text-body">{progress.active_days > 1 ? "jours actifs" : "jour actif"}</span>
        {progress.achieved && (
          <span className="ml-auto inline-flex items-center gap-1 text-[13px] text-success">
            <Icon name="check" size={14} />
            objectif atteint
          </span>
        )}
      </p>
      <WeekSquares days={progress.days} />
      <p className="mt-3.5 text-[13px] text-mute">
        {progress.vacation ? (
          "Mode vacances : ta série est en pause."
        ) : progress.streak > 0 ? (
          <>
            Série de <strong className="font-semibold text-ink">{plural(progress.streak, "semaine")}</strong>.
          </>
        ) : (
          "Atteins ton objectif pour lancer une série."
        )}
      </p>
    </section>
  );
}

/** Ce qui attend le membre : relectures, prochain exercice de sa carte, notifications. */
export function TodoCard({ me, progress }: { me: Me; progress: Progress | null }) {
  const actions = actionsFor(me, progress);
  return (
    <section aria-labelledby="a-faire" className={card}>
      <h2 id="a-faire" className={cardTitle}>
        À faire
      </h2>
      {actions.length > 0 ? (
        <ul className="mt-2">
          {actions.map((action) => (
            <li key={action.href}>
              <Link href={action.href} className="-mx-2 flex gap-3 rounded-xl px-2 py-2.5 hover:bg-hover">
                <span
                  className={`grid size-8 shrink-0 place-items-center rounded-lg ${
                    action.urgent ? "bg-accent-soft text-accent-text" : "bg-surface-card text-body"
                  }`}
                >
                  <Icon name={action.icon} size={16} />
                </span>
                <span className="min-w-0 text-sm leading-snug">
                  <span className="text-ink">{action.label}</span>
                  {action.detail && (
                    <span className={`mt-0.5 block text-[13px] ${action.urgent ? "text-accent-text" : "text-mute"}`}>
                      {action.detail}
                    </span>
                  )}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-mute">
          Rien ne t&apos;attend. Choisis un exercice, ou{" "}
          <Link href="/exercices/nouveau" className="text-ink underline decoration-stone underline-offset-4">
            publies-en un
          </Link>
          .
        </p>
      )}
    </section>
  );
}

/** Les trois premiers de la semaine (ou de la précédente, `lastWeek`, tant que celle-ci est
 * vide) : on voit qui est actif, et on va voir leur profil. */
export function LeadersCard({ board, lastWeek = false }: { board: Leaderboard; lastWeek?: boolean }) {
  const leaders = board.top.slice(0, 3);
  const mine = board.me?.rank ?? null;
  return (
    <section aria-labelledby="cette-semaine" className={card}>
      <h2 id="cette-semaine" className={cardTitle}>
        {lastWeek ? "En tête la semaine dernière" : "En tête cette semaine"}
      </h2>
      {leaders.length > 0 ? (
        <ol className="mt-2">
          {leaders.map((entry) => (
            <li key={entry.username}>
              <Link
                href={`/membres/${encodeURIComponent(entry.username)}`}
                className="-mx-2 flex items-center gap-3 rounded-xl px-2 py-2 hover:bg-hover"
              >
                <span
                  aria-hidden="true"
                  className="grid size-5 shrink-0 place-items-center rounded-full text-[11px] font-semibold text-[#1c1c1c]"
                  style={{ background: PODIUM_TINTS[entry.rank - 1] ?? PODIUM_TINTS[2] }}
                >
                  {entry.rank}
                </span>
                <Avatar avatar={entry.avatar} size={32} />
                <span className="min-w-0 flex-1 truncate text-sm text-ink">
                  <span className="sr-only">{ordinal(entry.rank)} : </span>
                  {entry.username}
                  {entry.is_me && <span className="text-mute"> (toi)</span>}
                </span>
                <span className="shrink-0 text-sm tabular-nums text-body">
                  {entry.points}
                  <span className="text-mute"> pts</span>
                </span>
              </Link>
            </li>
          ))}
        </ol>
      ) : (
        <p className="mt-2 text-sm text-mute">Le podium est libre : personne n&apos;a encore marqué de points.</p>
      )}
      {mine !== null && mine > 3 && (
        <p className="mt-1 text-[13px] text-mute">
          Toi : {ordinal(mine)} sur {board.total}.
        </p>
      )}
      <Link
        href={lastWeek && board.week ? `/classements?semaine=${board.week}` : "/classements"}
        className="mt-2 inline-block text-[13px] text-mute underline underline-offset-4 hover:text-ink"
      >
        Voir le classement
      </Link>
    </section>
  );
}

/** Rappels de cours publiés, proches du fil : de quoi revoir le cours avant de chercher. */
export function CourseNotesCard({ notes }: { notes: CourseNoteSummary[] }) {
  return (
    <section aria-labelledby="cours" className={card}>
      <h2 id="cours" className={cardTitle}>
        Revoir le cours
      </h2>
      <p className="mb-2 mt-1 text-[13px] text-mute">Les rappels des notions de ton fil.</p>
      <ul>
        {notes.map((note) => (
          <li key={note.slug} className="border-t border-hairline">
            <Link
              href={courseNotePath(note.slug)}
              className="flex min-h-10 items-center justify-between gap-3 py-2 text-sm text-ink hover:text-ink-deep"
            >
              <span>{note.title}</span>
              <span className="shrink-0 text-[13px] text-mute">{note.programs}</span>
            </Link>
          </li>
        ))}
      </ul>
      <Link href="/rappels" className="mt-2 inline-block text-[13px] text-mute underline underline-offset-4 hover:text-ink">
        Tous les rappels
      </Link>
    </section>
  );
}

/** Accueil d'un visiteur : la promesse, et une action claire. */
export function VisitorHero() {
  return (
    <section aria-labelledby="accroche">
      {/* Le nom du site dans le titre : il aide les moteurs à associer « XiMaths » à ce site. */}
      <h1 id="accroche" className="max-w-[22ch]">
        XiMaths : des maths du supérieur, résolues et relues par la communauté.
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
    title: "Écris ta solution à la main.",
    text: "Puis photographie ta copie avec ton téléphone, en scannant un QR code : trois pages au plus.",
  },
  {
    title: "Trois pairs la corrigent.",
    text: "Tu lis leurs commentaires. S'ils la jugent tous juste, elle rapporte des points, des badges et une place au classement.",
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
