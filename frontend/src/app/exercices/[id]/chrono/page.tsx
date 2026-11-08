import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { FormMessage } from "@/components/Form";
import { TrainingStart } from "@/components/Training";
import { fetchExercise, fetchMe, fetchTrainingOptions } from "@/lib/api";
import { MathText } from "@/components/MathText";

export const metadata: Metadata = { title: "Entraînement chronométré", robots: { index: false } };

type Props = { params: Promise<{ id: string }> };

const RULES = [
  "Entraînement non classé : documents autorisés.",
  "Deux pauses. Si tu fermes l'onglet, le chrono s'arrête et la session se reprend.",
  "Copie écrite à la main sur papier : au départ, scanne le QR code avec ton téléphone, puis photographie tes pages (3 au plus) avant la fin du temps, avec une minute de grâce. Rien ne se tape.",
  "Enregistrés : le temps, compté par le serveur, et le nombre de sorties d'onglet. Rien de tout cela n'est pénalisé.",
  "À la fin du temps et de la minute de grâce, les photos arrivées sont rendues automatiquement.",
  "Au rendu : copie relue par trois membres, solutions débloquées.",
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
        ← <MathText>{exercise.title}</MathText>
      </Link>
      <h1 className="mt-3">S&apos;entraîner en temps limité</h1>
      <ul className="mt-6 space-y-2 text-body">
        {RULES.map((rule) => (
          <li key={rule} className="flex gap-2">
            <span aria-hidden="true" className="mt-[0.6em] size-1.5 shrink-0 rounded-full bg-stone" />
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
