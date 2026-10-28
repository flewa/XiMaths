import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";

import { ApiUnavailable } from "@/components/ExerciseMeta";
import { TrainingRoom } from "@/components/Training";
import { fetchMe, fetchTrainingSession } from "@/lib/api";

export const metadata: Metadata = { title: "Entraînement chronométré" };

type Props = { params: Promise<{ id: string }> };

export default async function TrainingPage({ params }: Props) {
  const { id } = await params;
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchTrainingSession(id)]);
  } catch (error) {
    console.error(error);
    return <ApiUnavailable />;
  }
  const [me, session] = data;
  if (!me) redirect(`/connexion?suivant=/entrainement/${id}`);
  if (!session) notFound();
  return <TrainingRoom initial={session} />;
}
