import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { TrainingRoom } from "@/components/Training";
import { fetchMe, fetchTrainingSession } from "@/lib/api";

export const metadata: Metadata = { title: "Session chronométrée" };

type Props = { params: Promise<{ id: string }> };

export default async function TrainingPage({ params }: Props) {
  const { id } = await params;
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchTrainingSession(id)]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, session] = data;
  if (!me) redirect(`/connexion?suivant=/entrainement/${id}`);
  if (!session) notFound();
  return <TrainingRoom initial={session} />;
}
