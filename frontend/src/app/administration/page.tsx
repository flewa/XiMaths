import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { SolutionDecision } from "@/components/AdminActions";
import { VolunteerButton } from "@/components/ContributionForms";
import { CopyPhotoList } from "@/components/CopyPhotos";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { FilterChip, Tabs } from "@/components/FilterChip";
import { inputClass, secondaryButtonClass } from "@/components/Form";
import { MathText } from "@/components/MathText";
import { Tag } from "@/components/Tag";
import {
  type PanelDay,
  type PanelExercise,
  type PanelMember,
  type PanelOverview,
  type PanelReview,
  type PanelSolution,
  fetchMe,
  fetchPanelExercises,
  fetchPanelMembers,
  fetchPanelOverview,
  fetchPanelSolutions,
} from "@/lib/api";
import { dateFormat, plural } from "@/lib/labels";

export const metadata: Metadata = { title: "Administration", robots: { index: false } };

const VIEWS = [
  { value: "apercu", label: "Vue d'ensemble" },
  { value: "copies", label: "Copies" },
  { value: "membres", label: "Membres" },
  { value: "exercices", label: "Exercices" },
] as const;
type View = (typeof VIEWS)[number]["value"];

const FILTERS: Record<Exclude<View, "apercu">, { value: string; label: string }[]> = {
  copies: [
    { value: "", label: "Toutes" },
    { value: "under_review", label: "En relecture" },
    { value: "late", label: "En retard" },
    { value: "validated", label: "Validées" },
    { value: "needs_work", label: "À reprendre" },
    { value: "hidden", label: "Masquées" },
  ],
  membres: [
    { value: "", label: "Tous" },
    { value: "team", label: "Équipe" },
    { value: "sanctioned", label: "Suspendus ou bannis" },
    { value: "unverified", label: "Adresse non vérifiée" },
  ],
  exercices: [
    { value: "", label: "Tous" },
    { value: "published", label: "Publiés" },
    { value: "unsolved", label: "Sans copie validée" },
    { value: "draft", label: "Brouillons" },
    { value: "removed", label: "Retirés" },
    { value: "merged", label: "Fusionnés" },
  ],
};

const VERDICT_STYLES: Record<string, string> = {
  correcte: "text-success",
  lacunes: "text-warning",
  incorrecte: "text-danger-text",
};

const shortDay = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short", timeZone: "UTC" });

function day(iso: string | null) {
  return iso ? dateFormat.format(new Date(iso)) : "—";
}

function waiting(hours: number) {
  if (hours < 1) return "depuis moins d'une heure";
  if (hours < 48) return `depuis ${hours} h`;
  return `depuis ${Math.floor(hours / 24)} jours`;
}

/** Adresse du panneau pour cette vue, ce filtre, cette recherche et cette page. */
function href(view: View, params: { statut?: string; q?: string; page?: number } = {}) {
  const query = new URLSearchParams();
  if (view !== "apercu") query.set("vue", view);
  if (params.statut) query.set("statut", params.statut);
  if (params.q) query.set("q", params.q);
  if (params.page && params.page > 1) query.set("page", String(params.page));
  const text = query.toString();
  return text ? `/administration?${text}` : "/administration";
}

function memberHref(username: string) {
  return `/moderation/membres/${encodeURIComponent(username)}`;
}

// ---------------------------------------------------------------- vue d'ensemble

/** Une colonne par jour, sur 14 jours. Une seule teinte, neutre : le corail reste réservé à
 * ce qui attend une action. La valeur de chaque jour se lit au survol, au clavier, et dans
 * le tableau sous les tuiles. */
function DayBars({ days, pick, unit }: { days: PanelDay[]; pick: (day: PanelDay) => number; unit: string }) {
  const max = Math.max(1, ...days.map(pick));
  return (
    <div className="mt-3 flex h-14 items-end gap-0.5">
      {days.map((item, index) => {
        const value = pick(item);
        const date = shortDay.format(new Date(item.date));
        const side = index < 3 ? "left-0" : index > days.length - 4 ? "right-0" : "left-1/2 -translate-x-1/2";
        return (
          <div
            key={item.date}
            role="img"
            tabIndex={0}
            aria-label={`${date} : ${value} ${unit}`}
            className="group relative flex h-full min-w-0 flex-1 items-end justify-center outline-none"
          >
            <span
              className={`block w-full max-w-6 group-hover:bg-ink-deep group-focus-visible:bg-ink-deep ${
                value === 0 ? "h-0.5 bg-hairline-strong" : "rounded-t-[4px] bg-body"
              }`}
              style={value === 0 ? undefined : { height: `${Math.max(8, (value / max) * 100)}%` }}
            />
            <span
              className={`pointer-events-none absolute bottom-full z-10 mb-1 hidden whitespace-nowrap rounded-md border border-hairline bg-surface-card px-2 py-1 text-xs text-body shadow-lg group-hover:block group-focus-visible:block ${side}`}
            >
              <strong className="font-semibold text-ink-deep">{value}</strong> · {date}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function Figure({ value, label, note }: { value: number; label: string; note?: string }) {
  return (
    <div className="flex flex-col-reverse justify-end rounded-2xl bg-surface-soft px-4 py-3">
      <dt className="text-sm text-mute">
        {label}
        {note && <span className="block text-[13px]">{note}</span>}
      </dt>
      <dd className="font-serif text-[1.75rem] leading-tight text-ink-deep tabular-nums">{value}</dd>
    </div>
  );
}

function Overview({ data }: { data: PanelOverview }) {
  const todo = [
    data.late > 0 && {
      href: href("copies", { statut: "late" }),
      text: `${plural(data.late, "copie attend", "copies attendent")} une correction depuis plus de 3 jours`,
      action: "Les corriger",
    },
    data.moderation_pending > 0 && {
      href: "/moderation",
      text: `${plural(data.moderation_pending, "décision attend", "décisions attendent")} en modération`,
      action: "Ouvrir la modération",
    },
  ].filter((item): item is { href: string; text: string; action: string } => Boolean(item));
  const series = [
    { title: "Inscriptions", unit: "inscriptions", pick: (item: PanelDay) => item.signups },
    { title: "Copies envoyées", unit: "copies", pick: (item: PanelDay) => item.solutions },
    { title: "Relectures rendues", unit: "relectures", pick: (item: PanelDay) => item.reviews },
  ];
  return (
    <>
      <section aria-labelledby="a-traiter" className="mt-8">
        <h2 id="a-traiter">À traiter</h2>
        {todo.length === 0 ? (
          <p className="mt-3 rounded-2xl bg-surface-soft px-5 py-4 text-body">
            Rien n&apos;attend : aucune copie en retard, aucune décision de modération en attente.
          </p>
        ) : (
          <ul className="mt-3 grid gap-3 sm:grid-cols-2">
            {todo.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="flex h-full flex-col gap-2 rounded-2xl border border-accent bg-surface-soft px-5 py-4 hover:bg-hover"
                >
                  <span className="text-ink">{item.text}</span>
                  <span className="text-sm font-medium text-accent-text">{item.action} →</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="copies-chiffres" className="mt-10">
        <h2 id="copies-chiffres">Copies</h2>
        <dl className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Figure value={data.under_review} label="en relecture" note={data.late > 0 ? `dont ${data.late} en retard` : undefined} />
          <Figure value={data.validated} label="validées" />
          <Figure value={data.needs_work} label="à reprendre" />
          <Figure value={data.hidden} label="masquées" />
        </dl>
        <p className="mt-3 text-sm">
          <Link href={href("copies")} className="text-mute underline underline-offset-4 hover:text-ink">
            Voir toutes les copies
          </Link>
        </p>
      </section>

      <section aria-labelledby="site-chiffres" className="mt-10">
        <h2 id="site-chiffres">Le site</h2>
        <dl className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Figure value={data.members} label="membres" note={`+${data.members_week} en 7 jours`} />
          <Figure value={data.members_active_week} label="actifs en 7 jours" />
          <Figure value={data.reviewers} label={data.reviewers > 1 ? "relecteurs" : "relecteur"} note="peuvent être tirés au sort" />
          <Figure value={data.exercises} label="exercices publiés" note={`+${data.exercises_week} en 7 jours`} />
        </dl>
      </section>

      <section aria-labelledby="activite" className="mt-10">
        <h2 id="activite">Activité des 14 derniers jours</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          {series.map((serie) => (
            <div key={serie.title} className="rounded-2xl bg-surface-soft px-4 py-3">
              <p className="flex items-baseline justify-between gap-2">
                <span className="text-sm text-mute">{serie.title}</span>
                <span className="font-serif text-xl text-ink-deep tabular-nums">
                  {data.days.reduce((total, item) => total + serie.pick(item), 0)}
                </span>
              </p>
              <DayBars days={data.days} pick={serie.pick} unit={serie.unit} />
              <p className="mt-1 flex justify-between text-xs text-mute">
                <span>{shortDay.format(new Date(data.days[0].date))}</span>
                <span>{shortDay.format(new Date(data.days[data.days.length - 1].date))}</span>
              </p>
            </div>
          ))}
        </div>
        <details className="mt-3 text-sm">
          <summary className="text-mute hover:text-ink">Voir les chiffres jour par jour</summary>
          <div className="mt-2 overflow-x-auto">
            <table className="w-full min-w-[420px] text-left tabular-nums">
              <thead className="text-mute">
                <tr>
                  <th className="py-1.5 font-medium">Jour</th>
                  <th className="py-1.5 text-right font-medium">Inscriptions</th>
                  <th className="py-1.5 text-right font-medium">Copies envoyées</th>
                  <th className="py-1.5 text-right font-medium">Relectures rendues</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hairline border-y border-hairline text-body">
                {[...data.days].reverse().map((item) => (
                  <tr key={item.date}>
                    <td className="py-1.5">{shortDay.format(new Date(item.date))}</td>
                    <td className="py-1.5 text-right">{item.signups}</td>
                    <td className="py-1.5 text-right">{item.solutions}</td>
                    <td className="py-1.5 text-right">{item.reviews}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
        <p className="mt-3 text-sm text-mute">
          Sur 7 jours : {plural(data.solutions_week, "copie envoyée", "copies envoyées")},{" "}
          {plural(data.reviews_week, "relecture rendue", "relectures rendues")},{" "}
          {plural(data.messages_week, "message", "messages")} sous les exercices.
        </p>
      </section>
    </>
  );
}

// ---------------------------------------------------------------- listes

function Toolbar({
  view,
  statut,
  q,
  placeholder,
}: {
  view: Exclude<View, "apercu">;
  statut: string;
  q: string;
  placeholder: string;
}) {
  return (
    <>
      <Tabs label="Filtrer" className="mt-6">
        {FILTERS[view].map((filter) => (
          <FilterChip key={filter.value} href={href(view, { statut: filter.value, q })} label={filter.label} active={statut === filter.value} />
        ))}
      </Tabs>
      <form action="/administration" role="search" className="mt-4 flex max-w-md gap-2">
        <input type="hidden" name="vue" value={view} />
        {statut && <input type="hidden" name="statut" value={statut} />}
        <label htmlFor="recherche-panneau" className="sr-only">
          {placeholder}
        </label>
        <input id="recherche-panneau" name="q" type="search" defaultValue={q} placeholder={placeholder} className={inputClass} />
        <button type="submit" className={secondaryButtonClass}>
          Chercher
        </button>
      </form>
    </>
  );
}

function Pager({ view, statut, q, page, pages }: { view: View; statut: string; q: string; page: number; pages: number }) {
  if (pages <= 1) return null;
  const link = "rounded-lg bg-surface-card px-3 py-1.5 text-ink hover:bg-surface-dark-elevated";
  return (
    <nav aria-label="Pages" className="mt-6 flex items-center gap-3 text-sm">
      {page > 1 && (
        <Link href={href(view, { statut, q, page: page - 1 })} className={link}>
          ← Précédente
        </Link>
      )}
      <span className="text-mute tabular-nums">
        Page {page} sur {pages}
      </span>
      {page < pages && (
        <Link href={href(view, { statut, q, page: page + 1 })} className={link}>
          Suivante →
        </Link>
      )}
    </nav>
  );
}

function ReviewLine({ review }: { review: PanelReview }) {
  const state = review.submitted_at ? (
    <span className={VERDICT_STYLES[review.verdict] ?? "text-body"}>{review.verdict_label}</span>
  ) : review.expired ? (
    <span className="text-mute">non rendue, réattribuée</span>
  ) : (
    <span className="text-mute">en attente depuis le {day(review.assigned_at)}</span>
  );
  return (
    <li className="rounded-xl bg-surface-soft px-3 py-2 text-sm">
      <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <Link href={memberHref(review.reviewer)} className="font-medium text-ink hover:underline">
          {review.reviewer}
        </Link>
        <span className="text-mute">{review.team ? "équipe, décisive" : review.assigned ? "tiré au sort" : "volontaire"}</span>
        <span aria-hidden="true" className="text-mute">
          ·
        </span>
        {state}
      </p>
      {review.feedback && <p className="mt-1 whitespace-pre-line text-body">{review.feedback}</p>}
    </li>
  );
}

function SolutionRow({ solution, me }: { solution: PanelSolution; me: string }) {
  const inReview = solution.status === "under_review";
  // Une relecture de l'administrateur est déjà ouverte sur cette copie.
  const mine = inReview && solution.reviews.some((review) => review.reviewer === me && !review.submitted_at && !review.expired);
  return (
    <li className="py-4">
      <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-1.5">
        <p className="min-w-0 flex-1 basis-64 font-medium">
          <Link href={`/exercices/${solution.exercise_id}`} className="text-ink hover:underline">
            <MathText>{solution.exercise_title}</MathText>
          </Link>
        </p>
        <span className="flex flex-wrap items-center gap-2 text-sm">
          {solution.points > 0 && <span className="tabular-nums text-ink">+{solution.points} points</span>}
          {solution.late && <Tag strong>En retard</Tag>}
          <Tag strong={inReview && !solution.late}>{solution.status_label}</Tag>
        </span>
      </div>
      <p className="mt-1 flex flex-wrap gap-x-2 gap-y-0.5 text-sm text-mute">
        <span>
          par{" "}
          {solution.author ? (
            <Link href={memberHref(solution.author)} className="text-ink hover:underline">
              {solution.author}
            </Link>
          ) : (
            "un compte supprimé"
          )}
        </span>
        <span>· {solution.origin_label.toLowerCase()}</span>
        <span>· envoyée le {day(solution.published_at)}</span>
        {inReview && solution.waiting_hours !== null && <span>· en relecture {waiting(solution.waiting_hours)}</span>}
        {solution.validated_at && <span>· validée le {day(solution.validated_at)}</span>}
        {solution.review_round > 1 && <span>· tour {solution.review_round}</span>}
        {solution.ai_usage !== "aucune" && <span>· IA : {solution.ai_usage_label.toLowerCase()}</span>}
        {solution.is_model && <span>· copie modèle</span>}
        {solution.after_model && <span>· sans points (envoyée après la copie modèle)</span>}
      </p>
      <details className="mt-2">
        <summary className="text-sm text-mute hover:text-ink">
          Relectures : {solution.reviews_done} sur {solution.reviews_expected} · voir la copie
        </summary>
        <CopyPhotoList photos={solution.photos} compact />
        {solution.reviews.length === 0 ? (
          <p className="mt-2 text-sm text-mute">Aucun relecteur n&apos;a encore été trouvé pour cette copie.</p>
        ) : (
          <ul className="mt-2 space-y-1.5">
            {solution.reviews.map((review) => (
              <ReviewLine key={`${review.reviewer}-${review.assigned_at}`} review={review} />
            ))}
          </ul>
        )}
      </details>
      {solution.can_take && (
        <p className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-mute">
          <VolunteerButton solutionId={solution.id} label="La corriger moi-même" />
          <span>Ta relecture vaut décision ; la copie t&apos;attend ensuite dans Relectures.</span>
        </p>
      )}
      {solution.author && solution.author !== me && <SolutionDecision id={solution.id} status={solution.status} />}
      {mine && (
        <p className="mt-3 text-sm text-mute">
          Elle attend ta correction, qui vaut décision :{" "}
          <Link href="/relectures" className="text-accent-text underline underline-offset-4">
            la corriger dans Relectures
          </Link>
        </p>
      )}
    </li>
  );
}

const th = "whitespace-nowrap py-2 pr-4 font-medium";
const td = "py-2 pr-4 align-top";
const num = `${td} text-right tabular-nums`;

function MembersTable({ members }: { members: PanelMember[] }) {
  return (
    <div className="mt-4 overflow-x-auto">
      <table className="w-full min-w-[820px] text-left text-sm">
        <thead className="text-mute">
          <tr>
            <th className={th}>Membre</th>
            <th className={th}>Inscrit le</th>
            <th className={th}>Statut</th>
            <th className={`${th} text-right`}>Points</th>
            <th className={`${th} text-right`}>Exercices</th>
            <th className={`${th} text-right`}>Copies validées</th>
            <th className={`${th} text-right`}>Relectures</th>
            <th className={th}>Dernière connexion</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-hairline border-y border-hairline text-body">
          {members.map((member) => (
            <tr key={member.username}>
              <td className={td}>
                <Link href={memberHref(member.username)} className="font-medium text-ink hover:underline">
                  {member.username}
                </Link>
                <span className="block text-[13px] text-mute">
                  {member.is_staff ? "Administrateur" : member.trust_label}
                  {!member.email_verified && " · adresse non vérifiée"}
                </span>
              </td>
              <td className={`${td} whitespace-nowrap`}>{day(member.joined_at)}</td>
              <td className={td}>{member.status === "active" ? "Actif" : <Tag strong>{member.status_label}</Tag>}</td>
              <td className={num}>{member.points}</td>
              <td className={num}>{member.exercises}</td>
              <td className={num}>
                {member.validated} <span className="text-mute">sur {member.solutions}</span>
              </td>
              <td className={num}>{member.reviews}</td>
              <td className={`${td} whitespace-nowrap`}>{member.last_login ? day(member.last_login) : "jamais"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ExercisesTable({ exercises }: { exercises: PanelExercise[] }) {
  return (
    <div className="mt-4 overflow-x-auto">
      <table className="w-full min-w-[860px] text-left text-sm">
        <thead className="text-mute">
          <tr>
            <th className={th}>Exercice</th>
            <th className={th}>Niveau</th>
            <th className={th}>Statut</th>
            <th className={`${th} text-right`}>Lu par</th>
            <th className={`${th} text-right`}>Copies validées</th>
            <th className={`${th} text-right`}>En relecture</th>
            <th className={`${th} text-right`}>Messages</th>
            <th className={th}>Publié le</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-hairline border-y border-hairline text-body">
          {exercises.map((exercise) => (
            <tr key={exercise.id}>
              <td className={`${td} max-w-[320px]`}>
                {exercise.status === "published" ? (
                  <Link href={`/exercices/${exercise.id}`} className="font-medium text-ink hover:underline">
                    <MathText>{exercise.title}</MathText>
                  </Link>
                ) : (
                  <span className="font-medium text-ink">
                    <MathText>{exercise.title}</MathText>
                  </span>
                )}
                <span className="block text-[13px] text-mute">
                  {exercise.author ? `par ${exercise.author}` : "auteur supprimé"} · difficulté {exercise.difficulty}/5 ·{" "}
                  <Link href={`/administration/exercices/${exercise.id}`} className="text-ink underline underline-offset-4">
                    Modifier
                  </Link>
                </span>
              </td>
              <td className={td}>{exercise.primary_level}</td>
              <td className={td}>{exercise.status === "published" ? "Publié" : <Tag>{exercise.status_label}</Tag>}</td>
              <td className={num}>{exercise.readers}</td>
              <td className={num}>
                {exercise.validated} <span className="text-mute">sur {exercise.solutions}</span>
              </td>
              <td className={num}>{exercise.under_review}</td>
              <td className={num}>{exercise.messages}</td>
              <td className={`${td} whitespace-nowrap`}>{day(exercise.published_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <p className="mt-6 rounded-2xl bg-surface-soft px-5 py-4 text-body">{children}</p>;
}

// ---------------------------------------------------------------- page

export default async function AdministrationPage({
  searchParams,
}: {
  searchParams: Promise<{ vue?: string; statut?: string; q?: string; page?: string }>;
}) {
  const params = await searchParams;
  const view: View = VIEWS.some((item) => item.value === params.vue) ? (params.vue as View) : "apercu";
  const q = params.q?.trim() ?? "";
  const page = Math.max(1, Number.parseInt(params.page ?? "1", 10) || 1);
  // Un filtre inconnu (adresse tapée à la main) vaut « tout ».
  const statut = view !== "apercu" && FILTERS[view].some((filter) => filter.value === params.statut) ? (params.statut ?? "") : "";

  let data;
  try {
    const [me, overview, solutions, members, exercises] = await Promise.all([
      fetchMe(),
      view === "apercu" ? fetchPanelOverview() : null,
      view === "copies" ? fetchPanelSolutions({ status: statut, q, page }) : null,
      view === "membres" ? fetchPanelMembers({ show: statut, q, page }) : null,
      view === "exercices" ? fetchPanelExercises({ status: statut, q, page }) : null,
    ]);
    data = { me, overview, solutions, members, exercises };
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const { me, overview, solutions, members, exercises } = data;
  if (!me) redirect("/connexion?suivant=/administration");
  // Réservé aux administrateurs : pour les autres, la page n'existe pas.
  if (!me.is_staff) notFound();

  return (
    <div className="page-wide">
      <h1>Administration</h1>
      <p className="mt-2 max-w-[70ch] text-body">
        Tout ce qui se passe sur le site, et la main dessus : décider d&apos;une copie, corriger ou retirer un exercice,
        gérer un compte depuis sa fiche (un clic sur un pseudo). Chaque action demande un motif, prévient la personne
        concernée et s&apos;inscrit au{" "}
        <Link href="/moderation?file=journal" className="underline underline-offset-4">
          journal
        </Link>
        .
      </p>

      <Tabs label="Vues du panneau" className="mt-8">
        {VIEWS.map((item) => (
          <FilterChip key={item.value} href={href(item.value)} label={item.label} active={view === item.value} />
        ))}
      </Tabs>

      {overview && <Overview data={overview} />}

      {solutions && (
        <>
          <Toolbar view="copies" statut={statut} q={q} placeholder="Chercher un exercice ou un pseudo" />
          <p className="mt-5 text-sm text-mute">{plural(solutions.total, "copie")}</p>
          {solutions.items.length === 0 ? (
            <Empty>Aucune copie ne correspond.</Empty>
          ) : (
            <ul className="mt-2 divide-y divide-hairline border-y border-hairline">
              {solutions.items.map((solution) => (
                <SolutionRow key={solution.id} solution={solution} me={me.username} />
              ))}
            </ul>
          )}
          <Pager view="copies" statut={statut} q={q} page={solutions.page} pages={solutions.pages} />
        </>
      )}

      {members && (
        <>
          <Toolbar view="membres" statut={statut} q={q} placeholder="Chercher un pseudo" />
          <p className="mt-5 text-sm text-mute">
            {plural(members.total, "membre")}. Un clic sur un pseudo ouvre sa fiche de modération.
          </p>
          {members.items.length === 0 ? <Empty>Aucun membre ne correspond.</Empty> : <MembersTable members={members.items} />}
          <Pager view="membres" statut={statut} q={q} page={members.page} pages={members.pages} />
        </>
      )}

      {exercises && (
        <>
          <Toolbar view="exercices" statut={statut} q={q} placeholder="Chercher un titre ou un auteur" />
          <p className="mt-5 text-sm text-mute">{plural(exercises.total, "exercice")}</p>
          {exercises.items.length === 0 ? <Empty>Aucun exercice ne correspond.</Empty> : <ExercisesTable exercises={exercises.items} />}
          <Pager view="exercices" statut={statut} q={q} page={exercises.page} pages={exercises.pages} />
        </>
      )}
    </div>
  );
}
