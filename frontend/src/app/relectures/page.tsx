import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ReviewForm, VolunteerButton } from "@/components/ContributionForms";
import { ReportButton } from "@/components/ReportButton";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { CopyPhotoList, ExpectedAnswer } from "@/components/CopyPhotos";
import { MathMarkdown } from "@/components/MathMarkdown";
import { ProseSection } from "@/components/Prose";
import { Tag } from "@/components/Tag";
import { fetchMe, fetchOpenSolutions, fetchReviewTasks } from "@/lib/api";
import { AI_USAGE_BADGES, dueLabel, plural } from "@/lib/labels";
import { MathText } from "@/components/MathText";
import { PageIntro } from "@/components/PageIntro";

export const metadata: Metadata = { title: "Relectures", robots: { index: false } };

// Niveau de confiance à partir duquel on est tiré au sort pour relire.
const REVIEWER_TRUST_LEVEL = 2;
// Niveau Expert : il évalue les réponses aux questions de compréhension.
const EXPERT_TRUST_LEVEL = 3;
const MODERATOR_TRUST_LEVEL = 4;
// Au-delà, une copie attend trop : l'équipe est prévenue.
const LATE_HOURS = 72;
// Moins de 12 heures avant l'échéance : elle s'affiche en corail.
const SOON_MS = 12 * 3_600_000;

function waiting(hours: number) {
  if (hours < 1) return "à l'instant";
  if (hours < 24) return `depuis ${hours} h`;
  const days = Math.floor(hours / 24);
  return `depuis ${days} jour${days > 1 ? "s" : ""}`;
}

export default async function ReviewsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchReviewTasks(), fetchOpenSolutions()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, tasks, open] = data;
  if (!me) redirect("/connexion?suivant=/relectures");
  // L'équipe du site : sa relecture vaut décision, et elle voit toutes les copies en attente.
  const team = me.is_staff || me.trust_level >= MODERATOR_TRUST_LEVEL;
  const reviewer = team || me.trust_level >= REVIEWER_TRUST_LEVEL;
  const now = new Date();
  // La plus urgente : la première échéance ; à défaut (relectures spontanées), la plus ancienne.
  const urgent =
    [...tasks].filter((task) => task.due_at).sort((a, b) => a.due_at!.localeCompare(b.due_at!))[0] ?? tasks[0];

  return (
    <>
      <h1>Relectures</h1>
      <PageIntro id="relectures">
        L&apos;auteur reste anonyme et tu ne vois pas les autres verdicts avant d&apos;avoir rendu le
        tien. Une relecture tirée au sort est à rendre sous 72 heures ; au-delà, elle est confiée à
        quelqu&apos;un d&apos;autre, sans pénalité.
      </PageIntro>
      {team && (
        <p className="mt-3 rounded-xl bg-accent-soft px-4 py-3 text-accent-text">
          Tu fais partie de l&apos;équipe : ta relecture vaut décision. Dès que tu la rends, la copie est validée ou
          à reprendre, sans attendre les autres relecteurs.
        </p>
      )}
      {(team || me.trust_level >= EXPERT_TRUST_LEVEL) && (
        <p className="mt-3">
          <Link href="/evaluations" className="underline underline-offset-4">
            Réponses aux questions de compréhension à évaluer
          </Link>
        </p>
      )}

      {tasks.length === 0 ? (
        <p className="mt-8 text-mute">
          {reviewer
            ? "Aucune relecture en cours pour toi."
            : "Les relectures sont confiées aux membres de niveau Relecteur : 50 points et 2 copies validées. Continue à résoudre des exercices pour y accéder."}
        </p>
      ) : (
        <>
          <p className="mt-8 rounded-xl border border-hairline bg-surface-soft px-4 py-3">
            <strong className="font-semibold text-ink-deep">{plural(tasks.length, "copie")} à relire</strong>
            {urgent?.due_at && (
              <span className="text-body">
                {" "}
                · {dueLabel(urgent.due_at, now) ? `la plus urgente est à rendre ${dueLabel(urgent.due_at, now)}` : "la plus urgente a dépassé son échéance"}
              </span>
            )}
          </p>
          {/* Une copie ouverte à la fois, la plus urgente : les autres se déplient au besoin. */}
          {tasks.map((task) => {
            const aiBadge = AI_USAGE_BADGES[task.ai_usage];
            const soon = task.due_at !== null && new Date(task.due_at).getTime() - now.getTime() < SOON_MS;
            return (
              <details key={task.id} open={task.id === urgent?.id} className="mt-4 rounded-xl border border-hairline">
                <summary className="flex min-h-12 flex-wrap items-center gap-x-3 gap-y-1 px-4 py-3">
                  <span className="text-sm text-mute">[{task.primary_level}]</span>
                  <span className="font-medium text-ink">
                    <MathText>{task.exercise_title}</MathText>
                  </span>
                  <span className={`text-sm sm:ml-auto ${soon ? "font-medium text-accent-text" : "text-mute"}`}>
                    {!task.due_at
                      ? "Relecture spontanée, sans échéance"
                      : dueLabel(task.due_at, now)
                        ? `À rendre ${dueLabel(task.due_at, now)}`
                        : "Échéance passée : bientôt confiée à un autre"}
                  </span>
                </summary>
                <div className="border-t border-hairline px-4 pb-4">
                  <p className="mt-3 text-sm">
                    <Link href={`/exercices/${task.exercise_id}`} className="text-mute underline underline-offset-4 hover:text-ink">
                      Page de l&apos;exercice
                    </Link>
                  </p>
                  <MathMarkdown>{task.exercise_statement}</MathMarkdown>
                  <div className="mt-4 border-l-2 border-hairline-strong bg-surface-soft px-4 py-1">
                    <p className="mt-2 flex items-center gap-3 font-bold">
                      Solution proposée
                      {aiBadge && <Tag>{aiBadge}</Tag>}
                    </p>
                    <CopyPhotoList photos={task.solution_photos} />
                    {task.solution_body && <MathMarkdown>{task.solution_body}</MathMarkdown>}
                    <ExpectedAnswer value={task.expected_answer} />
                  </div>
                  <div className="mt-4">
                    <ReviewForm reviewId={task.id} />
                  </div>
                  {/* Plagiat, IA non déclarée : le verdict ne le dit pas, un signalement si. */}
                  <div className="mt-4 flex justify-end border-t border-hairline pt-3">
                    <ReportButton target="solution" targetId={task.solution_id} canReportDuplicates={false} />
                  </div>
                </div>
              </details>
            );
          })}
        </>
      )}

      {reviewer && (
        <ProseSection title={team ? "Copies en attente de correction" : "Relire spontanément"}>
          <p>
            {team
              ? "Toutes les copies en relecture, les plus anciennes d'abord. Corrige celles que les relecteurs tardent à relire."
              : "D'autres copies attendent leurs relecteurs. Ta relecture s'ajoute aux trois relectures tirées au sort."}
          </p>
          {open.length === 0 ? (
            <p className="text-mute">Aucune pour l&apos;instant.</p>
          ) : (
            <ul className="divide-y divide-hairline border-y border-hairline">
              {open.map((item) => {
                const late = item.waiting_hours >= LATE_HOURS || item.short_staffed;
                return (
                  <li key={item.solution_id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                    <span className="min-w-0">
                      <span className="text-mute">[{item.primary_level}] </span>
                      <MathText>{item.exercise_title}</MathText>
                      <span className="block text-sm text-mute">
                        <span className={late ? "font-medium text-accent-text" : ""}>
                          en attente {waiting(item.waiting_hours)}
                          {item.short_staffed && " · relecteurs manquants"}
                        </span>{" "}
                        · {item.reviews_done} relecture{item.reviews_done > 1 ? "s" : ""} sur {item.reviews_expected}
                      </span>
                    </span>
                    <VolunteerButton solutionId={item.solution_id} label={team ? "Corriger" : "Je relis"} />
                  </li>
                );
              })}
            </ul>
          )}
        </ProseSection>
      )}
    </>
  );
}
