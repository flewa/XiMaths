import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { ExerciseEditor } from "@/components/AdminActions";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { MathText } from "@/components/MathText";
import { fetchLevels, fetchMe, fetchPanelExercise, fetchTopics } from "@/lib/api";
import { dateFormat } from "@/lib/labels";

export const metadata: Metadata = { title: "Modifier un exercice", robots: { index: false } };

type Props = { params: Promise<{ id: string }> };

export default async function EditExercisePage({ params }: Props) {
  const id = Number((await params).id);
  if (!Number.isInteger(id) || id <= 0) notFound();
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchPanelExercise(id), fetchLevels(), fetchTopics()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, exercise, levels, topics] = data;
  if (!me) redirect(`/connexion?suivant=/administration/exercices/${id}`);
  // Réservé aux administrateurs, et exercice inconnu : la page n'existe pas.
  if (!me.is_staff || !exercise) notFound();

  return (
    <div className="max-w-[760px]">
      <Link href="/administration?vue=exercices" className="text-sm text-mute hover:text-ink">
        ← Exercices
      </Link>
      <h1 className="mt-3">
        <MathText>{exercise.title}</MathText>
      </h1>
      <p className="mt-2 text-sm text-mute">
        {exercise.author ? `Par ${exercise.author}` : "Auteur supprimé"} · {exercise.status_label}
        {exercise.published_at && ` · publié le ${dateFormat.format(new Date(exercise.published_at))}`}
        {exercise.edited_by_team_at && ` · modifié par l'équipe le ${dateFormat.format(new Date(exercise.edited_by_team_at))}`}
        {exercise.status === "published" && (
          <>
            {" · "}
            <Link href={`/exercices/${exercise.id}`} className="underline underline-offset-4 hover:text-ink">
              Voir la page
            </Link>
          </>
        )}
      </p>
      <p className="mt-3 text-sm text-body">
        {exercise.author && exercise.author !== me.username
          ? "Son auteur est prévenu de la modification, avec le motif. "
          : ""}
        {exercise.editorial
          ? "Exercice de la rédaction : une fois modifié ici, l'import des mises à jour ne touche plus à son titre ni à ses chapitres."
          : ""}
      </p>
      <ExerciseEditor initial={exercise} levels={levels} topics={topics} />
    </div>
  );
}
