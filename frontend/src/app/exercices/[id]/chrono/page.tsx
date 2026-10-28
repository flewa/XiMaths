import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { FormMessage } from "@/components/Form";
import { TrainingStart } from "@/components/Training";
import { fetchExercise, fetchMe, fetchTrainingOptions } from "@/lib/api";

export const metadata: Metadata = { title: "Entraînement chronométré" };

type Props = { params: Promise<{ id: string }> };

const RULES = [
  "Entraînement non classé : documents autorisés.",
  "Deux pauses. Si tu fermes l'onglet, le chrono s'arrête et la session se reprend.",
  "Enregistrés : le temps, compté par le serveur ; ton brouillon, toutes les 10 secondes ; le nombre de sorties d'onglet et la taille des collages venus d'ailleurs. Rien de tout cela n'est pénalisé.",
  "À la fin du temps, ta dernière version est rendue automatiquement.",
  "Au rendu : réponse finale vérifiée, justification relue par trois membres, solutions débloquées.",
];

export default async function TrainingRulesPage({ params }: Props) {
  const { id } = await params;
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchExercise(id), fetchTrainingOptions(id)]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, exercise, options] = data;
  if (!me) redirect(`/connexion?suivant=/exercices/${id}/chrono`);
  if (!exercise || !options) notFound();

  return (
    <div className="max-w-[640px]">
      <Link href={`/exercices/${exercise.id}`} className="text-sm text-mute hover:text-ink">
        ← {exercise.title}
      </Link>
      <h1 className="mt-3">S&apos;entraîner en temps limité</h1>
      <ul className="mt-6 space-y-2 text-body">
        {RULES.map((rule) => (
          <li key={rule} className="flex gap-2">
            <span className="shrink-0 text-mute">[+]</span>
            <span>{rule}</span>
          </li>
        ))}
      </ul>
      <div className="mt-10 border-t border-hairline pt-6">
        {me.email_verified ? (
          <TrainingStart exerciseId={exercise.id} options={options} tiersTemps={me.tiers_temps} />
        ) : (
          <FormMessage error="Confirme d'abord ton adresse email : le lien t'a été envoyé à l'inscription." />
        )}
      </div>
    </div>
  );
}
